# my-github-2024

生成你的 GitHub 年度数据统计图。

[English](README.md) | 简体中文

## 示例

![example](example.png)


## 使用方法

### 0. **准备 GitHub 访问令牌**

在 [Personal Access Tokens (Classic)](https://github.com/settings/tokens) 页面生成一个新的 GitHub 访问令牌。

---

### 1. **创建并激活 Conda 虚拟环境**

运行以下命令创建名为 `mygithub2024` 的虚拟环境，并指定 Python 版本：

```shell
conda create -n mygithub2024 python=3.12
conda activate mygithub2024
```

---

### 2. **修改 `.env` 文件**

在根目录中找到 `.env` 文件，并填写你的 GitHub 访问令牌、用户名和时区：

```shell
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_USERNAME=your-github-username
GITHUB_TIMEZONE=Asia/Shanghai
```

---

### 3. **安装依赖项**

运行以下命令安装项目所需的依赖项：

```shell
pip install -r requirements.txt
```

---

### 4. **启动程序**

运行以下命令启动程序：

```shell
python main.py
```

---

### 5. **预览项目**

- 在 **VSCode** 中，点击窗口右下角的 `Go Live` 按钮进行预览。

**或者**：

- 在浏览器中直接打开：

```shell
dist/index.html
```

---

## TODO

在线版本正在开发中，敬请期待。