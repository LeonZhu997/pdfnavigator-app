# PDFNavigator 快速启动指南

## 项目简介

PDFNavigator 是一个 GUI 桌面应用，可自动从 PDF 目录页提取书签信息，支持预览编辑，生成带多级嵌套书签的新 PDF。

## 环境要求

- Python 3.11+
- Windows 10/11

## 快速启动

### 1. 激活虚拟环境

**Windows CMD:**
```cmd
cd D:\LeonCode\Project-d\forceleap\PDFNavigator_app
.venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
cd D:\LeonCode\Project-d\forceleap\PDFNavigator_app
.venv\Scripts\Activate.ps1
```

**Git Bash:**
```bash
cd D:/LeonCode/Project-d/forceleap/PDFNavigator_app
source .venv/Scripts/activate
```

### 2. 运行应用

```bash
python main.py
```

## 使用流程

1. **选择 PDF 文件** - 拖拽文件到窗口或点击"选择文件"按钮
2. **自动检测目录页** - 应用会扫描前 20 页寻找目录页（关键词：目录、Contents 等）
3. **解析书签** - 从目录页提取标题、页码，并根据编号推断层级（1.1 → 第2级，1.1.1 → 第3级）
4. **编辑书签** - 在编辑器中添加、删除、修改书签
5. **保存 PDF** - 导出带书签的新 PDF 文件

## 运行测试

```bash
python -m pytest tests/ -v
```

## 项目结构

```
PDFNavigator_app/
├── .venv/              # 虚拟环境（首次运行需创建）
├── PDFNavigator/       # 源代码
│   ├── ui/             # 界面模块
│   │   ├── widgets.py
│   │   ├── main_window.py
│   │   └── editor_window.py
│   ├── core/           # 核心功能
│   │   ├── pdf_handler.py
│   │   ├── toc_detector.py
│   │   ├── toc_parser.py
│   │   └── bookmark_writer.py
│   └── utils/          # 工具模块
│       ├── config.py
│       └── helpers.py
├── tests/              # 测试文件
├── main.py             # 应用入口
├── pyproject.toml      # 项目配置
└── STARTUP.md          # 本文档
```

## 依赖说明

| 包名 | 用途 |
|------|------|
| PySide6 | Qt GUI 框架 |
| PyMuPDF (fitz) | PDF 读写操作 |
| pdfplumber | PDF 文本提取（保留布局） |
| pytest | 测试框架 |

## 常见问题

### Q: PySide6 DLL 加载失败
**解决：** 确保使用正确的 Python 版本（3.11+），或重新安装 PySide6：
```bash
pip uninstall PySide6
pip install PySide6
```

### Q: 目录页检测失败
**解决：** 应用会弹出提示，可手动指定目录页位置（后续版本功能）

## 技术架构

```
用户操作 → MainWindow → TOCDetector (检测目录页)
                        ↓
                      TOCParser (解析书签树)
                        ↓
                      EditorWindow (编辑预览)
                        ↓
                      BookmarkWriter (写入PDF)
```

## 开发信息

- 版本：0.1.0
- 架构：单体应用 + PySide6 + PyMuPDF
- 测试覆盖：20+ 单元测试