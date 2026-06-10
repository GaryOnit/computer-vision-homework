# opencv-people 快速启动

这个项目是一个最简命令行人像分割工具：输入图片，输出透明背景 PNG。

## 1. Windows 快速启动（PowerShell）

```powershell
cd D:\path\to\opencv-people
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py people.jpg
```

运行完成后会在当前目录生成：
- `people_portrait.png`

---

## 2. macOS 快速启动（Terminal）

```bash
cd /path/to/opencv-people
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py people.jpg
```

运行完成后会在当前目录生成：
- `people_portrait.png`

如果你在 macOS + Homebrew Python 环境遇到 `pyexpat` 动态库问题，可用：

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib ./venv/bin/python app.py people.jpg
```

---

## 3. 自定义输入/输出

```bash
python app.py your_photo.jpg -o out.png
```
