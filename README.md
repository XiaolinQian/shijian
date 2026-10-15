# 时笺 · SHIJIAN 宣传站

这是独立的静态网站，所有页面、图片、安装包都位于 `promo-site`。无需 npm、构建工具、数据库、账户或外部字体服务；未修改桌面应用源码。

## 查看与下载

双击 `index.html` 可直接预览；正式测试下载或在局域环境查看时，建议启动 HTTP 服务：

```sh
cd /Users/qianxiaolin/Desktop/AIJob/TodoApp/promo-site
python3 -m http.server 4173 --bind 127.0.0.1
```

打开 http://127.0.0.1:4173/ 。下载区包含真实 DMG、SHA-256 校验文件和宣传素材 ZIP。

- macOS：v0.1.0，Intel x64，macOS 13+；6,081,428 字节（5.80 MiB）。当前未签名、公证，Apple Silicon 原生包未提供。
- Windows：未提供安装包，按钮禁用，不会跳转到无效链接。
- 功能介绍按现有实现撰写：本地汇总、报告补充 / 导出；没有宣称 AI 润色或云同步已上线。

## 发布静态站

将 `downloads/TodoApp-website.zip` 解压到网站根目录，或上传以下内容到支持静态文件的主机：

```text
index.html
styles.css
assets/
press/
downloads/
```

全站使用相对路径，可部署在域名根目录或子目录。`tools/`、`verification/` 和 README 不必上传。若手动上传 downloads，请排除 `TodoApp-website.zip` 本身。

建议配置：

- 通过 HTTPS 提供服务；确保主机允许约 6 MB 的 DMG 文件。
- `.dmg` 返回 `application/x-apple-diskimage`，`.zip` 返回 `application/zip`；为下载文件设置 `Content-Disposition: attachment`。
- 更新页面 `<meta property="og:image">` 为真实站点下 `assets/share-cover.jpg` 的绝对 URL，便于社交平台抓取；当前不预设域名。
- `index.html` 使用较短缓存时间；更新安装包时修改文件名及下载链接，再更新 SHA256SUMS。
- 当前为可预览、可部署的本地站点；没有代替你购买域名或发布到外部账户。

## 宣传素材

`press/01-cover.png` 至 `04-download.png`：4 张 1080 × 1920 竖版原图。对应 JPG 为网页缩略图。

- `01-cover.png`：主宣传图，包含实际应用截图。
- `02-workflow.png`：记录 → 提醒 → 复盘。
- `03-reports.png`：日报、周报和月报。
- `04-download.png`：macOS 体验版下载引导。
- `press/短视频分镜与配文.md`：20 秒分镜、配文和使用说明。
- `assets/share-cover.jpg`：1200 × 630 横版分享封面。
- `downloads/TodoApp-press-kit.zip`：原图、横版封面及分镜文案合集。

内置 image_gen 调用未返回图片文件；最终 PNG 为真实应用素材与本地排版生成，未使用 API / CLI 生图付费回退。尝试的提示词及生成方式见 `tools/图片生成记录.md`。

## 修改与重新打包

- 页面内容：`index.html`；颜色、布局与响应式：`styles.css`。
- 宣传图文字和布局：`tools/render_press.py`，需要 Python + Pillow 和本机中文字体。没有分发字体文件。
- 生成图片：`python3 promo-site/tools/render_press.py`（在项目根目录运行）。
- 生成素材和网站 ZIP：`python3 promo-site/tools/package_release.py`。
- 浏览器检查：`node promo-site/tools/verify.mjs`。需要 Playwright 和 Chrome，可用 `PLAYWRIGHT_MODULE` 指向 Playwright 的 index.mjs，用 `PROMO_CHROME` 指定 Chrome 路径。

检查记录和页面截图保存在 `verification/`，不进入发布 ZIP。

## 名称与图标更新

当前宣传品牌为「时笺 · SHIJIAN」。历史应用截图和下载包仍是旧名称「日序」v0.1.0，页面已标明。新名称和图标已接入应用源码；安装包将在重新构建后更新。品牌源文件见 `../brand/shijian/`。
