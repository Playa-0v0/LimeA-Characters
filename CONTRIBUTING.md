# 贡献规范

本仓库维护 LimeA 角色的源文件、正式卡、作品索引和图标。通过 PR（合并请求）贡献，合并到 `main` 后应用读取远程资料；新增作品无需修改 LimeA 的内置图片或作品映射。

## 目录与编辑入口

```text
works.json                            作品标识、名称、图标路径与摘要
icons/<作品标识>.webp                 共享作品图标
<作品标识>/
  characters_dev/<角色标识>/
    character.json                    唯一入口
    prompts/                          固定提示词与对话示例
    worldbook/                        世界书
    assets/                           原始头像、封面等图片
  characters/<角色标识>/
    avatar.webp                       自动生成的头像预览
    cover.webp                        自动生成的封面预览
    <角色标识>.limea                  当前正式角色卡
catalog.json                          自动生成的商店清单
community.json                        工作流维护的角色讨论映射
```

只编辑 `characters_dev` 中的源文件。`characters`、`catalog.json`、首页角色表及图标摘要由构建脚本生成，不要两边手动修改。角色没有某种原图时不会生成对应预览。

作品标识和角色目录名使用小写字母、数字、点、下划线或连字符，首位为字母或数字，最长 128 字符。角色目录名建议与清单 `id` 的最后一段一致；身份以清单为准，不能从名称或目录猜测。

## 新增作品

在 `works.json` 的 `works` 数组登记：

```json
{
  "id": "new-work",
  "name": "新作品",
  "icon": { "path": "icons/new-work.webp" }
}
```

图标为不超过 256 KiB 的静态 WebP（网页图片格式），建议正方形，最多 400 万像素。构建脚本生成 `icon.sha256`。图标可省略，应用显示通用图标。原创世界也可登记独立的稳定标识；暂未归类的本地卡可不声明作品。

应用按索引声明加载图标，按内容摘要缓存到本机；断网复用缓存，未知作品显示通用图标。新增作品只需本仓库的资料与素材，不必提交主程序修改。

## 角色卡声明

格式以 LimeA 主仓库的 `docs/character-card-format.md` 与实际导入校验为准。`format` 固定为 `limea-character`，`formatVersion` 保持 `1`。上架卡必须声明：

```json
"extensions": {
  "limea.work": { "id": "new-work", "name": "新作品" }
}
```

作品标识、名称必须与 `works.json` 及所在作品目录一致。此字段只用于展示，不注入模型。原有 `limea.dialogueExamples` 等扩展照常保留。

- `id` 使用稳定的反向域名式标识，例如 `org.limea.characters.honkai-star-rail.cyrene`；更新不得变更。
- `name` 最长 80 字符；`author.name` 最长 120 字符，`author.url` 使用 `http` 或 `https` 地址。
- `version` 使用 SemVer（语义化版本号）：元数据或图片变动递增修订号，提示词／世界书内容变动递增次版本号，破坏原语义时递增主版本号。
- `prompts.fixed` 按顺序声明固定提示词，`prompts.worldbooks` 声明世界书；不可与 `files` 中旧版提示词用途混用。
- `files` 声明 `avatar`、`cover`、`gallery`、`readme`、`license` 等资源。声明的文件必须存在，制作目录不能有未声明文件。
- 图片支持静态 PNG、JPEG、WebP。头像建议 1:1，封面建议 3:4；原图保留在源文件和角色卡内，外部预览另行压缩。
- 文件路径相对角色根目录，用 `/`，最长 240 字符，禁止绝对路径、`..`、反斜杠、控制字符及仅大小写不同的重复名称。
- 世界书条目 `id` 在整张卡内唯一，更新时保留既有标识；不要因移动目录重写角色身份或条目标识。

容量边界：单卡 32 MiB、容器条目 256、展开总量 64 MiB、单文件 16 MiB、单份文本 1 MiB、封面预览 1 MiB。构建脚本检查文件完整性与生成结果，主程序仍执行完整导入校验。

## 构建与验证

需要 Node.js 24 或更高版本。仓库复用 Sharp（图像处理库）生成预览，复用 yazl（压缩容器写入库）生成稳定安装包，依赖版本由锁文件固定。

在仓库根目录执行：

```sh
npm ci
npm run build
npm test
npm run check
python -m unittest discover -s tests -p 'test_*.py' -v
```

`build` 自动生成正式卡、两种预览、图标摘要、商店清单和首页表格。`check` 在内存中重新生成并逐字节比较，拒绝过期文件；不会改写源文件。CI（持续集成检查）会运行这些测试与校验。

`.limea` 是 ZIP（压缩容器），根目录直接包含 `character.json`，不能多包一层目录。新增／更新时同时提交源目录、正式目录、清单和首页变化。只改作品名称或图标时也要运行构建，确保引用一致；已有角色的作品名称改变需要同步声明并递增角色版本。

## PR 与授权

一个角色贡献只处理该角色，或同一作品的元数据修复；不要修改其他作者的正文。用户明确要求的仓库级迁移可统一调整路径和声明，但必须保留正文、作者与稳定标识。

- 新增角色分支用 `character/<角色标识>`，修正用 `fix/<角色标识>`。
- 标题为单行 `type(scope): 中文描述`，scope 使用作品或角色名，描述以动词开头，不加句号。
- type 限定为 feat、fix、refactor、perf、style、docs、test、chore、ci、build、revert。
- 描述写明作品、角色、版本、改动和实际验证结果。
- 发布有权使用的素材，不包含隐私、密钥、临时文件、编辑器设置或依赖目录。
- `community.json` 由工作流维护，禁止手改。角色标识不变时已有讨论映射会保留，迁移目录不需要新建议题。

合并后工作流负责角色议题映射；不要在 PR 中预言或填写议题编号。清单与旧路径切换发布时先保留旧分发文件度过清单缓存期，再由维护者清理；不修改 Git（版本控制系统）历史。
