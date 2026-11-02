# OQI.ME · Keycloak 21.1 登录主题

这是一套可安装的 Keycloak **Login theme**，名称为 `oqi`。保留暖灯小屋、绿植、小猫、米杏色背景和深绿色表单，支持中文、英文、手机布局、深浅色切换和密码显示。

适配目标：Keycloak **21.1.x**。已使用官方 **21.1.2** 发行版、Java 17、默认 Browser flow 和合成测试 Realm 进行实际运行验证。不是 Sites 网页的 iframe，也没有模拟认证逻辑；表单由 Keycloak 在自己的登录域名中渲染。

## 文件怎么选

- NAS / Docker 用户：推荐用 `themes/oqi/` 目录挂载，修改图片和文案方便。
- 使用镜像构建或集中部署：可以用 `providers/oqi-keycloak-21.1.jar`。
- 同一实例只选一种方式，避免同名主题来源重复。
- 所有文件都已准备好，不需要 Node.js、npm、前端构建或联网加载 CDN。

## 方式一：NAS 容器目录挂载（推荐）

1. 把Release 安装包解压到 NAS 的持久化目录。例如你的原 Compose 文件所在目录，解压后能看到 `themes/oqi/login/theme.properties`。
2. 在**现有的 Keycloak 服务**上增加一个只读挂载。下面只展示新增项，请保留原服务的数据库、网络、环境变量和其他卷设置：

   ```yaml
   services:
     keycloak:
       volumes:
         - ./themes/oqi:/opt/keycloak/themes/oqi:ro
   ```

   `/opt/keycloak` 是官方 `quay.io/keycloak/keycloak` 镜像的路径。Bitnami 镜像通常使用 `/opt/bitnami/keycloak/themes/oqi`；如果你的镜像有自己的安装目录，应以镜像的 `$KC_HOME` 为准。NAS 管理界面也可以添加同样的「宿主机目录 → 容器目录」挂载。
3. 通过原来的管理方式应用容器配置；Compose 用户可执行 `docker compose up -d keycloak`（服务名按你自己的配置替换）。新增挂载需要重建容器，单纯 `restart` 不会添加卷；保留原有持久化卷。
4. 进入 Keycloak 管理台，选择你的业务 **Realm**，打开 **Realm settings → Themes**。
5. 把 **Login theme** 设为 **oqi**，保存。
6. 从 NAS 原应用正常发起登录，或打开该 Realm 的 Account 页面触发登录，检查效果。

不用修改 Admin、Account 或 Email theme。本主题只注册 `login` 类型。

## 方式二：安装 JAR

把 `providers/oqi-keycloak-21.1.jar` 放到 Keycloak 的 `providers/` 目录；官方镜像中的目标是：

```text
/opt/keycloak/providers/oqi-keycloak-21.1.jar
```

重启或按原镜像流程重新构建服务后，在 Realm 的 **Login theme** 中选择 `oqi`。

如果使用 `start --optimized` 或已有多阶段镜像构建：在原有构建阶段复制此 JAR，再用**原来的数据库和其他构建参数**执行 `kc.sh build`，然后部署构建产物。仅修改运行中容器的文件不是持久化安装方式。

JAR 包含 `META-INF/keycloak-themes.json`、明确的资源目录和全部主题静态资源，已验证可独立加载；无需再安装目录版本。

## 中文、英文与深浅色

在 **Realm settings → Localization** 中启用国际化，允许 `zh-CN` 和 `en`，可把默认语言设为 `zh-CN`。具体管理台标签可能随语言设置略有不同。只有 Realm 启用了多种支持语言，页面才显示语言菜单。

语言链接由 Keycloak 生成，会保留当前认证流程。深浅色按钮只在浏览器本地保存 `oqi-appearance` 这一项外观偏好，不保存用户名、密码或验证码。禁用 JavaScript 后，原生登录表单仍可用，外观切换和密码显示按钮不可用。

## 页面和真实状态

主题继承 `parent=keycloak`，未覆盖的页面使用当前安装的 Keycloak 21.1 原生模板，再统一应用 OQI.ME 布局和样式。页面与状态由实际认证流程决定。

- 普通登录、邮箱登录、分步用户名/密码：保留原字段名、隐藏凭据字段、回填值、服务端表单地址与动态入口。
- 错误密码、账户停用或暂时禁用：展示服务端字段错误或全局提示，不在前端判定身份。
- 注册、找回密码、密码策略、强制改密码、个人资料更新：由 Realm 的配置和服务端校验驱动。
- 邮箱验证、OTP 登录和绑定、验证码错误、多凭据选择、其他认证方式：沿用原生模板、数据、二维码和密钥。
- WebAuthn、账户关联、条款、授权、退出登录、恢复码等：沿用原生页面和认证脚本。是否出现取决于你启用的功能；没有配置这些功能时不会多出入口。
- 会话超时、页面过期、操作链接失效及信息页：展示服务端消息，继续/重新开始/返回应用等链接遵循原生条件。
- 无效 `redirect_uri` 或 `post_logout_redirect_uri`：保留服务端错误，并给出较易读的说明；不会把请求参数拼成返回链接。返回应用入口只使用服务端模板允许的 `client.baseUrl`。
- 回调已通过验证后，某些 OAuth/OIDC 错误会返回原应用，例如拒绝授权的 `access_denied`。它们不会被主题拦截成自定义成功或错误页面。

邮件内容仍由你当前 Email theme 负责。若启用「条款」必需操作，请先在 Realm 的本地化覆盖中设置自己的 `termsText`；使用条款内容应由部署者配置。

## 修改品牌和文案

目录模式直接修改 `themes/oqi/login/`；JAR 模式修改后重新打包。

- 品牌名称：`theme.properties` 中的 `oqiBrand=OQI.ME`。
- 隐藏左侧插图区域：`oqiShowIllustration=false`。
- 小屋图片：`resources/img/home-oqi.png`。
- 中文文案：`messages/messages_zh_CN.properties`。
- 英文文案：`messages/messages_en.properties`。
- 配色、字体、间距：`resources/css/oqi.css`。

消息文件保持 UTF-8，并保留首行 `# encoding: UTF-8`。带 `{0}` 等占位符的消息须保留占位符。不要在模板、脚本或 CSS 中填写账户密码、回调地址或生产 OTP 密钥。

修改生产主题文件后重启 Keycloak 以刷新缓存，浏览器再刷新页面。开发时可临时关闭主题缓存：

```text
--spi-theme-static-max-age=-1
--spi-theme-cache-themes=false
--spi-theme-cache-templates=false
```

生产环境保持原有缓存设置，无需添加上述开发参数。

## 从旧 haven 主题迁移

这是独立的新主题 `oqi`。先按本文安装新主题，再把 Realm 的 Login theme 从 `haven` 切换到 `oqi`。确认登录正常后，可以移除旧 `haven` 挂载或 JAR。无需更改 Realm 名称、客户端 ID、用户数据、DNS 或现有回调地址。页面上的域名品牌不会自动更改认证服务地址。

## 卸载、回退与排查

- 回退：先把业务 Realm 的 **Login theme** 改回 `keycloak` 并保存，再移除 OQI.ME 的挂载或 JAR，重启服务。
- 列表中没有 `oqi`：核对挂载层级、可读权限和实例实际安装目录；检查 JAR 是否进入了本次构建；查看服务端日志。
- 页面只有文字、没有样式：检查浏览器的 `/resources/.../login/oqi/` 请求，确认 CSS、JS、SVG 返回正常；反向代理须允许 Keycloak 的 `/resources/` 路径，不要加 `/auth` 等不匹配的前缀。
- 页面仍是旧样式：确认进入正确 Realm、Login theme 已保存，且没有同名主题重复安装；重启刷新主题缓存。
- 报错仍然存在：主题只负责呈现。无效返回地址须在对应 Client 的配置中修复；邮箱发送需要 Realm 的 SMTP 配置；OTP 和 WebAuthn 需要相应认证流程。
- 自定义 SPI、额外模板或其他 Keycloak 大版本：需单独验证。升级 Keycloak 时复查本主题覆盖的五个 `.ftl` 文件，不要假设跨版本模板接口不变。

## 构建与验证

Release 中的 JAR 可直接安装。如修改了目录源码，在本解压目录运行：

```sh
python3 build-jar.py
```

输出 `providers/oqi-keycloak-21.1.jar`。此脚本只用 Python 标准库，不访问网络，也不包含测试账户或服务器。

详见仓库根目录的 `VALIDATION.md` 中的已验证项目与未实测范围。许可证为 Apache-2.0，参见 `LICENSE.txt`、`NOTICE.txt`。

## 官方依据

- [Keycloak 21.1.2 Server Developer Guide — Themes](https://www.keycloak.org/docs/21.1.2/server_development/#_themes)
- [Keycloak 21.1.2 Realm 主题配置](https://www.keycloak.org/docs/21.1.2/server_admin/#_themes)
- [21.1.2 原生登录模板](https://github.com/keycloak/keycloak/tree/21.1.2/themes/src/main/resources/theme/base/login)

## 插图更新（1.0.1）

小屋主插图已换为图像生成模型绘制的透明背景水彩 PNG（1484×1060），不再使用原来手写的 SVG 小屋。图标和纸张纹理仍使用小型 SVG。
