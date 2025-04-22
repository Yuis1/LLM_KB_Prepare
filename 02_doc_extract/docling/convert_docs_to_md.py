import os
import csv
import sys
import traceback
import ssl
import time
import threading
from datetime import datetime
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat

# Add SSL certificate verification bypass
ssl._create_default_https_context = ssl._create_unverified_context

def convert_files(input_dir, report_path):
    # 支持的文件格式
    supported_formats = [
        InputFormat.PDF,
        InputFormat.DOCX,
        InputFormat.PPTX,
        InputFormat.HTML,
        InputFormat.IMAGE
    ]
    
    # 初始化转换器
    doc_converter = DocumentConverter(allowed_formats=supported_formats)
    report = [["Timestamp", "File Path", "Status", "Error"]]
    
    total_files = 0
    processed_files = 0
    
    for root, dirs, files in os.walk(input_dir):
        # 过滤隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            total_files += 1
            # 过滤隐藏文件
            if file.startswith('.'):
                print(f"跳过隐藏文件: {file}")
                continue
                
            file_path = os.path.normpath(os.path.join(root, file))
            
            try:
                # 构建输出路径
                output_filename = f"{file}.md"
                output_path = os.path.join(root, output_filename)
                
                print(f"正在处理: {file_path}")
                print(f"输出路径: {output_path}")
                
                # 设置转换开始时间和进度标志
                start_time = time.time()
                conversion_done = False
                progress_shown = False
                
                # 创建进度显示线程
                def show_progress():
                    dots = 0
                    while not conversion_done:
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 30 and not progress_shown:
                            # 超过30秒，显示进度
                            print(f"\r转换进行中{'.' * dots}", end="")
                            dots = (dots + 1) % 4
                            time.sleep(1)
                
                progress_thread = threading.Thread(target=show_progress)
                progress_thread.daemon = True
                progress_thread.start()
                
                try:
                    # 执行转换
                    conv_result = doc_converter.convert(file_path)
                    
                    # 导出为 Markdown
                    markdown_content = conv_result.document.export_to_markdown()
                finally:
                    # 标记转换完成
                    conversion_done = True
                    progress_thread.join(timeout=0.1)
                    
                # 计算并显示转换时间
                conversion_time = time.time() - start_time
                if conversion_time > 30:
                    print(f"\r转换完成，耗时: {conversion_time:.2f}秒")
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
                print(f"成功转换: {file}")
                
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                report.append([
                    datetime.now().isoformat(), 
                    file_path, 
                    "Failed", 
                    error_msg
                ])
                print(f"转换失败: {file}")
                print(f"错误详情: {error_msg}")
    
    # 生成总结报告
    summary = [
        "\n==== 转换统计 ====",
        f"总文件数: {total_files}",
        f"已处理文件: {processed_files}",
        f"跳过文件: {total_files - processed_files}",
        f"报告文件: {report_path}"
    ]
    print('\n'.join(summary))
    
    with open(report_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(report)

if __name__ == "__main__":
    try:
        # 设置输入目录为当前目录下的 input 文件夹
        input_dir = os.path.normpath(os.path.join(os.getcwd(), "input"))
        report_path = os.path.join(input_dir, "conversion_report.csv")
        
        print(f"正在验证路径: {input_dir}")
        
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"输入目录不存在: {input_dir}\n请在当前目录下创建 input 文件夹并放入要转换的文件。")
        if not os.path.isdir(input_dir):
            raise NotADirectoryError(f"路径不是目录: {input_dir}")
            
        print("=== 路径验证通过 ===")
        print(f"输入目录: {input_dir}")
        
        convert_files(
            input_dir,
            report_path
        )
        
    except Exception as e:
        print(f"\n错误类型: {type(e).__name__}", file=sys.stderr)
        print(f"错误详情: {str(e)}", file=sys.stderr)
        print(f"当前工作目录: {os.getcwd()}", file=sys.stderr)
        sys.exit(1)