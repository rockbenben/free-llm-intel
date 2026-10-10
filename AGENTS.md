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
- **页面家具在中英两侧落盘口统一洗**：`fulltext.strip_page_furniture()` 是判据的**唯一正本**，
  三个中文写入口（`--mark-translated`、`--ai-bodies`、CI 的 `--mt-bodies`）、中文原生页、
  以及**英文侧落盘**都过它——只在脚本里洗一次没用，第二天巡检的新稿又会把站件带回正文。
  （英文侧此前只洗串级，实测站件残留的大头就在英文侧：`Loading…` 536、`View all` 409、
  `Upvote` 1755 处，所以判据扩到两侧是必须的，不是可选。）
  判据有两种精确度：**行级**——整行等于站件闭集标签（`分类`、`标签：`、`分享本文`、
  `下载全部图片`、`相关新闻`、`阅读更多`、`联系销售`、`试用 ChatGPT`、`返回博客`、播放器倍速、
  加载占位、`Upvote`/`Published`/`Read paper`、`了解更多`/`加入社区`…），或结构块
  （带值标签后面的短标签值行；文末带「类别+日期」卡片指纹的推荐区整块；
  **连续 ≥2 行**的标签筛选链接块 `- [x](…?tags=y)`；只由 `•`/`·`/`/`/不可见字符组成的整行）；
  **串级**——句内的无障碍提示（`⁠（在新窗口中打开）` / `(opens in a new window)`，实测 4290 处）
  按 `[文字](url)` 切开只改文字段；显示文字全是不可见字符的**锚点图标链接**（`## [​](…#节)标题`）
  整条删，但只删 `_droppable_icon_targets` 坐实「删了不减少指向」的三种（同页锚点 / 本文另有出现 /
  本行标题自己的锚点），唯一指向别处的一律留着。第一条标题之前的导航碎行、头图裸媒体链接、
  以及**整行只有本页 host 品牌词的字标**（R8，任意位置）也删。字标这一档的边界是「整行相等」
  而不是「标题之前」：实测标题之后的 741 处全是孤立行（635 处在文末当页脚、106 处前后都空），
  而句子里的品牌词、`## OpenAI`、`| OpenAI |`、`- OpenAI` 都不匹配，删不到正文。比较会剥
  空格与连字符，所以**行首必须是品牌词本身**——否则 `- OpenAI` 的列表符号会被当成字标吃掉
  （实测踩过，靠列表项反向夹具钉住）。
  **``` 代码块内部一个字不动；URL 段与链接外的同名词都不动**（`我们建议在新窗口中打开这个页面`
  这种正常句子必须留着）。不变量按**链接目标多重集**判：`![](x.png)` 这类空 alt 图片整段不动；
  显示文本被提示串占满的链接改写成 `[url](url)`——塌成裸 URL 会让相邻几条黏成 `https://ahttps://b`，
  也没法再查多重集。
  「延伸阅读/继续阅读」同名标题**没有卡片指纹时按正文保留**——huggingface 用「延伸阅读」放文献清单，
  只认标题词一定会误删。加一条判据就同轮加一格守卫测试（`TestPageFurnitureStrip`）。
  历史正文用同一函数回填，不另写第二套判据；回填要带对撞证据（独立实现一遍朴素删除，
  与链接感知版逐行对撞，删掉的 URL 必须逐个等于「被判为可删的图标目标」，其余逐字保全）。
  删完 `.md` 的 frontmatter `body_sha` 要重算；**台账 `body_sha` 跟的是英文侧**，且只同步
  「改前本来就对得上」的行——`mark_translated` 历史不回写它，本就有陈旧值，不借机一并纠。
  仍然**不删正文本体**：卡片列表的标题行、TOC、关于作者段落都留着，只删独立成行的站件。
- **公式与逐字动画在抽取口就该收成一行**：KaTeX/MathJax 的 DOM 是「一个符号一个 `<span>`」，
  `_blocks` 早先把行内容器继续下钻，一个字一段——实测 poolside/modular/minimax 三页
  212/285/389 个单字符行。现在「纯行内容器」整块按 `_inline` 输出一行；公式只留**一份**表示
  （优先 `<annotation encoding="application/x-tex">` 包成 `$TeX$`，拿不到就退化成只读 `<math>`
  子树压一行）——同一公式在 KaTeX 里有三份（MathML 字形 / TeX 源 / `aria-hidden` 的逐字 HTML）。
  两条边界都是踩出来的：公式容器判据**只认 `<math>` 与 `.katex`/`mjx-container`**，写成
  「子树里有 `<math>` 就算」会把整篇正文当一个公式吃掉；分隔符行的字符类**不许含 `|` `-` `_`**，
  否则我们自己生成的 `| --- | --- |` 表格分隔行会被删掉。
  **存量 53 个文件的碎片不做本地「拼接修复」**：实测拼出来的是
  `BingoarbitrarycodeexecutioninModalsandbox!`（空格全丢）与 `123456789`（把 9 个条目并成数），
  比原样更坏；修复只能重抓，而 `zh_status=translated` 的行按规矩永不被重抓冲掉、
  `en_status=ok` 的行 CI 默认也不重抓——所以存量要动就得显式点名重抓。

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
