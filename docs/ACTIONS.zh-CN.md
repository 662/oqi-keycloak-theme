# GitHub Actions 设计与使用

## 工作流

| 工作流 | 触发方式 | 结果 |
| --- | --- | --- |
| CI | 提交到 `main`、PR、Actions 页面手动运行，或被 Release 复用 | 校验源码和模板，构建安装包，保留 14 天的构建产物 |
| Release | 推送 `v*` 标签 | 复用同一套 CI，通过后上传并公开该版本的 Release |

### CI 检查什么

1. 主题注册名、继承关系、版本号与 changelog 一致性。
2. 中英文消息键、占位符、模板和 CSS 引用的资源文件。
3. 原生登录表单的 POST 地址约定与 JavaScript 语法。
4. 使用 Keycloak 21.1.2 配套的 **FreeMarker 2.3.31** 解析五个自定义模板，并执行 9 个 Realm 标题回退与 HTML 转义测试。依赖 JAR 从 Maven Central 下载，并核对固定 SHA-256。
5. 13 个不访问 GitHub 的发布分支测试：版本不匹配、提交不匹配、已发布版本保护、文件损坏、上传中断、草稿恢复等。
6. 连续构建两次 JAR，确保相同源码生成相同字节；检查 JAR 的资源目录和源文件内容，生成 ZIP、JAR、校验文件和构建提交记录。
7. 发布脚本 dry-run，只验证输入，不创建 Release。

构建文件在 Actions 运行详情的 **Artifacts** 下载：`oqi-theme-<完整提交 SHA>`。

CI 是模板解析、静态契约和打包检查，不会启动 NAS，也不等同于重跑全部真实认证流程。历史运行验证范围见根目录的 `VALIDATION.md`。

### Release 怎么发布

Release 只使用当前标签提交构建出的产物，不复用 PR 或其他运行中的文件。发布前检查：

- 标签必须与 `META-INF/MANIFEST.MF` 的版本一致，例如 `v1.1.1` 对应 `Implementation-Version: 1.1.1`。
- 构建提交必须等于工作流提交和远程标签实际指向的提交。
- 本地 ZIP/JAR 的 SHA-256 必须正确。

随后先创建 **Draft Release**，上传 ZIP、JAR、`SHA256SUMS.txt`，核对 GitHub 返回的文件大小、上传状态和摘要后，才将草稿公开。

上传失败时保留草稿，修复问题后可重新运行。已公开且文件一致的版本保持不变；已公开但摘要不匹配时直接失败，不覆盖正式文件。

带 `-rc.1` 等后缀的版本自动标记为 prerelease。已有 `v1.1.0` 不会因为增加工作流而自动重新发布；不要移动旧标签。

## 发布下一个版本

以 `1.1.1` 为例：

1. 把 `META-INF/MANIFEST.MF` 的 `Implementation-Version` 改为 `1.1.1`。
2. 在 `CHANGELOG.md` 中添加 `## 1.1.1` 条目。
3. 提交到主分支并确认 CI 通过。
4. 给该提交打标签并推送：

   ```sh
   git tag v1.1.1
   git push origin v1.1.1
   ```

Release 工作流将自动运行。无需手工上传安装文件。

## 权限和依赖

- CI、PR 检查及构建任务只有 `contents: read`，不使用 `pull_request_target`。
- 只有标签发布任务具有 `contents: write`，使用 GitHub 自带 `GITHUB_TOKEN`，不需要个人访问令牌或 NAS 凭据。
- 官方 Actions 固定到完整提交 SHA，并标注对应版本。
- Checkout 不保留 Git 凭据。
- 构建新提交会取消同分支/PR 的旧 CI；同一标签的发布任务串行运行，避免互相覆盖。
- 本配置不更改仓库分支保护、访问权限或现有版本文件。

## 本地运行

```sh
python3 scripts/validate-theme.py
python3 -m unittest discover -s tests -v
node --check themes/oqi/login/resources/js/oqi.js
python3 scripts/package-release.py
python3 scripts/publish-release.py --dry-run
```

真实 FreeMarker 解析需要 Java 17 和 2.3.31 依赖；CI 中的命令展示了下载和校验方式。`dist/` 的内容默认不纳入 Git。
