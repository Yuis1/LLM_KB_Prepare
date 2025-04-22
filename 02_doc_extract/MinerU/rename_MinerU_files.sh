#!/bin/bash
# 脚本介绍：用于重命名 MinerU 桌面客户端转换后的文档名称，让其更语义化，以便Dify等知识库使用。
# 功能： 
# 当前目录下，所有子目录名称如果有带随机字符串，去除。例如目录名 示例文件.pdf-c45dba1d-8171-420a-88e1-0977dcf096bd  改为 示例文件.pdf
# 将当前子目录下，3类文件名恢复为带语义的文件名（也就是修改后的目录名的 . 之前的部分），例如 示例文件.pdf 目录下，full.md 改为 示例文件.md ，57399336-c9eb-4678-9b18-5cb0ebe92bf0_content_list.json 改为 示例文件.json ，57399336-c9eb-4678-9b18-5cb0ebe92bf0_origin.pdf 改为  示例文件.pdf 。其它文件名不变。


# Exit on error, undefined variables, and errors in pipes
set -euo pipefail

# Log function for better visibility
log() {
  echo "[$(date "+%Y-%m-%d %H:%M:%S")] $1"
}

log "Starting the renaming process..."

# Process each directory that matches the pattern NAME.pdf-RANDOM_STRING
find . -maxdepth 1 -type d -name "*.pdf-*" | while IFS= read -r dir; do
  # Extract the part before .pdf-
  dir_basename=$(basename "$dir")
  new_dir_name="${dir_basename%%.pdf-*}.pdf"
  
  log "Renaming directory: $dir_basename -> $new_dir_name"
  
  # Only proceed if target directory doesn't already exist
  if [ ! -d "./$new_dir_name" ]; then
    # Rename the directory
    mv "$dir" "./$new_dir_name"
    
    # Get the base name (without .pdf extension) for file renaming
    base_name="${new_dir_name%%.pdf}"
    
    # Enter the renamed directory and process files
    cd "./$new_dir_name" || { log "Failed to enter directory $new_dir_name"; exit 1; }
    
    # Rename full.md to base_name.md
    if [ -f "full.md" ]; then
      log "  Renaming: full.md -> $base_name.md"
      mv "full.md" "$base_name.md"
    else
      log "  Warning: full.md not found in $new_dir_name"
    fi
    
    # Find and rename *_content_list.json to base_name.json
    content_list_file=$(find . -maxdepth 1 -type f -name "*_content_list.json" | head -n 1)
    if [ -n "$content_list_file" ]; then
      content_list_basename=$(basename "$content_list_file")
      log "  Renaming: $content_list_basename -> $base_name.json"
      mv "$content_list_file" "./$base_name.json"
    else
      log "  Warning: No *_content_list.json found in $new_dir_name"
    fi
    
    # Find and rename *_origin.pdf to base_name.pdf
    origin_pdf_file=$(find . -maxdepth 1 -type f -name "*_origin.pdf" | head -n 1)
    if [ -n "$origin_pdf_file" ]; then
      origin_pdf_basename=$(basename "$origin_pdf_file")
      log "  Renaming: $origin_pdf_basename -> $base_name.pdf"
      mv "$origin_pdf_file" "./$base_name.pdf"
    else
      log "  Warning: No *_origin.pdf found in $new_dir_name"
    fi
    
    # Return to the parent directory
    cd ..
  else
    log "  Warning: Target directory $new_dir_name already exists, skipping."
  fi
done

log "Renaming process completed successfully!"

# Make the script display a summary
total_dirs=$(find . -maxdepth 1 -type d -name "*.pdf" | wc -l)
log "Total directories processed: $total_dirs"
log "Check for any warnings in the output above."

