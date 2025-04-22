import os
import csv
import sys
import traceback
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
from marker_pdf.converters.pdf import PdfConverter  # 修改: 替换原来的导入语句
from functools import wraps
from typing import Callable, Any
from time import sleep

# Load environment variables
load_dotenv()

def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            delay = initial_delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "rate limit" in str(e).lower() or "quota exceeded" in str(e).lower():
                        retries += 1
                        if retries == max_retries:
                            raise
                        wait_time = delay * (2 ** (retries - 1))  # Exponential backoff
                        print(f"\rRate limit hit, waiting {wait_time:.1f} seconds before retry {retries}/{max_retries}...")
                        sleep(wait_time)
                    else:
                        raise
            return None
        return wrapper
    return decorator

def convert_files(input_dir, report_path):
    # Get Gemini API key from environment
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    # Initialize Marker with Gemini LLM and add retry decorator
    marker = PdfConverter(use_llm=True, strip_existing_ocr=True)  # 修改: 使用 PdfConverter 并添加 strip_existing_ocr 参数
    marker.convert_file = retry_with_backoff(max_retries=5, initial_delay=4.0)(marker.convert_file)
    report = [["Timestamp", "File Path", "Status", "Error"]]
    
    total_files = 0
    processed_files = 0
    
    for root, dirs, files in os.walk(input_dir):
        # Filter hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            total_files += 1
            # Filter hidden files
            if file.startswith('.'):
                print(f"Skipping hidden file: {file}")
                continue
                
            file_path = os.path.normpath(os.path.join(root, file))
            
            try:
                # Build output path
                output_filename = f"{file}.md"
                output_path = os.path.join(root, output_filename)
                
                print(f"Processing: {file_path}")
                print(f"Output path: {output_path}")
                
                # Set conversion start time and progress flags
                start_time = time.time()
                conversion_done = False
                progress_shown = False
                
                # Create progress display thread
                def show_progress():
                    dots = 0
                    while not conversion_done:
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 30 and not progress_shown:
                            print(f"\rConverting{'.' * dots}", end="")
                            dots = (dots + 1) % 4
                            time.sleep(1)
                
                progress_thread = threading.Thread(target=show_progress)
                progress_thread.daemon = True
                progress_thread.start()
                
                try:
                    # Execute conversion
                    result = marker.convert_file(file_path)
                    
                    # Export as Markdown
                    markdown_content = result.markdown
                finally:
                    # Mark conversion as complete
                    conversion_done = True
                    progress_thread.join(timeout=0.1)
                    
                # Calculate and display conversion time
                conversion_time = time.time() - start_time
                if conversion_time > 30:
                    print(f"\rConversion complete, time taken: {conversion_time:.2f} seconds")
                    progress_shown = True
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                processed_files += 1
                report.append([
                    datetime.now().isoformat(), 
                    file_path, 
                    "Success", 
                    ""
                ])
                print(f"Successfully converted: {file}")
                
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                report.append([
                    datetime.now().isoformat(), 
                    file_path, 
                    "Failed", 
                    error_msg
                ])
                print(f"Conversion failed: {file}")
                print(f"Error details: {error_msg}")
    
    # Generate summary report
    summary = [
        "\n==== Conversion Statistics ====",
        f"Total files: {total_files}",
        f"Processed files: {processed_files}",
        f"Skipped files: {total_files - processed_files}",
        f"Report file: {report_path}"
    ]
    print('\n'.join(summary))
    
    with open(report_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(report)

if __name__ == "__main__":
    try:
        # Set input directory to input folder under current directory
        input_dir = os.path.normpath(os.path.join(os.getcwd(), "input"))
        report_path = os.path.join(input_dir, "conversion_report.csv")
        
        print(f"Verifying path: {input_dir}")
        
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}\nPlease create an input folder and place files to convert in it.")
        if not os.path.isdir(input_dir):
            raise NotADirectoryError(f"Path is not a directory: {input_dir}")
            
        print("=== Path verification passed ===")
        print(f"Input directory: {input_dir}")
        
        convert_files(
            input_dir,
            report_path
        )
        
    except Exception as e:
        print(f"\nError type: {type(e).__name__}", file=sys.stderr)
        print(f"Error details: {str(e)}", file=sys.stderr)
        print(f"Current working directory: {os.getcwd()}", file=sys.stderr)
        sys.exit(1)
