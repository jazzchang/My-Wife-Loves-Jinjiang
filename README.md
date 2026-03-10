# My Wife Loves Jinjiang 📖

> 专为老婆量身打造的极简主义「晋江文学城」单本小说连载下载器 (macOS)。
> 告别繁琐的网页操作与粗糙的下载工具，用浪漫专属的高颜值设计语言重构阅读、收集体验。
> 注意：只能下载免费书籍，VIP书籍不能下载。

## 📦 如何使用

本工具提供开箱即用的 macOS 原生客户端程序，您无需折腾环境即可随时享用。

1. 进入本项目发布的 **Releases** 栏目，下载最新的 `MyWifeLovesJinjiang.zip` 压缩包。
2. 解压缩获取 `.app` 应用程序。
3. 双击运行应用程序，点击右上角设置图标选择您要保存本小说的本地文件夹。
4. 复制贴入晋江文学城小说详情页地址（如：`https://www.jjwxc.net/onebook.php?novelid=9702952`）。
5. 点击专属的 `start` 胶囊悬浮按钮，后台将自动生成一本结构工整的 `.txt` 小说典藏文件送达您的设定目录。

> **安全提示**：由于 `.app` 包未经过 Apple 开发者企业证书官方公证认证（纯属私域程序），如果提示损坏或安全性拦截，请前往**系统偏好设置 -> 隐私与安全性**面板内选择「仍要打开」。

## 🛠️ 技术栈与二次开发

本项目非常极轻，由 Python 3.13 驱动。

* **UI 图形库**: PyQt6
* **网络与解析**: requests, BeautifulSoup4
* **可执行化方案**: PyInstaller 封装 macOS Bundles

要在您的本地展开二次开发：

```bash
# 激活环境、安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt # 请确保持有 requests bs4 pyqt6 

# 拉起 GUI 图形程序
python main_app.py
```

## 💖 寄语

希望这款带满私意的小工具，能让您和所爱之人的体验更加流畅与甜蜜。
