---
name: create-vtb
description: Create or update a public-source VTuber/persona skill from Weibo and Bilibili data, with reusable corpus, STT, and repo scaffolding. | 创建或更新一个基于微博/Bilibili 公开内容的 VTuber 人格 skill，包含采集、转写、语料整理和仓库搭建流程。
version: "0.1.0"
user-invocable: true
---

# create-vtb

这是一个面向公开人格蒸馏的元 skill。

适用场景：

- 用户要新建一个 VTuber / VUP / 公开网络人物 `.skill`
- 用户要维护已有角色 skill 的公开数据、语料或 README
- 用户要把单角色 repo 提升成可复用框架

优先读取：

- `docs/PRD.md`
- `references/manifest-schema.md`
- `references/source-playbook.md`
- `references/stt-playbook.md`
- `prompts/intake.md`
- `prompts/public_distillation.md`
- `prompts/repo_builder.md`
- `templates/target.template.json`
- `examples/aza.skill/`

## 工作原则

1. 只使用公开、可复核、允许合理引用的材料。
2. 不编造最新动态、精确原话、时间线和争议结论。
3. 角色感来自多条并行的稳定表达模式，不来自机械堆口癖或单一 running bit。
4. 反复出现的 public motif 可以保留，但只能当可选调味，不能取代整个人格骨架。
5. 优先把流程写成可复用脚本和文档，而不是一次性 prompt。
6. 输出的音频转写文件默认要兼容主流视频制作工具。
7. 默认先由 Codex / Claude Code 自行查公开来源，而不是先要求用户手填 manifest。
8. 如果只能验证到微博或 Bilibili 其中一个来源，就明确告诉用户另一个来源暂缺，并按单信源继续。
9. 如果微博和 Bilibili 都无法验证到稳定官方来源，就不要继续构建 skill。
10. 面向新用户时，默认先给“一条可直接复制给 Codex / Claude Code 的话术”，再给手工命令。

## 标准流程

### Step 1: 明确目标

参考 `prompts/intake.md`，确认：

- 角色是谁
- 目标平台
- 可公开采集的来源
- 想要保留的风格范围
- 明确禁止模仿或推断的边界

默认做法：

- 先自己查 Bilibili 和微博公开入口
- 找到的来源直接写进 manifest
- 找不到的来源留空，并在回复里明确说明“当前未检到稳定官方入口”
- 如果两个都没有，停止构建并把阻断原因告诉用户
- 如果用户只是想开始，默认把用户输入要求压到“角色名 + 可选风格限制”，不要先把人推回手工填表

### Step 2: 写 target manifest

用 `templates/target.template.json` 建一个 `sources/targets/<slug>.json`。

至少要补齐：

- `slug`
- `display_name`
- `canonical_sources`
- `collection_defaults`
- `style_hints`

优先把 `style_hints.key_phrases` 和 `style_hints.motif_phrases` 分开写：

- `key_phrases` 放跨语境稳定成立的高频元素
- `motif_phrases` 放公开来源里存在、但不该进入默认骨架的梗词或自嘲包袱

### Step 3: 跑公开数据采集

优先使用：

- `tools/source_refresh_public.py`
- `tools/collect_bilibili_public.py`
- `tools/collect_weibo_public.py`
- `tools/build_corpus_public.py`

如果微博受访客墙影响，明确说明采集受限，不要假装拿到了数据。
如果只找到一个平台来源，就按单信源继续，不要因为缺微博或缺 Bilibili 而放弃整条流程。

### Step 4: 选择适合 STT 的公开视频

优先选择：

- 自我介绍
- 直播切片
- 杂谈片段
- Q&A / 口播 / 明显说话向投稿

谨慎使用：

- 纯翻唱
- 大量特效处理音频
- 超长录播合集

使用：

- `tools/batch_bilibili_stt.py`
- `tools/audit_transcripts.py`
- `tools/build_training_set.py`
- `tools/build_style_bank.py`

### Step 5: 写角色 skill

一个角色 skill 至少包含：

- `SKILL.md`
- `persona.md`
- `references/profile.md`
- `references/distillation.md`
- `references/expression-dna.md`
- `references/boundaries.md`
- `references/sources.md`

如果已经有稳定 STT 结果，再补：

- `references/style-bank.md`

写 persona 和 references 时，先写 `3-5` 条并行稳定轴，再补“哪些 motif 只在特定语境里偶尔出现”。

### Step 6: 交付前自检

- repo 能说清楚自己是不是框架
- 示例 skill 能独立安装
- README 给出 Codex / Claude Code 的安装说明
- 角色描述没有越过公开来源边界
- 角色描述没有被单一梗词、称呼或自嘲包袱吞掉
- 语音转写输出至少包含 `json/srt/vtt/tsv/txt`

## 输出要求

- 用户要框架时，优先直接写文件和跑脚本，不要只停留在建议层。
- 用户要示范角色时，尽量产出一个可安装的完整示例 skill。
- 用户要发布材料时，优先给出可直接复制的 issue 文案、README 文案或命令。
- 用户要创建新人时，优先给出“直接对 Codex / Claude Code 说什么”的聊天式入口，而不是先让用户手工跑一堆命令。
- 当用户在问“怎么开始”时，优先按“最短可复制 prompt -> 增强版 prompt -> 手工命令”三个层次组织答案。
- 默认把 recurring meme 当配料而不是主菜；通用短输出里通常零次或一次点到就够。
