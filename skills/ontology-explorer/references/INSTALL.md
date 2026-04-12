# otlg 安装指南

## 方式一：pip install（推荐）

```bash
pip install git+https://github.com/YunSheng-T/yunsheng-skills.git
otlg --help
```

安装后 `otlg` 会出现在 Python 的 scripts 目录下。如果提示命令找不到，需要将该目录加入 PATH（见下方 [配置环境变量](#配置环境变量)）。

## 方式二：下载二进制文件

从 [GitHub Releases](https://github.com/YunSheng-T/yunsheng-skills/releases) 下载对应平台的文件。

### macOS / Linux

```bash
curl -L -o otlg https://github.com/YunSheng-T/yunsheng-skills/releases/latest/download/otlg-macos-arm64
chmod +x otlg
./otlg --help
```

建议移动到系统目录（见下方 [配置环境变量](#配置环境变量)）。

### Windows

```powershell
Invoke-WebRequest -Uri "https://github.com/YunSheng-T/yunsheng-skills/releases/latest/download/otlg-windows-amd64.exe" -OutFile "otlg.exe"
.\otlg.exe --help
```

## 方式三：clone + uv run

适用于开发者或需要修改源码的场景。

```bash
git clone https://github.com/YunSheng-T/yunsheng-skills.git
cd yunsheng-skills
uv sync
uv run otlg types
```

## 配置环境变量

安装后需要确保 `otlg` 在你的 PATH 中。

```bash
# 查看 otlg 位置
which otlg

# 添加到 ~/.zshrc 或 ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 验证
otlg --help
```

## 验证安装

```bash
otlg --help
otlg domains
otlg types --domain finance
```

三个命令都正常输出即表示安装成功。
