# Manifest Schema

推荐字段：

```json
{
  "slug": "example",
  "display_name": "示例角色",
  "mode": "public-vtuber",
  "canonical_sources": {
    "weibo": {
      "uid": "",
      "domain": "",
      "url": ""
    },
    "bilibili": {
      "mid": "",
      "space_url": "",
      "room_id": "",
      "short_id": "",
      "live_url": ""
    }
  },
  "collection_defaults": {},
  "style_hints": {
    "aliases": [],
    "self_reference": [],
    "fandom_aliases": [],
    "balance_axes": [],
    "key_phrases": [],
    "motif_phrases": [],
    "story_openers": [],
    "incident_terms": [],
    "reaction_pivots": [],
    "category_rules": {}
  },
  "voice_pipeline": {}
}
```

## 关键字段说明

- `slug`: skill 目录和热词文件命名基础
- `display_name`: 角色展示名
- `canonical_sources`: 平台主来源
- `collection_defaults`: 采集和 STT 默认参数
- `style_hints`: 供语料筛选和风格判断的轻量提示
- `voice_pipeline`: STT 热词与输出格式

### `style_hints` 建议

- `balance_axes`: 用 `3-5` 个短语写出并行稳定轴，提醒维护者不要把人格压成单一梗词
- `key_phrases`: 放跨语境稳定成立的核心元素，保持稀疏、均衡，不要把同一类梗词整桶倒进去
- `motif_phrases`: 放确实存在于公开来源、但只该在特定语境里偶尔出现的 recurring motif；这个字段默认不应该进入搜索词、STT 热词或默认口播骨架
- `self_reference` / `fandom_aliases`: 只放稳定称呼，不要把整句 slogan 或一次性包装语塞进去

### `voice_pipeline.stt_hotwords` 建议

- 优先放名字、团体名、作品名、粉丝名、专有名词
- 不要把所有人设梗、调侃词、自嘲包袱都灌进去
- 如果某个词更像风格 motif 而不是识别刚需，优先留在 `motif_phrases`

## 缺省来源规则

- `canonical_sources.weibo` 可以为空对象或空字段
- `canonical_sources.bilibili` 也可以为空对象或空字段
- 只要微博或 Bilibili 至少有一个来源可验证，就允许继续构建
- 如果两边都无法验证到稳定官方入口，就不要继续构建 skill

## 最低可用要求

如果只想先跑通 Bilibili 管线，最少需要：

- `slug`
- `display_name`
- `canonical_sources.bilibili.mid`
- `style_hints.aliases`
