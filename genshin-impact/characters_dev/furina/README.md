# 芙宁娜 · 角色卡说明

- 作品：《原神》；角色：芙宁娜 / Furina；版本：1.2.0；语言：简体中文。
- 编写：OpenAI Codex。非官方角色卡，不代表米哈游或 HoYoverse；不沿用其他贡献者的署名。
- 时间基线：枫丹魔神任务第四章第五幕「罪人舞步旋」与司颂之章第一幕「水的女儿」之后，包含相关剧透。不声称覆盖截至今日全部最新剧情。
- 当前形态：结束水神身份扮演、获得水元素神之眼、探索个人生活与幕后创作。用户不自动等于旅行者，不预设恋爱关系。
- 本版包含高清官方宣传图原文件，不含音频或音色绑定。图片与原作短引依用户明确确认的维护者意见选用，权利仍归原权利人；不宣称具有开放许可。

## 文件分工

固定提示词分为人格核心、表达规则和台词示例。世界书按身份日常、人物关系、阶段经历、枫丹背景及能力分组；只有时间与知识边界常驻，其余按具体关键词触发。所有文件均在 character.json 声明。

## 实际联网研究来源

访问日期：2026-11-03。检索语言：简体中文。本次直接读取下列公开 GitHub 数据文件；它们是社区整理或镜像的游戏文本，不是官方编辑网站。以原作正式游戏内容为最终依据。初次研究时官方 Wiki 与社区 Wiki 页面访问受限；本次补图已实际读取 HoYoWiki 角色数据与 BWIKI 芙宁娜页面，见下方图片来源。

### C：角色基本资料

[genshin-db：芙宁娜角色数据](https://github.com/theBowja/genshin-db/blob/49a6544a6c6ae36089cb42fa591fc46f01de8bcf/src/data/ChineseSimplified/characters/furina.json)

核对姓名、称号、生日10月13日、所属枫丹廷、水元素与司颂座；不根据模型身材字段推断年龄。

### V：中文语音转录

[genshin-db：芙宁娜语音](https://github.com/theBowja/genshin-db/blob/49a6544a6c6ae36089cb42fa591fc46f01de8bcf/src/data/ChineseSimplified/voiceovers/furina.json)

重点核对「关于神之眼」「想要了解芙宁娜·其五」、那维莱特、克洛琳德、娜维娅、夏洛蒂、仆人相关语音，以及日常、饮食和好奇心。它们分别支持重新接纳表演、人格与长期扮演的关系、具体人物态度和生活兴趣。注意部分语音有剧情及好感解锁条件，不把这些认知倒灌为主线早期已经知晓。

本卡逐字收录「闲聊·乐子」与「突破的感受·承」两条简短语音，其余六条为明确标注的原创协作示例。原作短引与原创示例分开标识，不完整复制语音页；未试听音频，不宣称核验了配音表演。

### S：角色故事与神之眼故事

[DimbreathBot/AnimeGameData：故事索引](https://github.com/DimbreathBot/AnimeGameData/blob/bd35e243fa436f141f015cf221a6e19d0c34b7ca/ExcelBinOutput/FetterStoryExcelConfigData.json)

[DimbreathBot/AnimeGameData：中文长文本](https://github.com/DimbreathBot/AnimeGameData/blob/bd35e243fa436f141f015cf221a6e19d0c34b7ca/TextMap/TextMap_MediumCHS.json)

依据 avatarId 10000089 定位 fetterId 89200–89207，以索引中的文本哈希读取，未将哈希缺失当成已经验证：

| 条目 | 本卡采用的事实 |
| --- | --- |
| 89200 角色详细、89201 故事一 | 大明星形象与真实表演造诣 |
| 89202 故事二 | 政务应酬的边界、动物相处与膨膨兽 |
| 89203 故事三 | 舞台细节标准、识破敷衍并更换剧团 |
| 89204 故事四 | 长期扮演的压力、对情绪与身份的迷茫 |
| 89205 故事五 | 搬离沫芒宫、低落、克洛琳德的来访与聚会 |
| 89206 孤心沙龙 | 书中人物、梦与沙龙伙伴的形象来历 |
| 89207 剧情解锁后的神之眼故事 | 柯莉欧、实际获得神之眼、幕后创作方向、学习力量时的失误 |

89207 的剧情解锁正文取 storyContext2TextMapHash=1609744823，对应文本；未解锁的问号标题不作为正文。其余条目采用 storyContextTextMapHash。

### Q：任务中文文本

[同一游戏数据镜像：中文任务及对话文本](https://github.com/DimbreathBot/AnimeGameData/blob/bd35e243fa436f141f015cf221a6e19d0c34b7ca/TextMap/TextMapCHS.json)

仅核对与芙宁娜有关的部分任务概述与对话，包括「水的女儿」邀请、顾问参与、剧团演出，以及将那维莱特面对的芙卡洛斯和旅行者面对的芙宁娜并置的剧情提示。没有完整通读魔神任务所有过场，因此不扩写完整神性计划、神座机制或未经核实的人物内心。

### T：技能文本

[genshin-db：芙宁娜天赋](https://github.com/theBowja/genshin-db/blob/49a6544a6c6ae36089cb42fa591fc46f01de8bcf/src/data/ChineseSimplified/talents/furina.json)

核对孤心沙龙三名成员的名称与形态、荒性和芒性对应的召唤、众水的歌者及万众狂欢的玩法描述；不将玩法数值扩写为剧情全能或现实医疗能力。

## 创作归纳与边界

「戏剧性的自尊与真诚可以并存」「专业要求有实际依据」「关心他人时留有私人边界」是基于故事和语音的写作归纳，不是官方人格诊断。任务拆解、资料查证、现实工具边界与用户关系规则是原创助手适配，不冒充游戏经历。

角色并非只剩水神假面，也不是必须不断求安慰的创伤符号；她可以自信、挑剔、有趣、独立，重新与他人建立关系。没有证据的精确年龄、身高、新恋情、永久治愈或后续剧情不予补写。

## 验证范围

仓库构建、分发文件一致性及现有测试用于验证打包流程；它们不等同于 LimeA 客户端完整导入、模型对话测试或配音试听。本次没有客户端环境，不声称已完成这些应用内验证。


## 高清图片来源与尺寸

访问日期：2026-11-03。所有图片原始字节保留；未插值放大、AI 补画、重绘、去标记或重新压缩原图。这里只报告实际下载文件的像素尺寸，不把它们称作 4K 图片。头像及封面的小尺寸 WebP 由仓库构建脚本生成，与包内原图分别保存。

| 文件 | 下载文件实际尺寸 | 用途与来源 |
| --- | --- | --- |
| assets/avatar.png | 2250×2250 PNG | 深色造型官方宣传图；BWIKI「芙宁娜立绘3.png」原文件，非缩略图 |
| assets/portrait-original.jpg | 1080×2160 JPEG | HoYoWiki Gallery 直接链接的竖版官方宣传图，原署名与标记保留 |
| assets/cover.png | 2250×2250 PNG | 浅色造型官方宣传图；BWIKI「芙宁娜立绘.png」原文件，非缩略图 |

- [BWIKI 芙宁娜页面与立绘区](https://wiki.biligame.com/ys/芙宁娜)
- [头像原文件](https://patchwiki.biligame.com/images/ys/6/6d/i0rv5nmrquh8mk02n0ber08gw7plbch.png)
- [封面原文件](https://patchwiki.biligame.com/images/ys/6/68/gf8q0j490ygvze7w9npx35e49hw6iu0.png)
- [HoYoWiki 芙宁娜 Gallery](https://wiki.hoyolab.com/pc/genshin/entry/4376?lang=en-us)
- [图集原文件](https://upload-static.hoyoverse.com/hoyolab-wiki/2023/09/25/151578876/129c1cc128b848f9e5b45a3649a93ccd_7558186121887964453.jpeg)

HoYoWiki 图片链接通过该页面的 entry_page_id=4376、gallery_character.pic 数据核对。BWIKI 两张图片的页面声明及下载解码均为2250×2250。图片仅用于角色展示，不据此推断当前剧情状态或额外能力。

本次选用官方宣传图与两条简短原作台词，依据维护者在[PR #37 的意见](https://github.com/Playa-0v0/LimeA-Characters/pull/37#issuecomment-6600037715)及用户随后明确确认的要求。该意见支持本次仓库贡献方向，不等于权利人授予开放或商业许可；本卡不作此类声明。
