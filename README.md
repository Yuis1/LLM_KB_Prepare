## 项目介绍
目的：为了提升知识库质量，给大模型喂更干净的语料。  
本项目整理了大模型知识库清洗整理提取的工作流程和实践，测试了各个开源工具，并编写对应脚本。  

```mermaid
graph LR;
    A[第1步：文档准备] --> B[第2步：文档提取];
    B --> C[第3步：人工整理];
    C --> D[第4步：知识库组织];
```

## 第1步：文档准备
目录：01_doc_prepare

### 文件去重 
- 可以使用轻量的工具 [DupeGuru](https://dupeguru.voltaicideas.net/)，跨平台，带GUI界面

### 纯文本编码转换
[convert_txt_encoding.py](01_doc_prepare/convert_txt_encoding.py)

### Office格式升级  
[office_format_update.py](01_doc_prepare/office_format_update.py)
将input目录及子目录下，所有doc、xls、ppt为docx、xlsx、pptx，输出路径同原文件。
确认转换成功后，删除原文件。在intput目录下，输出一份转换报告。

需要安装 [LibreOffice](https://www.libreoffice.org/) ，MacOS下：`brew install libreoffice` 

**原理：**以无头模式（在没有图形用户界面的情况下运行）启动 LibreOffice，对输入文件进行转换。

**其它替代方法：**

1. 使用宏文件 [texdoc2docx.dotm](01_doc_prepare/doc2docx.dotm) 
2. 使用Office、WPS 等软件，手工将doc、xls、ppt转为docx、xlsx、pptx

## 第2步：文档提取
目录：02_doc_extract

### 最终结论

- 入门：8K以内的小型文档，可以通过大模型对话进行提取，效果很好。
- 初级：Office文件，只提取文字（支持排版布局）和二维表格，可采用 Markitdown 
- 中级：PDF、Word、PPT文件，需要提取公式、复杂表格（含嵌入图片格式的文字和表格），并且保留其中的插图，可采用 MinerU
- 高级：需要在MinerU基础上进一步提升准确度，必须调用视觉大模型，考虑用 olmOCR、Marker (使用选项`--use_llm`) 

### 文档提取的工具测评
- [6大RAG知识库PDF文档处理神器对比](https://mp.weixin.qq.com/s/kJPURFFOeFZgqRz16RvoRg)
- [PDF转换工具Marker、MinerU、Markitdown对比分析](https://www.cnblogs.com/JCpeng/p/18623713)
- [MarkItDown微软开源文档转换工具--实测效果](https://zhuanlan.zhihu.com/p/23189172338)
- [文档解析神器 MinerU](https://mp.weixin.qq.com/s/PYZFqAcDtrd6Z-tvhOEYqg)

### 通过大模型对话提取
使用ChatGPT、Kimi、Gemini等对话，上传附件并要求提取。
只适用于8K以内的小型文档，要小心对话模型可能在提取时偷工减料。  

Prompt：
```Prompt
将附件文档整理成markdown格式给我（包括公式、表格），去除页眉和页脚。
所有的公式用latex表示 请使用  $行中公式$  和  $$单行公式$$ 的格式来写，公式不用添加```的代码块符号。
完整提取，不要省略任何内容，如果上下文窗口受限可在多轮对话中输出。
```

也可以调用大模型API，对每页进行分批提取，但费用比较高。  
这种方法工程化后就是 olmOCR、Marker (使用选项`--use_llm`) ，按需调用大模型更省Token。

### MarkitDown
特性：

- 转换速度飞快
- 多格式支持：自动处理 PDF、Office 文档、图像、音频等 12 种格式
- 基于 pdfminer.six 和 mammoth 实现高精度文档解析
- 通过 pytesseract 支持图像 OCR 文字识别
- 使用 openpyxl 保留 Excel 表格结构
- 双栏pdf可以解析。
- pdf中图片无法解析。
- pdf中表格解析效果差，没有形成Markdown表格。
- 对复杂表格、公式，提取效果不佳。图片识别依赖视觉大模型，贵。

安装：`pip install markitdown`

convert_md_to_ori.py
将input目录及子目录下，所有支持的文件转为markdown格式，输出到原目录下，输出的相对路径同原文件。
确认转换成功后，不删除原文件。
在input目录下，输出一份转换报告。

convert_md_to_output.py
将input目录及子目录下，所有支持的文件转为markdown格式，输出到output目录下，输出的相对路径同原文件。
确认转换成功后，不删除原文件。
在output目录下，输出一份转换报告。


### Docling
缺陷：

- 转换速度很慢
- 无法转换pdf内的图片中的表格。
- pdf中二维表格转换效果不佳，提取不全，错行。

测评结论：不可用

安装：`pip install docling`

### [MinerU](https://github.com/opendatalab/MinerU)
一站式开源高质量数据提取工具，将PDF转换成Markdown和JSON格式。

特性：

- 表格的提取统一用html标签表示，人工很难参与编辑

缺陷：

- 带视觉样式的图片格式的表格无法提取，会单独保存为图片
- 对PDF的文字提取，少数情况下会漏掉文字。
- 默认ocr选中文，对英文的ocr将丢失空格符，英文单词都连在一起；如果选英文，中文ocr将丢失。


安装：对需要硬件要求高。如果对文档的保密性不敏感，可以使用 [桌面客户端](https://mineru.net/client)（传到 上海人工智能实验室 服务器上解析提取），无硬件要求。

使用：  
[可选]语义化重命名：在桌面客户端批量提取完成后，将 [rename_MinerU_files.sh](02_doc_extract/MinerU/rename_MinerU_files.sh) 放入解析结果的文件夹。

### [Marker](https://github.com/VikParuchuri/marker)
Marker 是一个深度学习模型的流水线：

1. 提取文本，必要时进行 OCR（使用启发式方法或 Surya 模型）
2. 检测页面布局并确定阅读顺序（使用 Surya 模型）
3. 清理和格式化每个文本块（使用启发式方法、Texify 或 Surya 模型）
4. 可选地使用大语言模型 (LLM) 提高质量
5. 合并文本块并对完整文本进行后处理

它仅在必要时使用模型，这提高了速度和准确性。

PDF 是一种复杂的格式，因此 Marker 并不能总是完美工作。以下是一些已知的限制：

- 非常复杂的布局，包含嵌套表格和表单，可能无法正确处理
- 表单可能无法很好地渲染
- 注意：使用 `--use_llm` 标志可以解决大多数这些问题。

**安装：**  
[Marker：Windows环境折腾PDF转Markdown](https://forum-zh.obsidian.md/t/topic/28621)   
各种依赖比较复杂，推荐直接跑 Docker镜像。   
[Dockerfile](02_doc_extract/marker/Dockerfile)

### [olmOCR](https://olmocr.allenai.org/)
特性：

- 可以提取带视觉样式的图片格式的表格
- 表格的提取统一用html标签表示，人工很难参与编辑

## 第3步：人工整理

- 删除低密度、劣质、误导的信息，如广告、废话、目录大纲、致谢、版权声明等不含知识的信息，删除大部分只有标题或大纲的文档。  
- 删除隐私信息，进行匿名化处理。
- [可选]删除为了美观而设置的，没有实际知识的配图、插图。
- 含有实际信息的图片可保留，但目前不会提取。
- [可选]做好分段：一般按 空行 进行文档切片。所以希望一并输入到模型中的段落，中间不要有 空行；希望分开给到模型的，可以设置2个空行。


## 第4步：知识库组织
### 文本型知识库
#### 需要准备的文本知识内容
- 大模型已有的是公域知识，知识库需要重点准备行业深度知识、私域知识。  
- 大模型对公域知识大块文本的精确默写能力差，在需要精确默写的场景（比如引用法律、规范条款），需要准备这些公域知识的原文。

#### 文本型知识库的组织方式
根据内容检索的场景，综合考虑文献的结构和长度（分片及检索策略不同），在文件系统中组织成以下分类规则。  
对不支持多级分类的知识库，可按 一级目录-二级目录-三级目录 的方式进行知识库命名。

### 一级目录：项目名

### 二级目录：按文档类型分类
这一层级的分类主要考虑到文档的结构和长度，制定不同的分片及检索策略。

例如：  

- 01书籍
- 02论文
- 03测评
- 04案例
- 05课件
- 06QA  

### 三级目录：按主题场景分类（文献较少的可不分类） 
这一层级的分类主要是为了缩小查询范围，提升查询精准度。  
同时结合检索场景，细化分配和检索策略。

例如：

- 教育
- 婚恋
- ...
- 其它  

### 四级目录：按整理录入进度分类

- 01文档准备：初始上传的文件，需要进行 文档准备、文档提取 工作后，再移入 02人工整理 文件夹。
- 02人工整理：
    - 参照 第3步：人工整理 步骤
    - 保留原文件(同.md文件所在目录)。
  	- 将人工整理后的 .md 文件上传到知识库，再将目录整体移入 03已入库。
- 03已入库：
	- 上传到知识库。知识库推荐的组织方式：一级目录_二级目录_三级目录 为知识库名称。



