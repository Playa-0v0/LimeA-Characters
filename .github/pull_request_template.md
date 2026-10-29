## 变更类型

- [ ] 新增角色
- [ ] 更新角色
- [ ] 修复清单或元数据
- [ ] 文档或自动化

## 角色信息

- 作品标识：
- 角色标识：
- 角色版本：

## 变更内容

<!-- 说明新增或修改了什么，为什么需要这次改动。 -->

## 自检

- [ ] `.limea` 与角色制作目录内容一致，根目录直接是 `character.json`
- [ ] `character.json` 的 `id`、`name` 与 `catalog.json` 一致
- [ ] `catalog.json` 的 `sha256` 与实际 `.limea` 文件摘要一致
- [ ] 更新角色保留了 `id` 并递增了 `version`
- [ ] 容量未超过限制，没有临时文件、符号链接或加密条目
- [ ] `python -m unittest discover -s tests -p 'test_*.py' -v` 通过

## 确认

- [ ] 未修改其他作者的角色卡
- [ ] 未手工修改 `community.json`
- [ ] 素材已获授权，不含个人隐私信息
