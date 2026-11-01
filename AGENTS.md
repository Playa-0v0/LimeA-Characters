# AGENTS.md

开始前阅读 `CONTRIBUTING.md`。角色卡格式以 LimeA 主仓库 `docs/character-card-format.md` 和实际导入校验为准。

## 施工约定

- 使用简体中文沟通和写注释，保持当前任务的最小差异。
- 普通贡献一次只处理一个角色；用户明确授权的仓库级迁移可以调整多角色目录与声明，保留正文、作者和稳定标识。
- `community.json` 由工作流维护，禁止手工编辑。
- 不使用未经授权的素材，不写入隐私、密钥、编辑器配置、依赖目录或本地缓存。
- `formatVersion` 保持 `1`，不改变已有角色 `id` 和世界书条目 `id`。

## 目录与作品

- `<作品>/characters_dev/<角色>/` 是唯一编辑源，提示词、世界书和原图在这里维护。
- `<作品>/characters/<角色>/` 是构建产物，包含当前 `.limea` 和存在原图时生成的头像、封面预览。
- 新作品在 `works.json` 登记标识、名称和可选图标路径，图标放 `icons`。禁止为新作品添加主程序硬编码。
- 上架卡通过 `extensions["limea.work"]` 声明 `{id,name}`，必须与作品索引和所在目录一致。
- `character.json` 是唯一入口，文件位置与用途由清单声明。不能依赖文件名、标签或中文别名猜测归属。
- 所有声明文件必须存在，源目录不能有未声明文件；路径与容量规则见贡献规范。

## 修改与验收

1. 修改源文件，递增版本：元数据／图片变动递增修订号，内容变动递增次版本号，破坏语义时递增主版本号。
2. 在根目录运行 `npm ci`，随后 `npm run build`。自动生成分发文件、预览、清单、图标摘要和首页表格，禁止手工维护生成字段。
3. 运行 `npm test`、`npm run check` 和 `python -m unittest discover -s tests -p 'test_*.py' -v`。
4. 确认 `.limea` 根目录直接是 `character.json`，源文件与包内容一致；条件允许时用主程序实际导入验证。
5. 检查 `community.json`、其他作者正文和稳定标识未被改动。只提交当前角色与必要的生成文件，变更说明列明实际验证结果。

提交标题使用单行 `type(scope): 中文描述`。type 限定为 feat、fix、refactor、perf、style、docs、test、chore、ci、build、revert；scope 用作品或角色名；描述以动词开头，只说明一件事，不加句号。
