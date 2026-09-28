---
version: 1
name: free-llm-intel 浏览页设计契约
description: docs/index.html（厂商动态 / 最新变化 / 免费额度与活动一览）的唯一设计面。页面为单文件、无构建、无组件库，设计面就是这份文件里的 CSS 自定义属性。
colors:
  bg: "#ffffff"
  fg: "#1f2328"
  muted: "#656d76"
  line: "#d8dee4"
  card: "#ffffff"
  card-hover: "#f6f8fa"
  accent: "#0969da"
  chip-bg: "#f6f8fa"
  chip-fg: "#424a53"
  chip-active-bg: "#0969da"
  chip-active-fg: "#ffffff"
  warn-bg: "#fff8c5"
  warn-line: "#d4a72c"
  bg-dark: "#0d1117"
  fg-dark: "#e6edf3"
  muted-dark: "#8b949e"
  line-dark: "#30363d"
  accent-dark: "#58a6ff"
  warn-bg-dark: "#2d2410"
  warn-line-dark: "#9e6a03"
typography:
  display-lg:
    fontFamily: 'system-ui + PingFang SC / Microsoft YaHei 兜底'
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: -0.2px
  body-lg:
    fontFamily: '同上'
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: '同上'
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.6
  label-sm:
    fontFamily: '同上'
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
  caption-xs:
    fontFamily: '同上'
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.5
  code-sm:
    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.5
spacing:
  sp-2: 2px
  sp-4: 4px
  sp-5: 5px
  sp-6: 6px
  sp-7: 7px
  sp-8: 8px
  sp-10: 10px
  sp-11: 11px
  sp-12: 12px
  sp-14: 14px
  sp-16: 16px
  sp-18: 18px
  sp-20: 20px
  sp-28: 28px
  sp-32: 32px
  sp-40: 40px
  sp-48: 48px
  sp-60: 60px
rounded:
  control: 6px
  surface: 8px
  pill: 999px
components:
  tab:
    backgroundColor: chip-bg
    textColor: chip-fg
    typography: body-md
    rounded: surface
    padding: 8px 14px
    height: 31px
  tab-selected:
    backgroundColor: bg
    textColor: fg
    typography: body-md
    rounded: surface
    padding: 8px 14px
  chip:
    backgroundColor: chip-bg
    textColor: chip-fg
    typography: label-sm
    rounded: pill
    padding: 5px 10px
  chip-selected:
    backgroundColor: chip-active-bg
    textColor: chip-active-fg
    typography: label-sm
    rounded: pill
    padding: 5px 10px
  button:
    backgroundColor: card
    textColor: fg
    typography: label-sm
    rounded: control
    padding: 5px 12px
  button-primary:
    backgroundColor: chip-active-bg
    textColor: chip-active-fg
    typography: label-sm
    rounded: control
    padding: 5px 12px
  search-field:
    backgroundColor: card
    textColor: fg
    typography: body-md
    rounded: control
    padding: 7px 11px
  card-surface:
    backgroundColor: chip-bg
    textColor: fg
    rounded: surface
    padding: 10px 12px
  warning-surface:
    backgroundColor: warn-bg
    textColor: fg
    rounded: surface
    padding: 14px 16px
---

# DESIGN.md

## Overview

这个仓库的产品是一份机读情报流，人看的界面只有一个文件：`docs/index.html`。
它由 GitHub Pages 直接发布，没有构建步骤、没有组件库、没有 CSS 预处理——
**设计面 = 该文件 `<style>` 里的自定义属性**。改设计就是改变量，不是改样式表。

页面职责是把三种阅读节奏分开：「厂商动态」是长列表（3500+ 条，按时间倒序），
「最新变化」是带日期的事件流，「免费额度与活动一览」是全集快照。
三块共用同一套表面、同一套文字标度，只靠页签与密度区分，不各自造样式。

约束前提，后面所有取舍都由它推出：内容每天由巡检脚本重写，**页面不许硬编码任何数据**；
读者是来查事实的，不是来看排版的，所以信息密度优先于留白；中文正文为主。

## Colors

13 个语义角色 + 暗色同名覆盖，全部走 `:root`，样式里不出现裸 hex。

| 角色 | 用途 | 亮 | 暗 |
| --- | --- | --- | --- |
| `--bg` / `--fg` | 页面底与正文 | `#ffffff` / `#1f2328` | `#0d1117` / `#e6edf3` |
| `--muted` | 次要文字：日期、计数、提示、页脚 | `#656d76` | `#8b949e` |
| `--line` | 一切分隔线与描边 | `#d8dee4` | `#30363d` |
| `--card` / `--card-hover` | 输入框与按钮底 / 行悬停 | `#ffffff` `#f6f8fa` | `#161b22` `#1c2128` |
| `--accent` | 链接、悬停描边、次要按钮文字 | `#0969da` | `#58a6ff` |
| `--chip-bg` / `--chip-fg` | 胶囊与页签的默认态 | `#f6f8fa` `#424a53` | `#21262d` `#c9d1d9` |
| `--chip-active-bg` / `-fg` | 选中态（页签、筛选胶囊、主按钮） | `#0969da` / `#ffffff` | `#1f6feb` / `#ffffff` |
| `--warn-bg` / `--warn-line` | 需要读者留意的行：活动标签、需绑卡、降级告警条 | `#fff8c5` `#d4a72c` | `#2d2410` `#9e6a03` |

配色不表达品牌，只表达状态层级：中性面占绝大多数，`--accent` 只给可点的东西，
`--warn-*` 只给"这条值得停一下"。新增颜色前先问它属于哪个角色。

## Typography

五档整数标度，定义在 `:root` 的 `--fs-*`，样式表里只允许引用变量：

| token | 值 | 用在哪 |
| --- | --- | --- |
| `--fs-xl` | 24px | `h1` |
| `--fs-base` | 15px | body 基准、条目主标题、一览厂商名与**额度正文** |
| `--fs-md` | 14px | 导语、搜索框、页签、一览的**活动行** |
| `--fs-sm` | 13px | 行内次要信息（日期、有效期、最近核查、计数）与控件文字 |
| `--fs-xs` | 12px | 胶囊徽章、等宽 URL/订阅地址、提示段 |

中文最小可读档是 12px，**不再往下**。字体族是系统栈加中文兜底
（`-apple-system … "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei"`），
等宽只用于会被人复制粘贴的字符串。数字一律 `font-variant-numeric: tabular-nums`，
让日期与计数在列表里对齐。

字号**故意不做 `clamp()` 流式缩放**：这页是中文高密度情报流，五档是逐处定过的，
上 clamp 会改掉每一行的渲染像素，而收益只有"自适应"——无法用等像素验证的改动不做。
同理，收敛 `--sp-*` 到 4 的倍数需要一次带视觉验收的独立改动。

## Layout

单列，`.wrap` 最大 880px，左右 16px 内边距；不做多栏，因为条目宽度要留给长标题。

垂直顺序固定：header → 页签（sticky）→ `<main>` 内的三个 pane → footer。
`ul.items` 的行是 `日期 | 正文` 两段 flex，560px 以下转成纵向。
一览行是「名称+分区 → 额度 → 活动 → 元信息」四层，靠字号档位拉开，不靠颜色。

sticky 只留给页签栏：它曾经是整个筛选块（搜索 + 厂商胶囊 + 提示）常驻置顶，
实测占掉 360×740 视口的 39%，把"换视图"这个动作挤到滚动之外。

间距一律取 `--sp-<值>`（2/4/5/6/7/8/10/11/12/14/16/18/20/28/32/40/48/60），
守卫会拒绝 margin/padding/gap 里新出现的裸 px。
**这套值仍是历史形状，不是标度**：5/7/11/14/18/28 都是当年一处一调留下的。
目标形状是 4 的倍数（4/8/12/16/24/32/48），收敛它需要逐处改渲染像素、
再逐屏比对，属于另一次带视觉验收的改动；在此之前，新值只能从既有 token 里挑，
不许再开一个 13px。布局宽度（`.wrap` 880px、日期列 84px、输入框 240px）
与 1px 发丝描边不进这套 token——它们是结构，不是节奏。

## Elevation & Depth

没有阴影、没有 z 轴层次。层级全部由**表面色差 + 1px 描边**表达：
`--card` 浮在 `--bg` 上，`--chip-bg` 是次级面，`--warn-bg` 是提醒面。
唯一的 z-index 是页签栏（6），用来盖住滚动内容。动效只有 `:hover` 的底色与描边变化，
没有位移动画，因此不需要 `prefers-reduced-motion` 分支。

## Shapes

三种圆角，别的不许加：`--rd-control` 6px（按钮、输入框、分段控件）、
`--rd-surface` 8px（卡片、告警条、页签顶角）、`--rd-pill` 999px（胶囊与徽章）。
描边统一 1px `--line`；选中态把描边设为 `transparent`
而不是加粗，避免尺寸跳动。

## Components

胶囊基元：`.pill` 独占 `display / border-radius / border / background / color`，
角色类只写差异——`.chip`（可点筛选）、`.vendor`（行内厂商名）、`.kind`（事件类型）、
`.qpart`（分区标签）、`.qp-tag`（活动标签）。
**新胶囊挂 `.pill` + 一个角色类，不要再抄一遍基元**（守卫会拒绝第二处
`border-radius: var(--rd-pill)`）。
一个坑值得记下来：基元一旦声明 `color`，就接管了原本**继承**来的文字色——
`.qp-tag` 与 `.kind` 是提醒色底、文字跟着所在行走（前者继承 `--fg`，后者继承
`.meta` 的 `--muted`），所以必须显式写回 `color`。这条是像素哈希抓出来的，不是看出来的。

状态口径（各组件按此表取子集，别自造）：

| 状态 | 表达 | 说明 |
| --- | --- | --- |
| default | `--chip-bg` / `--card` 面 + 1px `--line` | 页签、胶囊、按钮、输入框共用 |
| hover | 底色换 `--card-hover`，或描边换 `--accent` | 只做颜色变化，不做位移与缩放 |
| focus-visible | 2px `--accent` 外描边（输入框 `outline-offset: -1px`） | 键盘可达性依赖它，不许用 `outline: none` 抹掉 |
| selected / pressed | `--chip-active-bg` + `--chip-active-fg`，描边转 `transparent` | 由 `aria-selected`（页签）或 `aria-pressed`（胶囊、视图切换）驱动 |
| active（按下） | 与 selected 同色，无额外样式 | 点击即切换视图/筛选，反馈来自结果变化 |
| disabled | 本页面**没有**禁用态 | 控件要么可用要么不渲染，别预留灰态 |
| loading | `.msg` 显示 `data-loading` 文案 | 首次取数前 |
| empty | `.msg` 显示各自的空结果文案 | 必须区别于 loading，见下 |
| error | `.msg.warn` + `--warn-*` 面 | 取数失败或厂商索引缺失 |

- **tab** — 顶角 8px、底边开口，默认 `--chip-bg`，选中态换成 `--bg` + 加粗。
  一组页签在 Tab 键序里只占一站（roving tabindex），左右键互切、Home/End 跳首尾。
- **chip** — 厂商筛选胶囊，`aria-pressed` 驱动选中态；计数尾巴 `.n` 同色，
  过去用 `opacity: .62` 压暗，在选中态上对比度不达标，已去掉。
  `.chip.more` 用虚线描边表示"还能展开更多"，与可筛选的实底胶囊区分。
- **button / button.primary** — 同一控件的两个强度，主按钮复用 `--chip-active-*`。
- **search-field** — `type=search`，焦点态是 2px `--accent` 外描边（`outline-offset: -1px`）。
- **warning-surface** — `.msg.warn`，只在取数失败或索引缺失时出现。
- **msg（三态提示行）** — 一个元素兼当加载中 / 空结果 / 出错，**谁最后画它谁定状态**；
  空结果必须写自己的文案，不许把「加载中…」留在页面上。

## Do's and Don'ts

- **Do** 新增视觉值先落到 `:root` 的既有变量上；确实需要新角色时，同时补亮暗两版。
- **Do** 用 `--fs-*` 控制字号，半像素字号（11.5 / 12.5 / 13.5）已经清过一轮，别再引入。
- **Don't** 用 `opacity` 压暗文字来表达层级——它会在深色底上直接跌破 4.5:1。
- **Don't** 在 HTML 里写 `style="…"`；显隐一律切 `hidden` 属性。
- **Don't** 给正文句子里的链接只靠颜色区分，默认态要有下划线。
- **Don't** 往页面里硬编码厂商清单或条目数据，全部从 `feeds/*.json` 读；
  仓库里有守卫测试钉住这条。
- **Don't** 把 sticky 当成"重要控件就钉住"的手段；常驻 chrome 每多一层，
  手机上可读的正文就少一屏。
