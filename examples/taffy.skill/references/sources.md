# 来源与采集路线

## 一手来源

### 微博

- 官方主页：`https://weibo.com/acetaffy`
- 首选路线：`m.weibo.cn` 官方移动站访客态抓取
- 在 `vtb.skill` 框架内推荐使用：`tools/collect_weibo_public.py`

当前优先策略：

- 先通过 `visitor.passport.weibo.cn` 建立访客 cookie
- 再调用 `m.weibo.cn/api/container/getIndex`
- 评论优先用 `m.weibo.cn/comments/hotflow`

推荐抓取：

- profile
- feeds
- comments
- 置顶微博和近期原创微博

### Bilibili

- 空间：`https://space.bilibili.com/1265680561`
- 直播间：`https://live.bilibili.com/22603245`
- 在 `vtb.skill` 框架内推荐使用：`tools/collect_bilibili_public.py`
- 官方稳定接口：
  - `m.bilibili.com/space/{mid}` 空间初始态
  - `x/web-interface/view/detail` 视频详情
  - `x/v2/reply/main` 热门评论
  - `live_user/v1/Master/info` / `room/v1/Room/get_info`
- 可补充检索：
  - `bilibili-mcp-js`
  - `bilibili-mcp-server`
  - `RSSHub` B 站用户视频 / 动态路由

推荐抓取：

- UP 主资料
- 视频列表
- 视频详情
- 官方动态
- 直播间信息

## 当前内置示例这轮实际计数

- Bilibili 视频详情：`180` 条
- Bilibili 空间动态：`149` 条
- 公开 source corpus：`330` 条

## 发布版保留情况

为了让 `vtb.skill` 更像框架仓库而不是本地缓存快照，当前发布版默认只保留轻量摘要，不内置完整 raw 抓取、下载媒体和转写文件。

如果你要继续做数据刷新和 STT：

- 直接在 `vtb.skill` 根目录重跑框架脚本
- raw 抓取、媒体和转写会在你的本地工作区重新生成
- 采集中断时，新的 `_collector_state.json` 也会在本地重新写出

## 恢复建议

- 如果采集中断，优先重跑 `python3 ../../../tools/source_refresh_public.py --target sources/targets/ace-taffy.json --steps bilibili,corpus`
- 默认保留 `--resume`，让框架继续利用已落盘的中间结果
- 如果想把微博也补进这个内置示例，再跑 `--steps weibo,bilibili,corpus`

## 工具路线

### 微博

- 官方移动站接口：
  - 通过访客态可稳定拿到用户主页、微博流、热门评论
  - 当前环境比 `mcp-server-weibo` 更稳定

- 仓库：`https://github.com/qinyuanpei/mcp-server-weibo`
  - 仍可作为备用路线
  - 当前环境下代理握手不稳定，不再作为主路线

### Bilibili

- 仓库：`https://github.com/34892002/bilibili-mcp-js`
  - 更偏搜索、视频详情、UP 主信息
  - 最近活跃度更好

- 仓库：`https://github.com/huccihuang/bilibili-mcp-server`
  - 能补充精确搜索与弹幕
  - 适合配合使用

## 数据优先级

### P0

- 微博原创正文
- B 站官方视频标题/简介/评论
- B 站官方视频转录

### P1

- B 站官方动态
- 官方直播间标题/公告
- 官方视频评论区高赞互动

### P2

- 授权切片
- 粉丝评论
- RSS 订阅式增量同步

## 在 `vtb.skill` 框架中的建议落桶

- `sources/raw/weibo/`
- `sources/raw/bilibili/`
- `sources/transcripts/`
- `sources/processed/corpus/`

## 说明

这个 `taffy.skill` 目录是内置示例，不是完整独立工具仓库。

如果你只想安装角色本体，当前目录已经够用。
如果你要继续做数据刷新和 STT，请在 `vtb.skill` 根目录执行框架脚本。
