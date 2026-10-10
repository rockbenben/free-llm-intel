# AGENTS.md — 在本仓库工作的 agent 须知

本仓库是中文 LLM 厂商免费额度情报聚合器（GitHub Pages）。产物由 `crawler_llm_intel.py`
生成，人 + agent 共同维护。**动手前先读 `CONTRIBUTING.md`**（标题翻译、AI 核查通道、
CI 流程的细则都在那）。本文件只放最容易踩、踩了会返工的硬规矩。

## 正文语料翻译：本地一律 agent 精译，MT 只是 CI 的糙覆盖

这是最容易搞反的一条。语料在 `docs/articles/<vendor>/<slug>[.en|].md`，ledger 是
`docs/feeds/bodies.json`，`translator` 字段标明一篇中文是怎么来的：

| 值 | 含义 | 谁产生 |
|---|---|---|
| `agent` | **人工/agent 逐段精译**，质量最高 | **本地** |
| `native` | 源站本身就是中文，无需翻译 | 抓取时自动 |
| `mt` | Google 机器翻译，**糙覆盖**（术语/品牌可能翻坏） | **CI 每日** |
| `llm` | LLM 通道精译（`--ai-bodies`，本地可选） | 本地（可选） |

**规矩：**
- **本地要处理待译正文时，一律由 agent 亲自精译**（写 `.md` 标 `translator: agent`，
  或 `--mark-translated`）。**不要在本地跑 `--mt-bodies` 来"代替"精译**——机翻是
  CI 那条不卡额度、求当日覆盖的路子，不是本地的交付标准。
- CI 分工：每日巡检 `--mt-bodies` 给新文章出机翻中文（`translator=mt`），无 LLM 额度墙、
  长文也能覆盖；`mt` 是临时糙稿，**重点篇之后由本地 agent 重译、覆盖同名 `.md` 升级为
  `agent`**（reconcile 会按 frontmatter 的 translator 更新 ledger）。
- 翻译口径（agent 与 LLM 都遵守）：品牌/模型/产品/术语留英文原样（Claude、GPT、LoRA、
  MCP、token、API、RAG、Hugging Face…，绝不音译）；忠实逐段、不增营销词/总结/漏段；
  保住 markdown 结构，``` 代码块内的代码与 URL **一个字都不动**。
- **页面家具在中文落盘口统一洗**：`fulltext.strip_page_furniture()` 是判据的**唯一正本**，
  三个中文写入口（`--mark-translated`、`--ai-bodies`、CI 的 `--mt-bodies`）与中文原生页落盘
  都过它——只在脚本里洗一次没用，第二天巡检的新稿又会把站件带回正文。
  判据只有两种，绝不猜形状：**整行精确等于**站件闭集标签（`分类`、`标签：`、`分享本文`、
  `下载全部图片`、`相关新闻`、`阅读更多`、`联系销售`、`试用 ChatGPT`、`返回博客`、播放器倍速、
  加载占位…），或**结构块**（带值标签后面的短标签值行；文末带「类别+日期」卡片指纹的推荐区整块）。
  第一条标题之前的导航碎行与头图裸媒体链接也删。
  **``` 代码块内部一个字都不动**；句中出现的同一个词不删（只认独立成行）。
  「延伸阅读/继续阅读」同名标题**没有卡片指纹时按正文保留**——huggingface 用「延伸阅读」放文献清单，
  只认标题词一定会误删。加一条判据就同轮加一格守卫测试（`TestPageFurnitureStrip`）。
  历史正文用同一函数回填，不另写第二套判据。删完 `.md` 的 frontmatter `body_sha` 要重算。
  仍然**不删正文本体**：卡片列表的标题行、TOC、关于作者段落都留着，只删独立成行的站件。

## 批量本地精译的正确做法（>几篇时）

分片交翻译子代理各写若干 `.md`（`translator: agent`），**控制者单点收口**：
`reconcile_translations` 从磁盘吸收译文更新 ledger → `validate_bodies` 过 schema →
提交。**以磁盘为准，不信子代理的"已完成"报告**（报告可能乐观/漏篇/夹英文）：
reconcile 后必查 `pending_translation_keys` 归零、并对每篇新 `.md` 扫 CJK 占比与长度，
把英文漏网/过短挑出来重做。

## 其它硬规矩

- **push 前先问**（用户惯例）；推语料可能触发 GitHub secret-scanning 对抓取正文里
  示例 token 的误报，需要用户在浏览器点 unblock-Allow URL（`gh api` 点前是空的）。
- 抓取/翻译**绝不编造**：抓不到记 `fetch_failed`、正文留空；目录页/链接列表记
  `index_page`——二者都**不进翻译队列**（`pending_translation_keys` 只放行 `en_status==ok`）。
- 改文案/产物要跑门禁：`python test_workflow_and_review.py`（含 CI 实产物 schema 兜底守卫）。
