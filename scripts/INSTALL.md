# otlg 安装指南

## 方式一：pip install（推荐）

适用于任何有 Python 环境的平台。

```bash
pip install git+https://github.com/YunSheng-T/yunsheng-skills.git
otlg --help
```

安装后 `otlg` 会出现在 Python 的 scripts 目录下。如果提示命令找不到，需要将该目录加入 PATH（见下方 [配置环境变量](#配置环境变量)）。

## 方式二：下载二进制文件

从 [GitHub Releases](https://github.com/YunSheng-T/yunsheng-skills/releases) 下载对应平台的文件。

### macOS / Linux

```bash
# 下载到当前目录
curl -L -o otlg https://github.com/YunSheng-T/yunsheng-skills/releases/latest/download/otlg-macos-arm64
# Linux 用这个：
# curl -L -o otlg https://github.com/YunSheng-T/yunsheng-skills/releases/latest/download/otlg-linux-amd64

chmod +x otlg
./otlg --help
```

建议移动到系统目录（见下方 [配置环境变量](#配置环境变量)）。

### Windows

```powershell
# 下载到当前目录
Invoke-WebRequest -Uri "https://github.com/YunSheng-T/yunsheng-skills/releases/latest/download/otlg-windows-amd64.exe" -OutFile "otlg.exe"
.\otlg.exe --help
```

建议移动到固定目录并加入 PATH（见下方 [配置环境变量](#配置环境变量)）。

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

## 配置环境变量

安装后需要确保 `otlg` 在你的 PATH 中，才能在任意位置直接使用。

### pip install 后找不到命令

pip 会把 `otlg` 安装到 Python 的 scripts 目录，需要确认该目录在 PATH 中：

```bash
# 查看 pip 安装位置
pip show yunsheng-skills | grep Location
# 或者直接查找 otlg 的位置
which otlg       # macOS / Linux
where otlg       # Windows
```

常见路径：
- macOS / Linux: `~/.local/bin` 或 `~/Library/Python/3.x/bin`
- Windows: `C:\Users\<用户名>\AppData\Local\Programs\Python\Python312\Scripts`

### macOS / Linux

```bash
# 查看当前 PATH
echo $PATH

# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 验证
otlg --help
```

如果二进制下载到了自定义目录：

```bash
# 移动到 /usr/local/bin（需要 sudo）
sudo mv ./otlg /usr/local/bin/otlg

# 或移动到用户目录
mkdir -p ~/bin
mv ./otlg ~/bin/
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Windows

**方法一：PowerShell 临时设置（当前会话有效）**

```powershell
$env:PATH += ";C:\path\to\otlg\directory"
otlg --help
```

**方法二：永久设置（系统环境变量）**

1. 打开「系统属性」→「高级」→「环境变量」
2. 在「用户变量」中找到 `Path`，点击「编辑」
3. 点击「新建」，添加 `otlg.exe` 所在的目录路径（如 `C:\Tools`）
4. 点击「确定」保存
5. 重新打开终端验证：

```powershell
otlg --help
```

**方法三：PowerShell 永久设置**

```powershell
# 添加到用户 PATH（永久生效）
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Tools", "User")
# 重新打开终端后生效
```

## 验证安装

```bash
otlg --help
otlg domains
otlg types --domain finance
```

三个命令都正常输出即表示安装成功。