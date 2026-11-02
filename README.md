# OQI.ME · Keycloak Login Theme

一个温馨的 Keycloak 登录主题。暖灯小屋、绿植和打盹的小猫，让每一次登录都像回家。

<p align="center"><img src="themes/oqi/login/resources/img/home-oqi.png" alt="Warm watercolor cottage with an oqi.me wooden nameplate" width="620"></p>

**主题名：`oqi` · 适配 Keycloak 21.1.x · 实测 21.1.2 · Apache-2.0**

## 特性

- 水彩小屋与 `oqi.me` 门牌、米杏色背景、`OQI.ME` 品牌标识。
- 中文与英文，语言菜单使用 Keycloak 生成的链接。
- 响应式布局、深浅色切换、密码显示按钮。
- 保留 Keycloak 原生认证：注册、密码找回、OTP、邮箱验证、授权和退出等由 Realm 配置控制。
- 字段错误、全局提示、会话过期及回调地址错误与真实服务端状态联动。
- 无前端构建依赖，无外部 CDN；脚本不拦截认证提交，也不存储凭据。

## 下载与安装

[从 Releases 下载 ZIP 或 JAR](https://github.com/662/oqi-keycloak-theme/releases/latest)。NAS / Docker 推荐使用 ZIP 中的目录版。

### 目录挂载

克隆仓库，或解压 Release 安装包，在**现有** Keycloak 服务中追加挂载：

```yaml
services:
  keycloak:
    volumes:
      - ./themes/oqi:/opt/keycloak/themes/oqi:ro
```

这是官方镜像的路径；保留原有数据库、环境变量、网络和其他卷。应用容器配置后，在管理台选择业务 Realm：

**Realm settings → Themes → Login theme → `oqi` → Save**

完整安装、国际化设置、自定义和回退步骤见 [中文部署说明](docs/INSTALL.zh-CN.md)。

### JAR 安装

将 Release 的 `oqi-keycloak-21.1.jar` 放到 `/opt/keycloak/providers/`。按当前部署方式重启或重建，然后选择 `oqi`。如果使用 `start --optimized`，须先按原构建参数重新执行 `kc.sh build`。

目录与 JAR 安装方式选一种，避免同名主题重复。

## 从源码构建

只需要 Python 3：

```sh
python3 build-jar.py
```

输出 `providers/oqi-keycloak-21.1.jar`，包含主题注册信息和静态资源目录。

## 自定义

在 `themes/oqi/login/` 中修改：

| 内容 | 文件 |
| --- | --- |
| 品牌、是否展示插图 | `theme.properties` 中的 `oqiBrand`、`oqiShowIllustration` |
| 中文文案 | `messages/messages_zh_CN.properties` |
| 英文文案 | `messages/messages_en.properties` |
| 配色与布局 | `resources/css/oqi.css` |
| 小屋插图 | `resources/img/home-oqi.png` |

修改消息文件时保留 `# encoding: UTF-8` 和 `{0}` 等占位符。品牌域名不会自动更改认证服务地址、DNS 或客户端回调配置。

## 兼容性与验证

基于 Keycloak 21.1.2 的 FreeMarker 模板接口，通过 `parent=keycloak` 继承原生认证页面。五个自定义模板只负责布局、提示和登录介绍，不替换认证后端。

已在本地 Keycloak 21.1.2 验证目录与 JAR 安装、错误密码、注册校验、找回密码邮件、OTP 登录、OAuth 授权拒绝和退出等流程。21.1.0 / 21.1.1 未分别启动测试；其他大版本及自定义 SPI 需要单独验证。详见 [验证记录与范围](VALIDATION.md)。

插图使用生成式图像工具制作，素材与编辑说明见 [DESIGN-NOTES.md](DESIGN-NOTES.md)。

## English

A warm, self-contained login theme for Keycloak 21.1.x, runtime-tested on 21.1.2. Theme name: **`oqi`**. It supports Chinese/English, mobile layouts, light/dark appearance, and native Keycloak authentication flows.

Download a directory ZIP or a theme JAR from [Releases](https://github.com/662/oqi-keycloak-theme/releases/latest). Mount `themes/oqi` at `/opt/keycloak/themes/oqi`, or install the JAR in `/opt/keycloak/providers`. Select `oqi` as the realm's **Login theme**. Build from source using `python3 build-jar.py`. Review the validation scope before deploying on other versions.

## License

[Apache License 2.0](LICENSE.txt). See [NOTICE.txt](NOTICE.txt) for attribution to the upstream Keycloak templates.

- [Keycloak 21.1.2 theme documentation](https://www.keycloak.org/docs/21.1.2/server_development/#_themes)
- [Upstream login templates](https://github.com/keycloak/keycloak/tree/21.1.2/themes/src/main/resources/theme/base/login)
