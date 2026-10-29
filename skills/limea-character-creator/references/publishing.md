# 发布角色卡到角色仓库

角色卡制作完成后，可发布到公开角色仓库 `https://github.com/Playa-0v0/LimeA-Characters`，让 LimeA 角色商店可以拉取。发布通过 Pull Request 进行；仓库的完整规范见其中的 `CONTRIBUTING.md`，以该文件为准。

## 发布前

1. 角色卡已在本地完成并通过格式检查：根目录为 `character.json`，清单声明与实际文件一致，没有未声明文件、临时文件或密钥。
2. 确认授权与隐私：只发布有权使用的文字、图片和音频素材；不包含真实个人信息。
3. 确认角色标识与版本：
   - `id` 使用反向域名式标识，例如 `org.limea.characters.honkai-star-rail.cyrene`，发布后保持不变。
   - 新角色从 `1.0.0` 开始；更新时按语义化版本递增：仅元数据或图片改动递增修订号，提示词或世界书内容改动递增次版本号，改变已有条目运行语义递增主版本号。
   - `name` 最长 80 字符，发布后不要静默改名；确需改名时保留 `id`。
4. 填写作者信息。`author.name` 为显示名，`author.url` 为 `http` 或 `https` 主页地址；商店详情会把作者名链接到该地址，其他协议会被丢弃。

## 仓库结构

```text
catalog.json                      商店清单
community.json                    角色与讨论议题映射（工作流维护，禁止手改）
<作品标识>/
  <角色标识>/
    character.json                角色卡源文件，可编辑
    prompts/                      提示词与台词示例
    worldbook/                    世界书
    assets/                       头像、封面等图片
  <角色标识>.limea                可导入单文件
  <角色标识>-cover.webp           商店封面预览（可选）
```

- 作品目录与角色目录只用于整理；程序身份以 `character.json` 的 `id` 为准。角色目录名应与 `id` 最后一段一致。
- 制作目录、`.limea` 和 `catalog.json` 条目在同一次提交中更新。
- 不要修改其他作者的角色卡，也不要手工修改 `community.json`。

## 操作步骤

1. 同步仓库：

   ```powershell
   git clone https://github.com/Playa-0v0/LimeA-Characters.git
   git -C LimeA-Characters pull --ff-only
   ```

   已有仓库时先拉取最新 `main`，避免摘要或清单冲突。

2. 新建分支：新增角色用 `character/<角色标识>`，修正用 `fix/<角色标识>`。

3. 把角色源文件放入 `<作品标识>/<角色标识>/`，按清单补齐头像、封面等图片。

4. 打包。在角色目录内执行，输出到作品目录：

   ```powershell
   Compress-Archive -Path .\* -DestinationPath ..\<角色标识>.limea -Force
   (Get-FileHash -Algorithm SHA256 ..\<角色标识>.limea).Hash.ToLowerInvariant()
   ```

   压缩包根目录必须直接是 `character.json`，不能多包一层角色目录。`.limea` 是 ZIP 容器，单卡不超过 32 MiB，容器条目不超过 256，解压总量不超过 64 MiB，单文件不超过 16 MiB，单份文本不超过 1 MiB。

5. 需要商店封面时，在作品目录放 `<角色标识>-cover.webp`：静态 WebP、建议 3:4、不超过 1 MiB，并计算其摘要。

6. 更新 `catalog.json` 对应作品的角色数组。新角色补齐全部字段，更新角色只改必要字段：

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

   `archive` 与 `cover.path` 必须位于对应作品目录内；`id`、`name` 必须与 `character.json` 完全一致；`description` 用于列表展示。

7. 自检。仓库测试只覆盖议题同步脚本，不会替你检查角色卡内容，以下项目需逐条确认：

   - 解压 `.limea` 后根目录直接是 `character.json`，内容与制作目录一致。
   - `character.json` 的 `id`、`name` 与 `catalog.json` 一致。
   - `catalog.json` 的 `sha256` 与实际 `.limea` 文件摘要一致，`cover.sha256` 与封面一致。
   - 清单声明的文件全部存在，制作目录没有未声明文件。
   - 世界书条目 `id` 在整张卡唯一；更新时保留已有条目 `id`。
   - 未改动 `community.json` 和其他角色。

   能使用 LimeA 开发环境时，用 `readCharacterArchive` 和 `inspectCharacterFiles` 实际读取压缩包做格式校验；只有实际执行成功才可报告校验通过。随后运行：

   ```powershell
   python -m unittest discover -s tests -p 'test_*.py' -v
   ```

8. 提交。只暂存本次角色相关文件，标题使用 `type(scope): 中文描述`：

   ```powershell
   git add catalog.json "<作品标识>/<角色标识>" "<作品标识>/<角色标识>.limea"
   git commit -m "feat(角色卡): 发布<角色名>角色卡"
   git push -u origin character/<角色标识>
   ```

   `type` 只用 `feat`、`fix`、`refactor`、`perf`、`style`、`docs`、`test`、`chore`、`ci`、`build`、`revert`；描述以动词开头，只说明一件事，不加句号。

9. 创建 PR 并填写仓库模板：变更类型、作品与角色、角色版本、变更内容、自检结果。一个 PR 只处理一个角色。

10. 合并后「角色议题同步」工作流会为缺少映射的角色建立讨论议题，并自动写入 `community.json`。不要在 PR 中预言或手填议题编号；工作流运行前看到 `community.json` 变化属于正常现象。

## 更新已有角色

1. 修改 `<作品标识>/<角色标识>/` 下的源文件，保留 `id` 和世界书条目 `id`。
2. 递增 `version`，重新打包并更新 `catalog.json` 的 `sha256`（封面变化时同步更新 `cover.sha256`）。
3. 按同样流程提交 PR。已发布角色不得更换 `id`；确需弃用旧卡时先和仓库维护者确认处理方式。

## 常见拒绝原因

- 压缩包多包了一层角色目录，或包含未声明文件、符号链接、加密条目、临时文件。
- `catalog.json` 摘要未更新，`id` 或 `name` 与清单不一致。
- 更新时改了 `id`、删改已有世界书条目 `id`，或版本未递增。
- 手工修改 `community.json`，或在一次 PR 中混入多个角色。
- 素材未获授权、包含个人隐私，或试图绕过容量与路径限制。
