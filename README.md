<div align="center">
  <img src="logo.png" alt="logo" />

  Statistics of your activities on GitHub in 2024.

  [简体中文](README_zh-CN.md) | English

  [![Server Status](https://img.shields.io/badge/dynamic/json?logo=linux&color=brightgreen&label=Server%20status&query=%24.status&cacheSeconds=600&url=https%3A%2F%2F2024.ch3nyang.top%2Fstatus)](https://2024.ch3nyang.top)

  [![GitHub issues](https://img.shields.io/github/issues/WCY-dt/my-github-2024)](https://github.com/WCY-dt/my-github-2024/issues) [![GitHub pull requests](https://img.shields.io/github/issues-pr/WCY-dt/my-github-2024)](https://github.com/WCY-dt/my-github-2024/pulls) [![GitHub license](https://img.shields.io/github/license/WCY-dt/my-github-2024)](https://github.com/WCY-dt/my-github-2024/blob/main/LICENSE)

  <strong style="font-size: 24px;">👉 Try it now: <a href="https://2024.ch3nyang.top">https://2024.ch3nyang.top</a></strong>
</div>

## Example

![example](example.png)

## Usage

> [!TIP]
>
> **New feature**: Now you can select any year from 2008 to 2024 to generate a report.

1. Visit [https://2024.ch3nyang.top](https://2024.ch3nyang.top).

2. Click the `Sign in with GitHub` button and authorize login.

3. Select your time zone and the year you want to generate, then click the `Generate` button, wait a few seconds, and you can view your activities on GitHub in 2024.

## Run locally

> [!IMPORTANT]
>
> Due to the features of the `datetime` library, this project requires Python-3.12 or above.

1. Clone the repository:

    ```bash
    git clone https://github.com/WCY-dt/my-github-2024.git
    cd my-github-2024
    ```

2. Create a Github OAuth App:

    Visit [GitHub Developer Settings](https://github.com/settings/developers) to create a new OAuth App. In it, fill in `Homepage URL` and `Authorization callback URL` with `http://127.0.0.1:5000` and `http://127.0.0.1:5000/callback` respectively.

    Get `Client ID` and `Client Secret`.

3. Configure the environment variable `.env` file in the root directory of the project. The content is as follows:

    ```env
    CLIENT_ID=your_client_id
    CLIENT_SECRET=your_client_secret
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Run the project:

    ```bash
    python my-github-2024.py
    ```

6. Visit `http://127.0.0.1:5000` and complete!
