## 项目介绍
采用各种脚本，为LLM知识库清洗整理文件，提升知识库质量。  
用到的开源组件：[markitdown](https://github.com/microsoft/markitdown)   
后续准备对比使用 [docling](https://github.com/DS4SD/docling)

## 准备工作 
- 文件去重，可以使用 https://dupeguru.voltaicideas.net/
- 为了将.doc文档转为.docx，需要安装 [LibreOffice](https://www.libreoffice.org/) 。MacOS下：brew install libreoffice
- 如果已经安装了word且不想安装LibreOffice，可以使用宏文件 doc2docx.dotm
- 为了转为.md文档，需要安装markitdown：pip install markitdown

## 脚本功能
### office_format_update.py  
将input目录及子目录下，所有doc、xls、ppt为docx、xlsx、pptx，输出路径同原文件。
确认转换成功后，删除原文件。
在intput目录下，输出一份转换报告。

主要原理：
soffice --headless --convert-to docx test.doc
soffice --headless --convert-to pptx test.ppt
soffice --headless --convert-to xlsx test.xls

soffice --headless 是 LibreOffice 和 OpenOffice 中的一个命令行选项，用于以无头模式（headless mode）启动 LibreOffice 或 OpenOffice。无头模式意味着在没有图形用户界面（GUI）的情况下运行，通常用于服务器环境或需要自动化任务的场景。

### convert_md_to_ori.py
将input目录及子目录下，所有支持的文件转为markdown格式，输出到原目录下，输出的相对路径同原文件。
确认转换成功后，不删除原文件。
在input目录下，输出一份转换报告。

### convert_md_to_output.py
将input目录及子目录下，所有支持的文件转为markdown格式，输出到output目录下，输出的相对路径同原文件。
确认转换成功后，不删除原文件。
在output目录下，输出一份转换报告。

## 知识库的组织和准备工作
根据内容检索的场景，综合考虑文献的结构和长度（分片及检索策略不同），形成以下分类规则。

### 第一层目录：按文献类型分类
例如：  
- 01书籍
- 02论文
- 03测评
- 04案例
- 05课件及QA  

### 第二层目录：按领域分类（文献较少的可不分类）
- 教育
- 婚恋
- ...
- 其它  

### 第三层目录：按整理录入进度分类
- 01待整理：初始上传的文件，整理编辑后移入 02已整理 。
- 02已整理：
	- 删除低密度、劣质、误导的信息，如广告、脚本、废话、目录大纲，删除大部分只有标题或大纲的文档。  
	- 删除隐私信息，进行匿名化处理。
	- [可选]删除为了美观而设置的，没有实际信息的配图、插图。
	- 含有实际信息的图片可保留，但目前不会提取。
	- 表格可保留，但是图片中的表格需要重新制作成文字表格。尽量是简单的二维表。
	- [可选]做好分段：一般按 空行 进行文档切片。所以希望一并输入到模型中的段落，中间不要有 空行；希望分开给到模型的，可以设置2个空行。
	- pdf文件，最好对照建一个.docx文件，再编辑。
	- 使用 office_format_update.py 将 .doc .xls .ppt 保存为 .docx .xlsx .pptx 格式，否则Dify不支持。
- 03已入库：
	- [可选]使用 convert_md_to_ori.py 将文件批量转为 .md 格式。
	- [暂不支持]转换音视频文件为.md
	- 上传到知识库。知识库推荐的组织方式：一级分类名+二级分类名 为一个目录。
	- 将转换后 .md 文件，连同原文件(同.md文件所在目录)，移入 03已入库。

## 其它补充说明
### MarkitDown
- 多格式支持：自动处理 PDF、Office 文档、图像、音频等 12 种格式
- 基于 pdfminer.six 和 mammoth 实现高精度文档解析
- 通过 pytesseract 支持图像 OCR 文字识别
- 使用 openpyxl 保留 Excel 表格结构

注意事项：
- 需要 Python ≥3.8 环境
- 音频转换需额外安装 SpeechRecognition 库
- 处理加密文档时会直接报错