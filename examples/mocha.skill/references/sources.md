# Sources

## 发布版保留的数据

- 目标 manifest：[../sources/targets/mocha.json](../sources/targets/mocha.json)
- 公共语料摘要：[../sources/processed/corpus/summary.json](../sources/processed/corpus/summary.json)
- 转写审计：[../sources/processed/transcript-audit.json](../sources/processed/transcript-audit.json)
- 训练摘要：[../sources/processed/training/summary.json](../sources/processed/training/summary.json)
- 风格片段库：[style-bank.md](style-bank.md)

当前发布版为了控制仓库体积，不内置：

- raw 抓取 JSON
- 下载媒体
- 完整转写 JSON
- corpus / training JSONL

如果你要继续重跑，下面的命令会在本地重新生成这些文件。

## 来源结论

- 已确认稳定 Bilibili 主页：`https://space.bilibili.com/212535360`
- 已确认直播间：`https://live.bilibili.com/21849412`
- 当前未检到稳定官方微博主页，因此 manifest 中微博留空
- 当前公开主页带有 Bilibili 的纪念账号系统提示，因此这版 skill 更偏单信源归档视角，不回答“实时近况”式问题

这条“微博缺失”不是猜测，而是当前构建时的明确缺省状态。

## 当前这批数据的实际计数

- Bilibili 视频详情：`6` 条
- Bilibili 空间动态：`42` 条
- source corpus：`49` 条
- transcript chunks：`30` 条
- combined corpus：`79` 条
- train-ready 片段：`15` 条
- 已审计转写视频：`2` 条，当前均为 `medium`

## 本轮实际执行过的命令

```bash
python3 tools/source_refresh_public.py \
  --target sources/targets/mocha.json \
  --steps weibo,bilibili,corpus

python3 tools/batch_bilibili_stt.py \
  --target sources/targets/mocha.json \
  --bvid BV14f4y1B7yE \
  --bvid BV1ft4y1m7cV \
  --limit 2 \
  --model small \
  --retry-no-vad \
  --force

python3 tools/audit_transcripts.py \
  --input-dir sources/transcripts \
  --video-details sources/raw/bilibili/video_details.json \
  --output-json sources/processed/transcript-audit.json \
  --output-tsv sources/processed/transcript-audit.tsv

python3 tools/build_training_set.py \
  --audit-json sources/processed/transcript-audit.json

python3 tools/build_style_bank.py \
  --target sources/targets/mocha.json \
  --input-jsonl sources/processed/training/transcript_train_ready.jsonl
```
