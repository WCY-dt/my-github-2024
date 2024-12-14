# my-github-2024

Generate your GitHub yearly statistics chart.

[简体中文](README_zh-CN.md) | English

## Example

![example](example.png)

## Usage

### 0. **Prepare Your GitHub Access Token**

1. Go to the [Personal Access Tokens (Classic)](https://github.com/settings/tokens) page.  
2. Generate a new GitHub access token and ensure it has the necessary scopes (such as `repo`, `user`, etc.).

---

### 1. **Create and Activate a Conda Virtual Environment**

Run the following commands to create a virtual environment named `mygithub2024` with Python 3.12 and activate it:

```shell
conda create -n mygithub2024 python=3.12
conda activate mygithub2024
```

---

### 2. **Modify the `.env` File**

In the root directory, locate or create a `.env` file and fill in the following information:

```shell
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_USERNAME=your-github-username
GITHUB_TIMEZONE=Asia/Shanghai
```

**Tips**:  
- Ensure the `.env` file is excluded from version control by adding it to `.gitignore`.
- Replace `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` with your actual GitHub access token.

---

### 3. **Install Dependencies**

Run the following command to install the required dependencies:

```shell
pip install -r requirements.txt
```

---

### 4. **Start the Program**

Run the following command to execute the program:

```shell
python main.py
```

---

### 5. **Preview the Project**

- In **VSCode**, click the `Go Live` button located in the bottom right corner to start the local server and preview the project.

**Alternatively**, you can open the `dist/index.html` file directly in your browser:

```shell
dist/index.html
```

---

## TODO

The online version is under development. Please stay tuned!