import os
import csv
import subprocess
import traceback
from datetime import datetime

def convert_files(input_dir, report_path):
    supported_ext = ('.doc', '.xls', '.ppt')
    conversion_map = {
        '.doc': '.docx',
        '.xls': '.xlsx',
        '.ppt': '.pptx'
    }
    
    report = [["Timestamp", "File Path", "New File Path", "Status", "Error"]]
    
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
                
            if file == "conversion_report.csv" and os.path.dirname(os.path.join(root, file)) == os.path.join(input_dir, "output"):
                print(f"跳过转换报告文件: {file}")
                continue
                
            file_path = os.path.normpath(os.path.join(root, file))
            rel_path = os.path.relpath(file_path, input_dir)
            
            # 正确的扩展名检查
            ext = os.path.splitext(file)[1].lower()
            if ext not in supported_ext:
                print(f"跳过不支持的文件类型: {file} [{ext}]")
                continue
                
            try:
                # 构建输出文件路径
                new_ext = conversion_map[ext]
                base_name = os.path.splitext(file)[0]
                new_file_name = f"{base_name}{ext}{new_ext}"
                new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
                
                print(f"正在处理: {file_path}")
                print(f"输出路径: {new_file_path}")
                
                # 执行转换
                subprocess.run(['soffice', '--headless', '--convert-to', new_ext[1:], '--outdir', os.path.dirname(new_file_path), file_path], check=True)
                
                # 检查转换结果
                if not os.path.exists(new_file_path):
                    raise FileNotFoundError(f"转换后文件未找到: {new_file_path}")
                    
                processed_files += 1
                report.append([
                    datetime.now().isoformat(), 
                    file_path, 
                    new_file_path, 
                    "Success", 
                    ""
                ])
                print(f"成功转换: {file}")
                
                # 删除原文件
                os.remove(file_path)
                print(f"已删除原文件: {file}")
                
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                report.append([
                    datetime.now().isoformat(), 
                    file_path, 
                    "", 
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