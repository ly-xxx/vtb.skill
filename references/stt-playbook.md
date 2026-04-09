# STT Playbook

## 目标

把公开视频转写成三类产物：

- 机器可消费：`json`, `tsv`
- 剪辑可直接用：`srt`, `vtt`
- 人工快速浏览：`txt`

## 推荐流程

1. 先用 `batch_bilibili_stt.py` 下载音频并转写
2. 用 `audit_transcripts.py` 给样本打分
3. 用 `build_training_set.py` 导出推荐片段
4. 用 `build_style_bank.py` 提取高质量表达片段

## 选片原则

- 优先人声清晰、说话占比高的视频
- 少量高质量样本比大量低质量录播更有价值
- 大型合集适合作为补充，不适合作为首轮样本

## 输出兼容性

默认输出：

- `json`
- `srt`
- `vtt`
- `tsv`
- `txt`

这样基本兼容常见剪映、PR、达芬奇和字幕整理流程。
