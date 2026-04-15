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

### macOS

```bash
# 查看 otlg 位置
which otlg

# 如果在 ~/.local/bin 下，添加到 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 如果是二进制文件，移动到已有 PATH 目录
sudo mv otlg /usr/local/bin/

# 验证
otlg --help
```

### Linux

```bash
# 查看 otlg 位置
which otlg

# 方式 A：添加到 PATH（适用于 pip 安装）
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 方式 B：移动到系统目录（适用于二进制文件）
sudo mv otlg /usr/local/bin/

# 验证
otlg --help
```

### Windows

**方式 A：通过 PowerShell 临时添加（当前会话有效）**

```powershell
$env:PATH += ";C:\Users\你的用户名\AppData\Local\Programs\Python\Python3x\Scripts"
otlg --help
```

**方式 B：永久添加到系统 PATH**

```powershell
# 1. 查看 Python scripts 目录（pip 安装时使用）
python -c "import sysconfig; print(sysconfig.get_path('scripts'))"

# 2. 将输出的路径添加到系统环境变量
# 打开：设置 → 系统 → 关于 → 高级系统设置 → 环境变量
# 在 "用户变量" 或 "系统变量" 中找到 Path → 编辑 → 新建 → 粘贴路径 → 确定

# 3. 重新打开 PowerShell 验证
otlg --help
```

**方式 C：二进制文件**

将下载的 `otlg.exe` 移动到 `C:\Windows\System32\`（需要管理员权限），或创建专用目录并加入 PATH：

```powershell
# 创建目录并移动文件
mkdir C:\Tools
move otlg.exe C:\Tools\

# 添加到用户 PATH（永久）
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Tools", "User")

# 重新打开 PowerShell 验证
otlg --help
```

## 卸载

### pip 安装卸载

```bash
pip uninstall yunsheng-skills
```

### 二进制文件卸载

```bash
# macOS / Linux
sudo rm /usr/local/bin/otlg
# 或
rm ~/.local/bin/otlg

# Windows
del C:\Tools\otlg.exe
# 或从 System32 删除（需要管理员权限）
del C:\Windows\System32\otlg.exe
```

### 配置文件清理

```bash
# 所有平台通用 — 删除配置目录
rm -rf ~/.otlg
```

## 验证安装

```bash
otlg --help
otlg domains
otlg types --domain finance
```

三个命令都正常输出即表示安装成功。
