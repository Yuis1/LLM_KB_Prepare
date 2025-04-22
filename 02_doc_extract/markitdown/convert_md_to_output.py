import os
import csv
import traceback
from datetime import datetime
from markitdown import MarkItDown
from urllib.parse import unquote

def convert_files(input_dir, output_dir, report_path):
    supported_ext = ('.pdf', '.docx', '.pptx', '.xlsx', 
                    '.jpg', '.jpeg', '.png', '.mp3', 
                    '.html', '.csv', '.json', '.xml')
    
    md = MarkItDown()
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
            rel_path = os.path.relpath(file_path, input_dir)
            
            # 正确的扩展名检查
            ext = os.path.splitext(file)[1].lower()
            if ext not in supported_ext:
                print(f"跳过不支持的文件类型: {file} [{ext}]")
                continue
                
            try:
                # 构建输出路径
                output_subdir = os.path.join(output_dir, os.path.dirname(rel_path))
                os.makedirs(output_subdir, exist_ok=True)
                output_filename = f"{os.path.splitext(file)[0]}{ext}.md"  # 修改: 加入原始扩展名
                output_path = os.path.join(output_subdir, output_filename)
                
                print(f"正在处理: {file_path}")
                print(f"输出路径: {output_path}")
                
                # 执行转换
                result = md.convert(file_path)
                
                # 检查转换结果有效性
                if not hasattr(result, 'text_content'):
                    raise AttributeError("转换结果缺少 text_content 属性")
                    
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result.text_content)
                
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
        f"输出目录: {output_dir}",
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
        output_dir = os.path.normpath(os.path.join(os.getcwd(), "output"))
        report_path = os.path.join(output_dir, "conversion_report.csv")
        
        print(f"正在验证路径: {input_dir}")
        
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"输入目录不存在: {input_dir}\n请在当前目录下创建 input 文件夹并放入要转换的文件。")
        if not os.path.isdir(input_dir):
            raise NotADirectoryError(f"路径不是目录: {input_dir}")
            
        # 创建输出目录并检查权限
        os.makedirs(output_dir, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"输出目录不可写: {output_dir}")
            
        print("=== 路径验证通过 ===")
        print(f"输入目录: {input_dir}")
        print(f"输出目录: {output_dir}")
        
        convert_files(
            input_dir,
            output_dir,
            report_path
        )
        
    except Exception as e:
        print(f"\n错误类型: {type(e).__name__}", file=sys.stderr)
        print(f"错误详情: {str(e)}", file=sys.stderr)
        print(f"当前工作目录: {os.getcwd()}", file=sys.stderr)
        sys.exit(1)