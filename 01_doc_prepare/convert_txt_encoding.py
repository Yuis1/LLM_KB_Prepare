# 将MacOS下乱码的txt文件进行转码

import os
import chardet

def convert_encoding(source_dir, target_dir):
    # 遍历所有子目录和文件
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.txt'):
                src_path = os.path.join(root, file)
                
                # 构建目标路径
                relative_path = os.path.relpath(root, source_dir)
                dest_folder = os.path.join(target_dir, relative_path)
                dest_path = os.path.join(dest_folder, file)
                
                # 创建目标目录
                os.makedirs(dest_folder, exist_ok=True)

                # 读取二进制内容
                with open(src_path, 'rb') as f:
                    raw_data = f.read()

                # 自动检测编码
                detected = chardet.detect(raw_data)
                original_encoding = detected.get('encoding', None)
                confidence = detected.get('confidence', 0)

                # 准备尝试的编码列表（优先级：检测结果 → 常见中文编码 → 其他）
                encodings_to_try = []
                if original_encoding and confidence > 0.5:
                    encodings_to_try.append(original_encoding)
                encodings_to_try += ['GB18030', 'GBK', 'BIG5', 'utf-8', 'latin1']

                # 尝试解码
                decoded = None
                for enc in encodings_to_try:
                    try:
                        decoded = raw_data.decode(enc)
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue

                # 写入转换后的文件
                if decoded:
                    with open(dest_path, 'w', encoding='utf-8') as f:
                        f.write(decoded)
                    print(f"成功转换: {src_path} → {dest_path}")
                else:
                    print(f"无法解码: {src_path}（尝试过的编码：{encodings_to_try}）")

if __name__ == '__main__':
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, 'output')
    
    # 删除已存在的 output 目录
    if os.path.exists(output_dir):
        print("检测到已存在的 output 目录，正在清理...")
        import shutil
        shutil.rmtree(output_dir)
    
    print("开始转换...")
    convert_encoding(current_dir, output_dir)
    print("\n转换完成！输出目录：", output_dir)
