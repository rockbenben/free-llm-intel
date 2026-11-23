---
version: 2
name: free-llm-intel 浏览页设计契约
description: docs/index.html（厂商动态 / 额度变化 / 免费额度与活动）的唯一设计面。单文件、无构建、无组件库，设计面就是该文件 `<style>` 里的 CSS 自定义属性。
colors:
  bg: "#f6f7f9"
  surface: "#ffffff"
  surface-subtle: "#f1f4f7"
  fg: "#18212b"
  muted: "#556270"
  line: "#e2e7ee"
  line-strong: "#cdd5df"
  card: "#ffffff"
  card-hover: "#f3f6f9"
  accent: "#0f766e"
  accent-hover: "#115e59"
  accent-soft: "#ecfdf5"
  accent-line: "#99d5cc"
  chip-bg: "#eef2f6"
  chip-fg: "#364152"
  chip-active-bg: "#0f766e"
  chip-active-fg: "#ffffff"
  ok-bg: "#ecfdf5"
  ok-fg: "#065f46"
  ok-line: "#a7f3d0"
  info-bg: "#eff6ff"
  info-fg: "#1e40af"
  info-line: "#bfdbfe"
  warn-bg: "#fffbeb"
  warn-fg: "#92400e"
  warn-line: "#f59e0b"
  bg-dark: "#0e1319"
  surface-dark: "#151c24"
  surface-subtle-dark: "#1b242f"
  fg-dark: "#e7edf4"
  muted-dark: "#93a1b2"
  line-dark: "#25303e"
  line-strong-dark: "#334154"
  accent-dark: "#2dd4bf"
  accent-hover-dark: "#5eead4"
  accent-soft-dark: "#122b2b"
  accent-line-dark: "#1f5c58"
  warn-bg-dark: "#2b2110"
  warn-fg-dark: "#fcd34d"
  warn-line-dark: "#a16207"
typography:
  display-xl:
    fontFamily: 'system-ui + PingFang SC / Microsoft YaHei 兜底'
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: -0.2px
  heading-xl:
    fontFamily: '同上'
    fontSize: 22px
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: -0.3px
  heading-lg:
    fontFamily: '同上'
    fontSize: 17px
    fontWeight: 700
    lineHeight: 1.4
  body-base:
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
  sp-6: 6px
  sp-8: 8px
  sp-10: 10px
  sp-12: 12px
  sp-16: 16px
  sp-20: 20px
  sp-24: 24px
  sp-32: 32px
  sp-40: 40px
  sp-48: 48px
rounded:
  control: 8px
  surface: 12px
  pill: 999px
components:
  tab:
    backgroundColor: transparent
    textColor: muted
    typography: body-md
    rounded: control
    padding: 10px 12px
  tab-selected:
    backgroundColor: surface
    textColor: fg
    typography: body-md
    indicator: 2px inset bottom accent
    padding: 10px 12px
  chip:
    backgroundColor: chip-bg
    textColor: chip-fg
    typography: label-sm
    rounded: pill
    padding: 6px 10px
  chip-selected:
    backgroundColor: chip-active-bg
    textColor: chip-active-fg
    typography: label-sm
    rounded: pill
    padding: 6px 10px
  button:
    backgroundColor: card
    textColor: fg
    typography: label-sm
    rounded: control
    padding: 6px 12px
  button-primary:
    backgroundColor: chip-active-bg
    textColor: chip-active-fg
    typography: label-sm
    rounded: control
    padding: 6px 12px
  search-field:
    backgroundColor: card
    textColor: fg
    typography: body-md
    rounded: control
    padding: 8px 12px 8px 32px
  card-surface:
    backgroundColor: surface
    textColor: fg
    rounded: surface
    padding: 16px
  warning-surface:
    backgroundColor: warn-bg
    textColor: fg
    rounded: control
    padding: 8px 10px
---

# DESIGN.md

## Overview

这个仓库的产品是一份机读情报流，人看的界面只有一个文件：`docs/index.html`。
它由 GitHub Pages 直接发布，没有构建步骤、没有组件库、没有 CSS 预处理——
**设计面 = 该文件 `<style>` 里的自定义属性**。

界面气质为**现代编辑情报台**：冷灰白画布（`--bg`）托起纯白内容卡片（`--surface`），深翡翠青（`--accent`）作为唯一交互主色，配合语义状态色（免费绿 `--ok-*`、注册赠金蓝 `--info-*`、活动与绑卡警示琥珀 `--warn-*`）区分信息优先级；支持自动跟随系统与手动一键切换亮暗主题（持久化在 `localStorage` 的 `fli-theme`）。

页面职责将三种阅读节奏分开：「厂商动态」是高密度时间线长列表（4500+ 条，配右侧语言标明的全文档阅读抽屉），「额度变化」按字段突出显示改动片段，「免费额度与活动」是可多维筛选的厂商档案卡集（分区、有免费额度、免绑卡、长期/周期、OpenAI 兼容一键复制）。

约束前提：内容每天由巡检脚本重写，**页面不许硬编码任何数据**；中文正文为主，信息密度优先于装饰性留白。

## Colors

全站颜色走 `:root` 语义变量 + `@media (prefers-color-scheme: dark)` 与 `:root[data-theme="dark"]` 覆盖，样式里不出现裸 hex。

| 角色 | 用途 | 亮 | 暗 |
| --- | --- | --- | --- |
| `--bg` / `--surface` | 画布底与白卡面板底 | `#f6f7f9` / `#ffffff` | `#0e1319` / `#151c24` |
| `--surface-subtle` | 兼容端点块、对比字段、代码块底 | `#f1f4f7` | `#1b242f` |
| `--fg` / `--muted` | 正文主墨色与日期/计数/说明文字 | `#18212b` / `#556270` | `#e7edf4` / `#93a1b2` |
| `--line` / `--line-strong` | 卡片发丝分隔线与控件边框 | `#e2e7ee` / `#cdd5df` | `#25303e` / `#334154` |
| `--card` / `--card-hover` | 按钮/输入框底与列表悬停 | `#ffffff` / `#f3f6f9` | `#151c24` / `#1d2733` |
| `--accent` / `--accent-hover` | 主链接、当前页签指示、动作高亮 | `#0f766e` / `#115e59` | `#2dd4bf` / `#5eead4` |
| `--accent-soft` / `--accent-line` | 「读全文」胶囊与展开按钮激活底/框 | `#ecfdf5` / `#99d5cc` | `#122b2b` / `#1f5c58` |
| `--chip-bg` / `--chip-fg` | 胶囊默认态 | `#eef2f6` / `#364152` | `#1c2530` / `#cbd5e1` |
| `--chip-active-bg` / `-fg` | 选中态（筛选胶囊、分段按钮、主按钮） | `#0f766e` / `#ffffff` | `#0f766e` / `#ffffff` |
| `--ok-*` | 有免费用量 / 免费额度定期刷新 / OpenAI 兼容标签 | `#ecfdf5` / `#065f46` / `#a7f3d0` | `#102a25` / `#6ee7b7` / `#1f5c4d` |
| `--info-*` | 注册赠送 / 一次性额度标签 | `#eff6ff` / `#1e40af` / `#bfdbfe` | `#132238` / `#93c5fd` / `#234674` |
| `--warn-*` | 活动、需绑卡警示、错误告警条 | `#fffbeb` / `#92400e` / `#f59e0b` | `#2b2110` / `#fcd34d` / `#a16207` |

## Typography

七档整数标度，定义在 `:root` 的 `--fs-*`，样式表里只允许引用变量：

| token | 值 | 用在哪 |
| --- | --- | --- |
| `--fs-2xl` | 24px | 阅读器正文 `h1` |
| `--fs-xl` | 22px | 页面报头 `h1` |
| `--fs-lg` | 17px | 阅读器小节标题 `h2` |
| `--fs-base` | 15px | 正文基准、条目主标题、一览厂商名与主额度正文 |
| `--fs-md` | 14px | 导语、搜索框、页签、一览模型列表与活动行 |
| `--fs-sm` | 13px | 日期、计数、控件按钮、差异对比、折叠提示 |
| `--fs-xs` | 12px | 胶囊徽章、等宽 URL/代码片段、提示说明 |

中文最小可读档为 12px，**不再往下**。数字一律 `font-variant-numeric: tabular-nums`，保证日期、计数与页签数字对齐。

## Layout

单列 `.wrap` 最大宽度 960px，左右 16px 内边距。

垂直顺序固定：`header`（紧凑报头 + 可折叠 RSS 面板）→ `nav.tabs`（sticky 置顶页签栏）→ `<main>` 三面板 → `footer`。

- **报头收拢**：RSS 地址与一键复制收进默认折叠的 `#subscribe-panel`，由顶部 `RSS 订阅` 按钮切换；无论收起或展开，顶部 `#subscribe-link` 均同步当前视图或所选厂商单源，且 `header` 不吸顶，保证 `tabsDocTop()` 测算精确与移动首屏内容直达。
- **页签栏**：唯一使用 `position: sticky` 的导航带，小屏单行水平收纳并在 360px 宽度下保持三页签与计数同屏可见。
- **筛选区**：`.controls` 不吸顶，随内容滚动。支持 `/` 快捷键聚焦当前面板搜索框，`Escape` 优先关抽屉、次优收起 RSS 面板。
- **间距标度**：以 4px 为基数收敛为 `--sp-2/4/6/8/10/12/16/20/24/32/40/48`，守卫测试禁止在 `:root` 之外引入裸 px 间距或圆角。
- **触摸目标**：`@media (pointer: coarse)` 下增大按钮、页签与胶囊内边距，桌面端保持紧凑。

## Elevation & Depth

卡片与列表通过**画布与表面色差（`--bg` vs `--surface`）+ 1px 发丝描边**建立层级，列表与卡片不铺投影；仅右滑全屏/780px 阅读抽屉 `.reader-drawer` 使用 `--shadow-drawer` 与 `--backdrop` 区分模态覆盖层。

## Shapes

三种圆角，别的不许加：`--rd-control` 8px（按钮、输入框、分段控件、兼容端点块、差异框）、`--rd-surface` 12px（列表卡、一览厂商卡、订阅面板、告警条）、`--rd-pill` 999px（胶囊与徽章）。

## Components

- **胶囊基元 `.pill`**：全页唯一声明 `border-radius: var(--rd-pill)` 的规则，角色类（`.chip` / `.vendor` / `.read-btn` / `.qpart` / `.qtier` / `.qp-tag` / `.qsignup` / `.kind` / `.diff-field` / `.tab-n` / `.brand-dot`）只写颜色、字号与内边距差异。
- **`[hidden]` 显隐规则**：显式覆盖 `.btn` / `.pill` / `.subscribe` / `.filter-group` / `.reader-orig` 的 `display`，避免自定义 `display: inline-flex` 压过原生 `hidden` 属性。
- **条目行 `.item`**：`日期 | 正文` 两段 flex（640px 以下转纵向）。`.meta` 放可点筛选的 `.vendor` 按钮、单行省略的 `.note.orig` 原文标题、以及固定靠右（`margin-left: auto`）且标注语言可用性（`读全文 · 中/EN` 等）的 `.pill.read-btn`。
- **额度变化 `.diff-row`**：改前、改后上下对齐，缩短共同上下文并高亮变化处。可展开查看字段原值，历史截断的字段标明只保留了片段。超过 2 个变更字段自动折叠进 `.diff-more`。
- **免费额度与活动 `.qrow`**：独立卡片展示，顶部承载分区与免费类型徽章（`有免费用量` / `免费额度定期刷新` / `一次性赠额 / 试用` / `限时免费 / 公测` / `开源自托管`）及右侧官网直达按钮；内联解析 `` `code` `` 与 `**bold**` 富文本节点（纯 DOM 拼接，不拼 HTML）；兼容厂商附带 `base_url` 一键复制框；限制说明默认折叠进 `.qcaveats`。
- **阅读抽屉 `.reader-drawer`**：780px 宽滑出抽屉，内部 `.reader-prose` 限制 `max-width: 68ch` 与 `1.8` 行高，支持头部跳转原文、中/英双语切换与浏览器前进后退同步。

## Do's and Don'ts

- **Do** 新增视觉值先落到 `:root` 变量并同步亮暗两版。
- **Do** 在 `<style>` 中严格避免 `opacity`（改用语义色变量表达层级）和除 `.pill` 之外的 `var(--rd-pill)`。
- **Don't** 在 `docs/index.html` 中出现独立小写厂商 ID（如 `openai` / `modal` 等），防止触发 `test_browse_page_does_not_hardcode_vendors`。
- **Don't** 让 `.controls` 吸顶，或把 `.read-btn` 塞回 `.title` 行。
- **Don't** 往页面里硬编码厂商清单或条目数据，全部从 `feeds/*.json` 读。
