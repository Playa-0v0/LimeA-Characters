# 角色卡文件和写作

以下格式适用于当前 LimeA 角色卡；若目标版本不同，优先核对该版本的公开格式文档或实际校验规则。保留已有角色卡的清单形式，不因编辑而静默转换旧格式。

## 目录和清单

以下是一个可导入的最小示例。文件名可自定，清单声明决定用途；路径大小写必须与文件一致。

```text
example-character/
├── character.json
├── prompts/
│   ├── soul.md
│   └── dialogue.md
└── worldbook/
    └── world.md
```

> 但是不强制，可以根据不同的角色复杂度有不同的类型的文件

### character.json

```json
{
  "format": "limea-character",
  "formatVersion": 1,
  "id": "example.character",
  "version": "1.0.0",
  "name": "示例角色",
  "description": "一位好奇、可靠的旅伴。",
  "prompts": {
    "fixed": ["prompts/soul.md", "prompts/dialogue.md"],
    "worldbooks": ["worldbook/world.md"]
  },
  "files": [],
  "extensions": {
    "limea.dialogueExamples": ["prompts/dialogue.md"]
  }
}
```

`id` 是稳定角色标识，1–128 位字母、数字、点、下划线或连字符，首位为字母或数字；新角色使用不会与其他角色冲突的标识，更新已有卡时保留原值。`version` 是语义化版本号。固定文件按 `prompts.fixed` 的顺序每轮加载；世界书文件在 `prompts.worldbooks` 中声明。示例文件既在 `fixed` 中，也在 `extensions.limea.dialogueExamples` 中，以便界面识别列表。不要把新格式的 `prompts` 和旧格式 `files` 中的 `system`、`soul`、`voiceExamples`、`worldbook` 或 `fixed` 提示词声明混用。

每个文件只声明一次；已声明文件必须存在，不能带未声明的额外文件。`files` 用于声明可选图片或说明文件：例如 `{"path":"assets/avatar.png","role":"avatar"}`、`{"path":"assets/cover.webp","role":"cover"}` 或 `{"path":"README.md","role":"readme"}`。头像和封面各最多一份；图片支持 PNG、JPEG、WebP。路径为相对路径，用 `/` 分隔；不要使用绝对路径、`..`、反斜杠、控制字符、Windows 保留名称或仅大小写不同的重复路径。正文为 UTF-8 文本，清单为标准 JSON，不使用注释或尾逗号。

## soul.md：固定人设

人设应让角色在协作中能稳定行动：身份和背景、价值取向、性格及相处方式、说话风格、遇到不确定或困难时的行为。事实与创作推断分开，不把尚无依据的细节写成原作设定。保持角色声音，同时说明它以助手身份协作；不要让人设覆盖应用规则、工具权限或当前事实。

### prompts/soul.md

```markdown
# 示例角色 · 人格核心

## 身份与价值

你是示例角色，重视同行者的信任，喜欢探索陌生事物。

## 性格与表达

你温和而好奇，说话自然直接。遇到不确定的事情先说明不知道，再和用户一起查证。

## 与用户协作

认真处理用户交给你的任务；角色经历不能替代实际资料和工具结果。
```

## dialogue.md：台词示例

一条示例由描述和原话构成。描述可以写场景、情绪或表达特点，`/` 是普通文本。每条使用一行粗体列表描述、空行、引用原话；多行原话每行以 `> ` 开头。保持原话准确，示例只用于表达风格参考，不要求照抄。没有可靠原话时可以写自创示例，但应明确标为自创，不冒充原作。

### prompts/dialogue.md

```markdown
- **初次相遇 / 温和问候**

> 「你好呀，接下来的路，我们一起走吧。」

- **遇到困难 / 认真协作**

> 「先别着急，让我和你一起看看。」
```

## world.md：世界书

一个文件可以包含多个独立条目，每个条目用顶层 `## 标题` 开始。条目之间的事实按主题拆分，正文要足以在触发时独立理解。每个条目应提供在整张卡中唯一且稳定的 `id`；修改标题或移动文件时保留它，避免已有会话的激活记录失联。

### worldbook/world.md

```markdown
## 星港

- id: example-star-port
- 触发词: 星港, 港口
- 常驻: 否
- 连带触发词: 飞船
- 内容: 星港是旅人停靠和补给的地方。

  它也是示例角色与同行者相遇的地点。

## 同行约定

- id: example-travel-promise
- 常驻: 是
- 内容: 遇到危险时，示例角色优先照顾同行者。
```

非常驻条目需要触发词，多个词用英文逗号、中文逗号或顿号分隔；常驻字段只用“是”或“否”，省略时为“否”。`连带触发词` 可省略或写 `无`，只触发一跳；正文不能为空。多段 `内容` 后续行缩进两个空格。`内在价值` 和 `优先级` 目前不参与评分、排序或退出，不能暗示设置它们已经生效。

触发以用户被接纳的输入文本做忽略大小写的字面子串匹配，助手输出不触发。条目命中后在会话中保留，重复命中不会重复加入；常驻条目每轮可用。避免过于常见的触发词，以免不相关内容长期进入上下文。

## 打包与检查

按清单检查文件存在、没有多余文件、世界书 `id` 全卡唯一且触发/正文有效。`.limea` 是 ZIP 容器，`character.json` 必须位于容器根目录，不能多包一层角色文件夹；不要把来源笔记、音频、密钥或未声明文件顺手加入。

如果环境已有 Python，可在示例角色目录内用标准库按清单中的相对路径打包（`x` 模式防止覆盖已有文件）：

```text
python -c "from zipfile import ZipFile, ZIP_DEFLATED; paths=['character.json','prompts/soul.md','prompts/dialogue.md','worldbook/world.md']; z=ZipFile('../example-character.limea','x',ZIP_DEFLATED); [z.write(p,p) for p in paths]; z.close()"
```

先检查每个路径存在且目录和文件均不是符号链接，再根据实际清单调整 `paths` 列表。不要使用 `python -m zipfile -c` 逐个传入子目录中的文件：该命令会去掉它们的目录层级。可以用 `python -m zipfile -l ../example-character.limea` 核对容器路径；此检查不等同于 LimeA 的完整导入校验。仓库开发环境可复用 `readCharacterArchive` 和 `inspectCharacterFiles` 做真实格式校验；在安装版中可通过角色管理导入验证，只有实际执行成功才能报告导入成功。没有可用打包或验证工具时交付文件夹并说明限制。
