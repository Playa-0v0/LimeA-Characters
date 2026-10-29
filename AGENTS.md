# AGENTS.md

本文件约束在本仓库工作的编码代理。开始前先读 `CONTRIBUTING.md`；角色卡格式的最终依据是 LimeA 主仓库的 `docs/character-card-format.md`，两者冲突时以主仓库文档和实际导入校验为准。

## 基本约定

- 使用简体中文沟通和写注释。
- 只修改当前任务直接相关的文件，保持最小差异；一次只处理一个角色。
- `community.json` 由 GitHub Actions 维护，禁止手工编辑。
- 不修改其他作者的角色卡，不改动角色卡的格式版本（`formatVersion` 固定为 `1`）。
- 不提交 `__pycache__`、临时压缩包、编辑器配置或本地缓存。
- 不使用未经授权的素材，不写入个人隐私信息。

## 角色卡规则

- `character.json` 是唯一入口，必须位于角色卡根目录；文件位置和用途全部由清单声明，不能依赖文件名。
- `id` 使用反向域名式标识，发布后保持不变。作者改名或更新内容时保留 `id`，只递增 `version`。
- `name` 必须与 `catalog.json` 对应条目完全一致，最长 80 字符。
- `author.url` 只填写 `http` 或 `https` 地址；商店会把作者名链接到该地址。
- 同一张卡不能混用 `prompts` 与旧格式提示词用途。
- 清单声明的文件必须存在；制作目录内不能有未声明的文件。
- 路径使用 `/`，最长 240 字符，禁止 `..`、反斜杠和控制字符。
- 更新角色时保留世界书条目已有 `id`，避免已绑定会话丢失命中。
- 容量上限：角色卡 32 MiB、容器条目 256、解压总量 64 MiB、单文件 16 MiB、单份文本 1 MiB、封面 WebP 1 MiB。

## 改动流程

1. 修改角色制作目录中的源文件。
2. 递增 `version`：仅元数据或图片改动递增修订号，内容改动递增次版本号，破坏已有条目语义时递增主版本号。
3. 重新打包，压缩包根目录必须直接是 `character.json`：

   ```powershell
   Compress-Archive -Path .\* -DestinationPath ..\<角色标识>.limea -Force
   (Get-FileHash -Algorithm SHA256 ..\<角色标识>.limea).Hash.ToLowerInvariant()
   ```

4. 用新摘要更新 `catalog.json` 的 `sha256`；新增角色还要补齐 `id`、`name`、`description`、`archive` 和可选 `cover`。
5. 运行测试：

   ```powershell
   python -m unittest discover -s tests -p 'test_*.py' -v
   ```

## 完成前自检

- `.limea` 内容与制作目录一致，没有多包一层目录。
- `character.json` 的 `id`、`name` 与 `catalog.json` 一致。
- `catalog.json` 的 `sha256` 与实际文件摘要一致。
- 所有声明文件存在，没有未声明文件与临时文件。
- 未修改 `community.json` 和其他角色。
- 变更说明写清作品、角色、新增或更新、自检结果。

## 提交信息

需要提交时使用单行标题：`type(scope): 中文描述`。`type` 只使用 `feat`、`fix`、`refactor`、`perf`、`style`、`docs`、`test`、`chore`、`ci`、`build`、`revert`；`scope` 使用作品或角色名；描述以动词开头，只说明一件事，不加句号。
