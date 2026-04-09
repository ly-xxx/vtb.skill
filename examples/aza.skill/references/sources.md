# Sources

## 发布版保留的数据

- 目标 manifest：[../sources/targets/aza.json](../sources/targets/aza.json)
- 语料概览：[../sources/processed/corpus/summary.json](../sources/processed/corpus/summary.json)
- 转写审计：[../sources/processed/transcript-audit.json](../sources/processed/transcript-audit.json)
- 训练摘要：[../sources/processed/training/summary.json](../sources/processed/training/summary.json)
- 风格片段库：[style-bank.md](style-bank.md)

当前发布版为了控制仓库体积，不内置：

- raw 抓取 JSON
- 下载媒体
- 完整转写 JSON
- corpus / training JSONL

如果你要继续重跑，下面的命令会在本地重新生成这些文件。

## 已实际跑过的示范命令

```bash
python3 ../../../tools/build_corpus_public.py \
  --target sources/targets/aza.json \
  --raw-dir sources/raw \
  --transcript-dir sources/transcripts \
  --output-dir sources/processed/corpus

python3 ../../../tools/batch_bilibili_stt.py \
  --target sources/targets/aza.json \
  --bvid BV1yJ411Q73u \
  --bvid BV1C4SDB6EqQ \
  --limit 2 \
  --model small \
  --retry-no-vad \
  --force

python3 ../../../tools/audit_transcripts.py \
  --input-dir sources/transcripts \
  --video-details sources/raw/bilibili/video_details.json \
  --output-json sources/processed/transcript-audit.json \
  --output-tsv sources/processed/transcript-audit.tsv
```

## 已确认的公开平台信息

- Bilibili 空间：`https://space.bilibili.com/480680646`
- Bilibili 直播间：`https://live.bilibili.com/21696950`
- 微博主页：`https://www.weibo.com/u/7333181765`
- 微博 handle：`@阿萨AzA`

## 当前这批数据的实际计数

- 微博公开博文抓取：`120` 条
- Bilibili 视频详情：`120` 条
- Bilibili 空间动态：`30` 条
- source corpus：`279` 条
- combined corpus：`412` 条

## 当前限制

- 当前已验证的新动态接口为 `x/polymer/web-dynamic/v1/opus/feed/space`，老接口 `x/polymer/web-dynamic/v1/feed/space` 仍可能返回 `412`
- 口播 STT 样本仍需继续扩充
