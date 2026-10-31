# LimeA 角色仓库

⚠️ LimeA 尚未开发完成，LimeA 角色商店的公开角色卡仓库。每张角色卡包含人格提示词、台词示例和世界书，安装后即可在 LimeA 中使用。

## 收录角色

<h2>
  <img src="icons/崩坏星穹铁道.webp" width="28" alt="崩坏：星穹铁道图标">
  崩坏：星穹铁道
</h2>

<table width="100%">
  <thead>
    <tr>
      <th width="12%" align="center">立绘</th>
      <th width="18%" align="left">角色</th>
      <th width="36%" align="left">角色卡</th>
      <th width="17%" align="left">作者</th>
      <th width="17%" align="left">安装</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><img src="honkai-star-rail/cyrene-cover.webp" width="72" alt="昔涟立绘"></td>
      <td align="left"><strong><a href="honkai-star-rail/cyrene/character.json">昔涟</a></strong></td>
      <td align="left">人格设定、台词示例与世界书</td>
      <td align="left"><a href="https://github.com/Playa-0v0">Playa</a></td>
      <td align="left"><a href="honkai-star-rail/cyrene.limea">下载 .limea</a></td>
    </tr>
  </tbody>
</table>

<h2>
  <img src="icons/崩坏3.webp" width="28" alt="崩坏3图标">
  崩坏3
</h2>

<table width="100%">
  <thead>
    <tr>
      <th width="12%" align="center">立绘</th>
      <th width="18%" align="left">角色</th>
      <th width="36%" align="left">角色卡</th>
      <th width="17%" align="left">作者</th>
      <th width="17%" align="left">安装</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><img src="honkai-impact-3/seele-cover.webp" width="72" alt="希儿·芙乐艾立绘"></td>
      <td align="left"><strong><a href="honkai-impact-3/seele/character.json">希儿·芙乐艾</a></strong></td>
      <td align="left">表里双重人格、台词示例与世界书</td>
      <td align="left"><a href="https://github.com/Bi-Jia">Bi-Jia</a></td>
      <td align="left"><a href="honkai-impact-3/seele.limea">下载 .limea</a></td>
    </tr>
  </tbody>
</table>

列表与 `catalog.json` 保持一致，应用内商店读取的也是这份清单。点击角色名可查看源文件；`.limea` 是可直接分发的单文件角色卡，其摘要记录在清单里。

## 安装

- 应用内：在 LimeA 打开「设置 → 角色商店」，按作品浏览并安装。
- 离线：下载 `.limea` 文件后在 LimeA 中导入，导入入口以当前版本为准。

## 角色制作技能

[skills/limea-character-creator](skills/limea-character-creator/SKILL.md) 是制作与发布角色卡的技能，覆盖人设、台词示例、世界书、音色绑定和发布流程。把该目录加入你所用代理的技能目录即可直接使用，详细规则见 [SKILL.md](skills/limea-character-creator/SKILL.md)。

## 参与贡献

- 提交角色卡前阅读[贡献规范](CONTRIBUTING.md)，其中包含角色卡字段、容量限制、打包与清单更新、PR 要求和评审清单。
- 使用自动化代理时先阅读 [AGENTS.md](AGENTS.md)。
- 新增或更新角色时，把角色源文件、`.limea` 和更新后的 `catalog.json` 放在同一个 PR 里。

## 自动化

角色写入 `catalog.json` 并推送到 `main` 后，GitHub Actions 会为缺少映射的角色建立讨论议题，并把角色标识与议题编号写入 `community.json`，供 LimeA 读取评论。已有映射会保留；重跑会先查找自动创建的议题，避免中断后重复创建。工作流不会发表评论，也不会删除或关闭议题。

`community.json` 由工作流维护，请不要手工修改。清单的 `id`、`name` 必须与角色卡中的 `character.json` 一致，`sha256` 必须与实际 `.limea` 文件一致；完整导入校验仍由 LimeA 负责。

在本机运行自动化测试：

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

工作流依赖 GitHub 提供的 `gh` 命令、Python 标准库以及仓库令牌的 `issues: write` 和 `contents: write` 权限。令牌由 GitHub 自动提供，不需要将个人令牌写入仓库。若分支保护禁止工作流提交，映射写入会失败，可调整仓库权限后手动重跑。
