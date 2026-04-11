# otlg 安装指南

## 方式一：pip install（推荐）

适用于任何有 Python 环境的平台。

```bash
pip install git+https://github.com/YunSheng-T/yunsheng-skills.git
otlg types
```

## 方式二：下载二进制文件

从 [GitHub Releases](https://github.com/YunSheng-T/yunsheng-skills/releases) 下载对应平台的文件。

### macOS

```bash
curl -L -o otlg https://github.com/YunSheng-T/yunsheng-skills/releases/latest/download/otlg-macos-arm64
chmod +x otlg
./otlg types
```

### Linux

```bash
curl -L -o otlg https://github.com/YunSheng-T/yunsheng-skills/releases/latest/download/otlg-linux-amd64
chmod +x otlg
./otlg types
```

### Windows

```powershell
Invoke-WebRequest -Uri "https://github.com/YunSheng-T/yunsheng-skills/releases/latest/download/otlg-windows-amd64.exe" -OutFile "otlg.exe"
.\otlg.exe types
```

## 方式三：clone + uv run

适用于开发者或需要修改源码的场景。

```bash
git clone https://github.com/YunSheng-T/yunsheng-skills.git
cd yunsheng-skills
uv sync
uv run otlg types
```

## 方式四：从源码构建二进制

适用于需要自定义构建的场景。

```bash
git clone https://github.com/YunSheng-T/yunsheng-skills.git
cd yunsheng-skills
uv sync --group dev
uv run scripts/build.py
./dist/otlg types
```

## 验证安装

```bash
otlg --help
otlg domains
otlg types --domain finance
```
