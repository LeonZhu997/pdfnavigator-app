# PDFNavigator

一款 PDF 书签自动添加工具，支持从目录页提取书签或基于字体大小自动检测章节标题。

## 功能特点

- 📖 **目录页自动识别** - 智能检测 PDF 目录页位置
- 🔤 **字体检测章节** - 无目录页时，根据字体大小自动识别章节标题
- 🌳 **多级书签结构** - 支持多级嵌套书签（章/节/小节等）
- ✏️ **可视化编辑** - 预览、编辑、删除、调整书签层级
- 🎨 **现代界面** - 拖拽上传、实时进度显示、友好交互
- 📁 **批量处理** - 支持大文件处理，显示页数和文件大小

## 安装

### 方式一：直接使用 exe 文件（推荐）

无需安装 Python，直接运行打包好的可执行文件：

```
dist/pdfnavigator.exe
```

### 方式二：源码运行

1. 创建 Python 环境：
```bash
conda create -n pdfenv python=3.12
conda activate pdfenv
```

2. 安装依赖：
```bash
pip install PySide6 PyMuPDF pdfplumber
```

3. 运行程序：
```bash
python main.py
```

## 使用方法

### 操作流程

```
① 选择PDF → ② 提取书签 → ③ 编辑确认 → ④ 保存导出
```

1. **选择 PDF 文件** - 拖拽文件到窗口或点击"浏览选择文件"
2. **提取书签** - 点击"开始提取书签"，自动检测目录页或字体章节
3. **编辑确认** - 在编辑器中查看、修改书签内容和层级
4. **保存导出** - 保存为新的 PDF 文件（原文件名加 `_bookmarked`）

### 书签提取模式

| 模式 | 说明 |
|------|------|
| 目录页提取 | 检测包含"目录"、"目次"等关键词的页面，解析目录结构 |
| 字体检测 | 扫描全文档，根据字体大小识别章节标题（大字体=章，中等字体=节） |

### 编辑器功能

- ➕ 添加新书签
- ➖ 删除选中书签
- ⬆ 升级层级（变为父级）
- ⬇ 降级层级（变为子级）
- ↺ 恢复原始提取结果
- 双击编辑标题和页码

## 项目结构

```
pdfnavigator-app/
├── pdfnavigator/           # 主包
│   ├── core/               # 核心功能
│   │   ├── toc_detector.py     # 目录页检测
│   │   ├── toc_parser.py       # 目录解析
│   │   ├── font_chapter_detector.py  # 字体章节检测
│   │   ├── bookmark_writer.py  # 书签写入 PDF
│   │   └── pdf_handler.py      # PDF 基础操作
│   ├── ui/                 # 用户界面
│   │   ├── main_window.py      # 主窗口
│   │   ├── editor_window.py    # 编辑器窗口
│   │   ├── widgets.py          # 自定义控件
│   │   └── styles.py           # 样式定义
│   ├── utils/              # 工具函数
│   │   ├── config.py           # 配置常量
│   │   └── helpers.py          # 辅助函数
│   └── assets/             # 资源文件
│       ├── icon.png            # 应用图标（源）
│       └ icon.ico              # Windows exe 图标
│   └── resources/          # 其他资源
├── tests/                  # 测试文件
├── main.py                 # 程序入口
├── pdfnavigator.spec       # PyInstaller 配置
├── pyproject.toml          # 项目配置
└── README.md               # 说明文档
```

## 技术栈

| 技术 | 用途 |
|------|------|
| PySide6 | Qt GUI 框架 |
| PyMuPDF (fitz) | PDF 读取、书签写入 |
| pdfplumber | 文本提取（带布局信息） |
| PyInstaller | 打包为 exe 可执行文件 |

## 开发说明

### 运行测试

```bash
pytest tests/
```

### 打包 exe

```bash
conda activate pdfenv
pyinstaller --onefile --windowed --name "pdfnavigator" --icon=pdfnavigator/assets/icon.ico --add-data "pdfnavigator/assets;assets" main.py
```

打包后文件位于 `dist/pdfnavigator.exe`

## 常见问题

**Q: 目录页检测失败怎么办？**
A: 程序会自动提示使用字体检测模式，扫描全文档识别章节标题。

**Q: exe 文件较大（100MB）？**
A: 包含了完整的 Qt 框架和 PDF 处理库，首次运行会稍慢（需解压资源）。

**Q: 杀毒软件报警？**
A: PyInstaller 打包的程序常被误报，属于正常现象，添加信任即可。

## 许可证

MIT License

## 版本历史

- v0.1.0 - 初始版本，支持目录页提取和字体检测两种模式