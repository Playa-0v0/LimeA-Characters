# 贡献规范

本仓库向 LimeA 角色商店提供角色卡。所有改动通过 Pull Request（PR）提交，合并到 `main` 后由 GitHub Actions 建立角色讨论议题并维护 `community.json`。

---

## 仓库结构

```text
catalog.json                      商店清单
community.json                    角色标识与议题编号的映射（自动维护）
<作品标识>/
  <角色标识>/
    character.json                角色卡清单
    prompts/                      固定提示词与对话示例
    worldbook/                    世界书
    assets/                       头像、封面等图片
  <角色标识>.limea                可导入单文件（由制作目录打包）
  <角色标识>-cover.webp           商店封面预览（可选）
icons/                            作品图标（README 展示用）
scripts/                          自动化脚本
tests/                            自动化测试
```

- 作品标识和角色标识只使用小写字母、数字、点、下划线或连字符，且必须以字母或数字开头，最长 128 个字符。
- 角色目录名与角色标识的最后一段保持一致；目录名只用于整理，程序身份以 `character.json` 的 `id` 为准。
- 不要手工修改 `community.json`。它由工作流在合并后写入，手改会与自动化提交冲突。
- 不要修改其他作者的角色卡。一次 PR 只处理一个角色或同一作品的清单元数据修复。

---

## 角色卡要求

角色卡格式由 `character.json` 清单定义，具体解析规则以 LimeA 主仓库的 `docs/character-card-format.md` 为准。发布前必须满足以下全部条件。

### 清单字段

| 字段            | 要求                                                                                      |
| --------------- | ----------------------------------------------------------------------------------------- |
| `format`        | 固定为 `limea-character`                                                                  |
| `formatVersion` | 固定为 `1`；不要自行升级格式版本                                                          |
| `id`            | 必需，反向域名式标识，例如 `org.limea.characters.honkai-star-rail.cyrene`；发布后不得变更 |
| `version`       | 必需，SemVer（语义化版本号），例如 `1.0.1`                                                |
| `name`          | 必需，显示名，最长 80 字符，必须与 `catalog.json` 完全一致                                |
| `nickname`      | 可选，最长 80 字符                                                                        |
| `description`   | 可选，最长 2000 字符                                                                      |
| `author`        | 可选；提供时 `name` 必填且最长 120 字符，`url`（作者主页）必须为 `http` 或 `https` 地址   |
| `tags`          | 可选，最多 32 个，每个最多 40 字符                                                        |
| `prompts`       | 新格式的提示词声明：`fixed` 为固定提示词，`worldbooks` 为世界书文件                       |
| `files`         | 图片与说明文件的用途声明：`avatar`、`cover`、`gallery`、`readme`、`license`               |
| `extensions`    | 可选扩展数据；`limea.dialogueExamples` 标记对话示例文件                                   |

补充约定：

- 同一张卡不能同时使用 `prompts` 与旧格式提示词用途（`system`、`soul`、`voiceExamples`、`worldbook`、`fixed`）。
- 所有路径使用 `/`，相对角色卡根目录，最长 240 字符；必须大小写精确、唯一，并且实际存在。
- 角色卡内不能出现未在清单声明的文件。声明了但缺失的文件同样会导致导入失败。
- 图片只支持静态 PNG、JPEG、WebP，按内容识别而不看后缀。头像建议 1:1，封面建议 3:4，避免自动裁切。
- 世界书按 `## 标题` 分条，建议显式填写稳定的 `id`。更新角色时保留已有条目 `id`，否则已绑定会话的命中记录会丢失。
- `version` 递增规则：仅补全清单元数据或更换图片时递增修订号（`1.0.0` → `1.0.1`）；提示词或世界书内容调整递增次版本号；删除或重命名已有条目、改变运行语义时递增主版本号。

### 容量上限

| 项目           | 上限             |
| -------------- | ---------------- |
| 单个角色卡     | 32 MiB           |
| 压缩容器条目   | 256 项（含目录） |
| 解压总量       | 64 MiB           |
| 单个解压文件   | 16 MiB           |
| 单份文本       | 1 MiB            |
| 商店封面预览图 | 1 MiB，静态 WebP |
| `catalog.json` | 1 MiB            |

---

## 打包与清单更新

`.limea` 本质是 ZIP 容器，解压后的根目录必须直接是 `character.json` 及声明的文件，不能多包一层角色目录。

```powershell
# 在角色制作目录内执行，输出到角色目录的上一级
Compress-Archive -Path .\* -DestinationPath ..\<角色标识>.limea -Force
(Get-FileHash -Algorithm SHA256 ..\<角色标识>.limea).Hash.ToLowerInvariant()
```

每次重新打包后摘要都会变化，必须在同一次提交里更新 `catalog.json`：

```json
{
  "id": "org.limea.characters.honkai-star-rail.cyrene",
  "name": "昔涟",
  "description": "角色简介",
  "archive": "honkai-star-rail/cyrene.limea",
  "sha256": "重新打包后的 SHA-256",
  "cover": {
    "path": "honkai-star-rail/cyrene-cover.webp",
    "sha256": "封面图片的 SHA-256"
  }
}
```

- `archive` 必须位于对应作品目录内；`cover` 同样必须在作品目录内，且只接受静态 WebP。
- `id` 与 `name` 必须与角色卡清单一致；`description` 用于商店列表展示。
- 封面可选，但填写时必须填写图片自身的摘要。

---

## 本地校验

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
```

提交 PR 前逐项确认：

1. 解压 `.limea` 后根目录直接是 `character.json`。
2. `character.json` 的 `id`、`name` 与 `catalog.json` 条目一致。
3. `catalog.json` 的 `sha256` 与实际 `.limea` 文件摘要一致。
4. 制作目录内的每个文件都已在清单声明，且清单声明的文件全部存在。
5. 容量满足上表限制，压缩包内没有符号链接、加密条目或临时文件。
6. `community.json` 未被本次改动修改。

---

## PR 规范

- 分支命名：新增角色使用 `character/<角色标识>`，修正使用 `fix/<角色标识>`。
- 一个 PR 只做一件事：新增一个角色，或更新一个角色，或修复一处清单元数据。
- PR 标题使用单行格式：`type(scope): 中文描述`。`type` 只使用 `feat`、`fix`、`refactor`、`perf`、`style`、`docs`、`test`、`chore`、`ci`、`build`、`revert`；`scope` 使用作品或角色名；描述以动词开头，只说明一件事，不加句号。
  - `feat(角色卡): 发布昔涟角色卡`
  - `fix(昔涟): 修正封面摘要`
  - `docs(仓库): 补充角色卡贡献规范`
- PR 描述必须包含：作品与角色、新增还是更新、变更内容、本地校验结果。
- 新增角色时，同时提交制作目录、`.limea`、`catalog.json` 条目和可选的封面预览图。
- 更新角色时，保持 `id` 不变、递增 `version`、重新打包并更新摘要。已发布角色不得静默改名或更换 `id`。
- 合并后 GitHub Actions 会自动为缺少映射的角色建立讨论议题，并把编号写入 `community.json`。不要在 PR 中预言或手填议题编号。
- PR 的 diff 只应包含与当前角色相关的文件；不要提交 `__pycache__`、编辑器配置、临时压缩包或本地缓存。
- 不接受未经授权转载的素材、包含个人隐私的内容，以及试图绕过容量、路径或格式校验的压缩包。

### 评审清单

- [ ] 角色卡格式、身份字段与商店清单一致
- [ ] `.limea` 与制作目录内容一致，摘要已更新
- [ ] 新角色包含完整可运行的人设、世界书和必要图片
- [ ] 更新角色保留 `id`，`version` 已递增，世界书条目 `id` 未被无故改动
- [ ] 作者信息真实，`author.url` 为 `http`/`https` 地址
- [ ] 本地测试通过，容量未超限
- [ ] 未修改其他角色与 `community.json`

---

## 新角色发布流程

1. 在对应作品目录下创建角色制作目录并编写 `character.json`、提示词、世界书和图片。
2. 按上文打包为 `<角色标识>.limea`，计算摘要。
3. 在 `catalog.json` 的作品条目下添加角色条目，填写 `id`、`name`、`description`、`archive`、`sha256` 和可选 `cover`。
4. 运行本地测试并完成自检，提交 PR。
5. 合并后等待「角色议题同步」工作流建立议题；`community.json` 不需要手动处理。
