# LimeA 角色仓库

角色按作品目录组织。`catalog.json` 声明商店中的角色卡，`.limea` 是可导入文件，角色文件夹保留可编辑内容。

提交角色卡前请阅读[贡献规范](CONTRIBUTING.md)；使用自动化代理时先阅读 [AGENTS.md](AGENTS.md)。

角色被写入 `catalog.json` 并推送到 `main` 后，GitHub Actions 会为缺少映射的角色建立讨论议题，然后把角色标识和议题编号写入 `community.json`，供 LimeA 读取评论。已有映射会保留；重跑会先查找自动创建的议题，避免中断后重复创建。自动化不会发表评论或删除、关闭议题。每次推送清单都会触发，也可以在 Actions 页面手动运行；定时运行用于恢复临时故障。

发布角色时，将角色卡和更新过的清单一起提交。清单的 `id` 和 `name` 必须与角色卡中的 `character.json` 一致，`sha256` 必须与 `.limea` 文件一致。脚本检查角色卡摘要和基本身份，但完整导入校验仍由 LimeA 负责。映射文件中的既有编号不会自动替换或删除；若出现多个带相同角色标识的自动议题，需要人工核对。

在本机运行自动化测试：

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

工作流依赖 GitHub 提供的 `gh` 命令、Python 标准库以及仓库令牌的 `issues: write` 和 `contents: write` 权限。令牌由 GitHub 自动提供，不需要将个人令牌写入仓库。若分支保护禁止工作流提交，映射写入会失败，可调整仓库权限后手动重跑。
