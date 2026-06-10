# opencv-car 快速启动

这个项目是一个最简命令行车辆计数工具：输入道路视频，输出带检测框和计数结果的标注视频。

## 1. Windows 快速启动（PowerShell）

```powershell
cd D:\path\to\opencv-car
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py --no-preview
```

运行完成后会在当前目录生成：
- `output_videos/output_counted.mp4`

---

## 2. macOS 快速启动（Terminal）

```bash
cd /path/to/opencv-car
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py --no-preview
```

运行完成后会在当前目录生成：
- `output_videos/output_counted.mp4`

如果你在 macOS + Homebrew Python 环境遇到 `pyexpat` 动态库问题，可用：

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib ./venv/bin/python app.py --no-preview
```

---

## 3. 自定义输入/输出

```bash
python app.py --input vehicle.mp4 --output output_videos/custom.mp4
```
