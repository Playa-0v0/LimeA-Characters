# 发布角色卡到角色仓库

角色仓库为 `https://github.com/Playa-0v0/LimeA-Characters`。完整规范以其中 `CONTRIBUTING.md` 为准，通过 PR（合并请求）发布，禁止手工修改 `community.json`。

## 布局

```text
works.json
icons/<作品标识>.webp
<作品标识>/characters_dev/<角色标识>/
  character.json
  prompts/
  worldbook/
  assets/
<作品标识>/characters/<角色标识>/
  avatar.webp
  cover.webp
  <角色标识>.limea
```

源码目录是唯一编辑入口。正式目录、图标摘要、`catalog.json` 和首页角色表由脚本生成，存在原图时才生成对应预览。

## 操作

1. 同步最新 `main`；有用户改动时在独立工作区施工，不覆盖已有修改。新增分支用 `character/<角色标识>`，修正用 `fix/<角色标识>`。
2. 新作品先登记 `works.json` 的 `{id,name,icon?:{path}}`，可选图标放 `icons`，使用 256 KiB 内的静态 WebP。图标摘要自动计算，不修改主程序作品表。
3. 将原文本与图片放 `<作品>/characters_dev/<角色>/`。角色卡中写入 `extensions["limea.work"]={"id":"作品标识","name":"作品名"}`，与作品索引完全一致；保留其他扩展。
4. 保留已有角色和世界书条目的稳定 `id`。更新时递增 `version`，作者信息真实，素材获得授权。
5. 在仓库根目录运行：

   ```sh
   npm ci
   npm run build
   npm test
   npm run check
   python -m unittest discover -s tests -p 'test_*.py' -v
   ```

   构建生成正式卡、两类预览、摘要、目录和首页；检查会重新生成并比较。主程序的完整导入校验仍是最终格式依据，实际运行后才能报告导入通过。

6. 核对声明文件、版本、容量、身份和摘要。`.limea` 根目录直接包含 `character.json`；不能带未声明文件、链接、临时文件或密钥。`community.json` 不修改。
7. 只暂存该角色的源目录与正式目录，以及必要的作品索引、图标、市场清单和首页变化。标题为单行 `type(scope): 中文描述`，描述以动词开头，不加句号。一个角色贡献只处理该角色。
8. 提交 PR，写明作品、角色、版本、改动和实际自检结果。只有用户授权发布时才推送或创建 PR，不得声称尚未发生的合并或上架。

合并后既有工作流维护讨论映射，角色 `id` 不变就保留原议题。未知作品本机仍可使用并显示通用图标；索引和图标合并后刷新即可显示，不需要应用内置新图片。
