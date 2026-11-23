// 浏览页纯逻辑的行为测试。页面是单文件（DESIGN.md 契约），纯逻辑内联在
// index.html 的 <script id="fli-core"> 块里——这里把该块从 HTML 抽出来 eval，
// 真调函数断言返回值，替掉「正则扫源码字符串形状」。块缺失/被加 DOM 依赖都会让
// 抽取或 eval 失败，本测试因此也守住了「核心块存在且无 DOM 依赖」。
// 零依赖：`node --test docs/app.test.mjs`。
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('./index.html', import.meta.url), 'utf8');
const block = html.match(/<script id="fli-core">([\s\S]*?)<\/script>/);
if (!block) {
  throw new Error('index.html 里找不到 <script id="fli-core"> 块（被删了或改了 id？）');
}
// 核心块是纯 JS（无 window/document/self），可安全在 node 里求值。
const FLI = new Function(block[1] + '\n;return FLI;')();

const row = (title, url, vid, date, orig) => [title, url, vid, date, orig];

test('mapRow: 有品牌映射用品牌名，缺映射退回厂商 id，再缺退回未知来源', () => {
  const brands = { anthropic: 'Anthropic Claude' };
  const feeds = { anthropic: 'https://x/anthropic.xml' };
  const a = FLI.mapRow(row('T', 'u', 'anthropic', '2026-01-01', 'Orig'), brands, feeds);
  assert.equal(a.vendor, 'Anthropic Claude');
  assert.equal(a.feed, 'https://x/anthropic.xml');
  assert.equal(a.orig, 'Orig');

  const b = FLI.mapRow(row('T', 'u', 'ghost', '', ''), {}, {});
  assert.equal(b.vendor, 'ghost', '缺品牌映射应退回厂商 id');
  const c = FLI.mapRow(row('T', 'u', '', '', ''), {}, {});
  assert.equal(c.vendor, FLI.UNKNOWN, '连 id 都没有才退回未知来源');
});

test('mapRow: 短行/缺列不抛异常，各字段回退空串', () => {
  const a = FLI.mapRow(['只有标题'], {}, {});
  assert.equal(a.title, '只有标题');
  assert.equal(a.link, '');
  assert.equal(a.date, '');
  assert.equal(a.vendor, FLI.UNKNOWN);
});

test('rankOf: 登记过的用登记名次，未登记/缺索引退回 Infinity（排到最后）', () => {
  assert.equal(FLI.rankOf('a', { a: 3 }), 3);
  assert.equal(FLI.rankOf('z', { a: 3 }), Infinity);
  assert.equal(FLI.rankOf('a', null), Infinity);
});

test('vendorList: rank 优先，其次篇数，末位按名称；rank 相同才比篇数', () => {
  const all = [
    { vendor: 'OpenAI', vendorId: 'oai', feed: '' },
    { vendor: 'OpenAI', vendorId: 'oai', feed: '' },
    { vendor: 'Anthropic', vendorId: 'ant', feed: '' },
    { vendor: 'Zeta', vendorId: 'unranked', feed: '' },
  ].map((x) => ({ title: '', link: '', orig: '', date: '', ...x }));
  const rank = { ant: 1, oai: 2 }; // unranked → Infinity
  const list = FLI.vendorList(all, rank);
  assert.deepEqual(list.map((v) => v.name), ['Anthropic', 'OpenAI', 'Zeta'],
    '旗舰(按 rank) 在前、未登记的 Zeta 垫底');
  assert.equal(list.find((v) => v.name === 'OpenAI').n, 2, '篇数统计正确');
});

test('vendorList: 同 ID 合并，feed 取第一个非空', () => {
  const all = [
    { vendor: 'X', vendorId: 'x', feed: '' },
    { vendor: 'X', vendorId: 'x', feed: 'https://f/x.xml' },
  ].map((x) => ({ title: '', link: '', orig: '', date: '', ...x }));
  const list = FLI.vendorList(all, {});
  assert.equal(list.length, 1);
  assert.equal(list[0].feed, 'https://f/x.xml');
  assert.equal(list[0].n, 2);
});

test('厂商筛选和统计按 ID 区分同名厂商', () => {
  const all = [
    { vendor: '同名', vendorId: 'one', feed: 'one.xml' },
    { vendor: '同名', vendorId: 'two', feed: 'two.xml' },
  ];
  assert.deepEqual(FLI.vendorList(all, {}).map((v) => v.key), ['one', 'two']);
  assert.deepEqual(FLI.visible(all, 'one', '', false, 20), [all[0]]);
});

test('visible: 摘要上限只在「未选厂商且未搜索」时生效', () => {
  const mk = (v) => ({ vendor: v, title: 't', link: '', orig: '', date: '' });
  const all = [];
  for (let i = 0; i < 5; i++) all.push(mk('A'));
  for (let i = 0; i < 5; i++) all.push(mk('B'));

  assert.equal(FLI.visible(all, null, '', true, 3).length, 6, '摘要+全部：每家截到 3');
  assert.equal(FLI.visible(all, null, '', false, 3).length, 10, '非摘要：不截断');
  assert.equal(FLI.visible(all, 'A', '', true, 3).length, 5, '选了厂商：摘要不生效，给全部匹配');
  assert.equal(FLI.visible(all, null, 't', true, 3).length, 10, '搜了关键词：摘要不生效');
});

test('visible: 关键词匹配标题或原文；缺少厂商 ID 时按显示名筛选', () => {
  const all = [
    { vendor: 'OpenAI', title: 'GPT-6 Released', link: '', orig: '', date: '' },
    { vendor: 'Anthropic', title: 'Claude update', link: '', orig: '', date: '' },
    { vendor: 'OpenAI', title: '语音 agent 自动化', link: '', orig: 'Retell uses OpenAI models', date: '' },
  ];
  assert.equal(FLI.visible(all, null, 'gpt-6', false, 20).length, 1);
  assert.equal(FLI.visible(all, null, 'retell uses', false, 20).length, 1,
    '屏上显示的英文原文标题也要能被搜索命中');
  assert.equal(FLI.visible(all, 'Anthropic', '', false, 20).length, 1);
  assert.equal(FLI.visible(all, null, 'zzz', false, 20).length, 0);
});

test('fmtDate: RFC822 → YYYY-MM-DD，空/非法回退空串', () => {
  assert.equal(FLI.fmtDate('Thu, 01 Jan 2026 00:00:00 GMT'), '2026-01-01');
  assert.equal(FLI.fmtDate(''), '');
  assert.equal(FLI.fmtDate('not a date'), '');
});

test('plain: 剥掉 Markdown 强调符', () => {
  assert.equal(FLI.plain('**bold** and `code`'), 'bold and code');
  assert.equal(FLI.plain(null), '');
});

test('asList: 数组原样、字符串包一层、空值给空数组', () => {
  assert.deepEqual(FLI.asList(['a', 'b']), ['a', 'b']);
  assert.deepEqual(FLI.asList('a'), ['a'], '手写档案可能是字符串，渲染与搜索都要能接住');
  assert.deepEqual(FLI.asList(''), []);
  assert.deepEqual(FLI.asList(null), []);
  assert.deepEqual(FLI.asList(undefined), []);
});

test('cacheAgeLabel: <1 分钟不掉进「0 分钟」', () => {
  const now = 1_000_000_000_000;
  assert.equal(FLI.cacheAgeLabel(now, now), '不到 1 分钟');
  assert.equal(FLI.cacheAgeLabel(now - 30_000, now), '不到 1 分钟');
});

test('cacheAgeLabel: <60 分钟报分钟，48 小时内报小时，再久报天', () => {
  const now = 1_000_000_000_000;
  assert.equal(FLI.cacheAgeLabel(now - 5 * 60000, now), '5 分钟');
  assert.equal(FLI.cacheAgeLabel(now - 59 * 60000, now), '59 分钟');
  assert.equal(FLI.cacheAgeLabel(now - 90 * 60000, now), '1.5 小时');
  assert.equal(FLI.cacheAgeLabel(now - 47 * 3600e3, now), '47 小时');
  assert.equal(FLI.cacheAgeLabel(now - 13 * 86400e3, now), '13 天',
    '缓存最长 14 天；报「312 小时」读者没有直观概念');
});

// ---- mdToHtml：与 crawler_llm_intel._md_to_html 对偶 ----
test('mdToHtml: heading + paragraph + list + fenced code', () => {
  const md = '# Title\n\nHello **world**, `code`.\n\n- a\n- b\n\n1. one\n2. two\n\n```\nprint(1)\n```\n';
  const h = FLI.mdToHtml(md);
  assert.match(h, /<h1>Title<\/h1>/);
  assert.match(h, /<strong>world<\/strong>/);
  assert.match(h, /<code>code<\/code>/);
  assert.match(h, /<ul><li>a<\/li><li>b<\/li><\/ul>/);
  assert.match(h, /<ol><li>one<\/li><li>two<\/li><\/ol>/);
  assert.match(h, /<pre><code>print\(1\)<\/code><\/pre>/);
});

test('mdToHtml: pipe 表格', () => {
  const md = '| Model | Score |\n|---|---|\n| A | 1 |\n| B | 2 |\n';
  const h = FLI.mdToHtml(md);
  assert.match(h, /<thead>/);
  assert.match(h, /<th>Model<\/th>/);
  assert.match(h, /<td>A<\/td>/);
  assert.equal((h.match(/<tr>/g) || []).length, 3);
});

test('mdToHtml: 链接与图片', () => {
  const md = 'See [docs](https://x.test/a) and ![alt](https://x.test/p.png).\n';
  const h = FLI.mdToHtml(md);
  assert.match(h, /<a href="https:\/\/x\.test\/a">docs<\/a>/);
  // 属性顺序固定为 src/alt/loading/decoding；懒加载是 2026-11-21 加的（长文图多）
  assert.match(h, /<img src="https:\/\/x\.test\/p\.png" alt="alt" loading="lazy" decoding="async">/);
});

test('mdToHtml: 协议白名单（可执行协议不套标签）', () => {
  // 与 crawler_llm_intel._md_url_safe 对偶：语料是不可信第三方 HTML，
  // javascript:/vbscript:/data:text/html 进 href/src 就是点击即执行的存储型 XSS。
  const h = FLI.mdToHtml('[js](javascript:alert(1)) [JS](JaVaScRiPt:alert(1)) '
                       + '[v](vbscript:msgbox(1)) [d](data:text/html,<b>hi</b>)\n');
  assert.ok(!h.includes('<a '), h);
  assert.ok(!/href="javascript:/i.test(h), h);
  // 丢的是链接形态不是内容：显示文字照留（尾部 `)` 是极简渲染器对带括号目标的一贯形态）
  assert.equal(h.trim(), '<p>js) JS) v) d</p>');
  assert.ok(!FLI.mdToHtml('![x](javascript:alert(1))\n').includes('<img'));
  assert.equal(FLI.mdToHtml('![封面图](javascript:alert)\n').trim(), '<p>封面图</p>');
  // data:image 是语料里真实存在的内联图，img 侧放行
  assert.match(FLI.mdToHtml('![x](data:image/png;base64,AAAA)\n'),
               /<img src="data:image\/png;base64,AAAA"/);
  const ok = FLI.mdToHtml('[a](https://x.test/a) [b](http://x.test/b) [m](mailto:a@x.test) '
                        + '[t](tel:+1) [r](../blog/post) [c](#section)\n');
  assert.equal((ok.match(/<a /g) || []).length, 6, ok);
  // 语料实测：inception_labs 正文里有源站的 about:blank 占位链接 → 只丢链接保文字
  const about = FLI.mdToHtml('[SearchBlox](about:blank) 正在为企业提供搜索。\n');
  assert.ok(!about.includes('<a '), about);
  assert.equal(about.trim(), '<p>SearchBlox 正在为企业提供搜索。</p>');
  // 语料实测的探针行：属性突破本来就不成立，现在也不该出标签
  const probe = FLI.mdToHtml('![](https://cdn-avatars.huggingface.co/v1/a"><img '
                           + 'src=x onerror=window.__av296=1>.png)\n');
  assert.ok(!probe.includes('<img'), probe);
});

test('mdToHtml: HTML escape，不成立即标签；剥危险标签', () => {
  const h = FLI.mdToHtml('Type `<div>` here.\n');
  assert.match(h, /&lt;div&gt;/);
  assert.ok(!h.includes('<div>'));
  // 段落里 raw <script>…</script> 被 escape，只剩字面量；strip 步骤再兜底剥
  const h2 = FLI.mdToHtml('before\n\n<script>alert(1)</script>\n\nafter\n');
  assert.ok(!h2.includes('<script>'));
});

test('mdToHtml: 引用块 + 空输入 + 无 block 元素兜底成段落', () => {
  const bq = FLI.mdToHtml('> hi\n');
  assert.match(bq, /<blockquote>hi<\/blockquote>/);
  assert.equal(FLI.mdToHtml(''), '');
  assert.equal(FLI.mdToHtml(null), '');
});

// ---- reader 抽屉的正文决议（docs/index.html 的 FLI.loadBody / FLI.langFlags）----
// 这里唯一被测的东西是**时序**：另一语言的正文常常根本不存在，旧实现却让两个请求
// 赛跑，那个注定 404 的响应往往比真要读的正文先落地，于是「没有另一种语言」被当成
// 「这篇没有正文」——只有单语正文的行（中文原生页、还没译的英文页）点开就是空白。
const mkFetch = (spec) => {
  const calls = [];
  const fn = (lang) => {
    calls.push(lang);
    const s = spec[lang];
    if (s.throwSync) throw new Error('boom');
    return new Promise((res, rej) => setTimeout(
      () => (s.missing ? rej(new Error('HTTP 404')) : res(s.text)), s.ms || 0));
  };
  return { fn, calls };
};

test('loadBody: 只有中文正文时，另一语言的 404 不许把正文挤掉', async () => {
  const { fn, calls } = mkFetch({ zh: { text: '中文正文', ms: 40 }, en: { missing: true, ms: 5 } });
  const got = await FLI.loadBody('zh', fn);
  assert.deepEqual(got, { lang: 'zh', text: '中文正文' });
  assert.deepEqual(calls, ['zh'], '目标语言读到了就不该再发另一个请求');
});

test('loadBody: 目标语言读不到才回退另一种（未翻译页选中文也能读到原文）', async () => {
  const { fn, calls } = mkFetch({ zh: { missing: true, ms: 5 }, en: { text: 'English', ms: 40 } });
  const got = await FLI.loadBody('zh', fn);
  assert.deepEqual(got, { lang: 'en', text: 'English' }, '回退要成行，不能被先到的 404 带进报错态');
  assert.deepEqual(calls, ['zh', 'en']);
});

test('loadBody: 两种语言都有时不许被更快的另一语言抢走读者选的那门', async () => {
  const { fn } = mkFetch({ zh: { text: '中文正文', ms: 40 }, en: { text: 'English', ms: 5 } });
  const got = await FLI.loadBody('zh', fn);
  assert.equal(got.lang, 'zh', '点的是「中」就显示中文，页签语言不能随响应快慢漂移');
  assert.equal(got.text, '中文正文');
});

test('loadBody: 两种都读不到才 reject（页面据此报错，而不是渲染空抽屉）', async () => {
  const { fn, calls } = mkFetch({ zh: { missing: true }, en: { missing: true } });
  await assert.rejects(() => FLI.loadBody('zh', fn), /HTTP 404/);
  assert.deepEqual(calls, ['zh', 'en']);
});

test('loadBody: fetchText 同步抛异常同样按「这门读不到」回退', async () => {
  const { fn } = mkFetch({ zh: { throwSync: true }, en: { text: 'English' } });
  const got = await FLI.loadBody('zh', fn);
  assert.deepEqual(got, { lang: 'en', text: 'English' });
});

test('langFlags: 索引认识的三种值给出可用性，认不出的一律 null', () => {
  assert.deepEqual(FLI.langFlags('both'), { zh: true, en: true });
  assert.deepEqual(FLI.langFlags('zh'), { zh: true, en: false });
  assert.deepEqual(FLI.langFlags('en'), { zh: false, en: true });
  // '' = 建这一版索引时盘上还没有正文（正文晚索引一步落盘）；undefined = 老索引缺列。
  // 两者都不能当成「这篇读不到」，只能退回真去请求一次。
  assert.equal(FLI.langFlags(''), null);
  assert.equal(FLI.langFlags(undefined), null);
  assert.equal(FLI.langFlags('ZH'), null, '认不出的值不许让页面禁用页签');
});

test('mapRow: langs 取第 8 列，老索引缺列退回空串', () => {
  const r = ['T', 'u', 'v', '2026-01-01', 'O', 'slug12345678', '1', 'zh'];
  assert.equal(FLI.mapRow(r, {}, {}).langs, 'zh');
  assert.equal(FLI.mapRow(r.slice(0, 7), {}, {}).langs, '');
});

test('matchQuotaFilters: 按分区、有免费额度、免绑卡、长期/周期与 OpenAI 兼容筛选', () => {
  const base = {
    part: 1,
    in_guide: true,
    signup: 'phone',
    tiers: ['permanent'],
    openai_compat: { base_url: 'https://api.example.com/v1' },
  };
  assert.equal(FLI.matchQuotaFilters(base, {}), true);
  assert.equal(FLI.matchQuotaFilters(base, { part: 2 }), false);
  assert.equal(FLI.matchQuotaFilters(base, { part: 1 }), true);
  assert.equal(FLI.matchQuotaFilters({ ...base, tiers: [] }, { onlyGuide: true }), false);
  assert.equal(FLI.matchQuotaFilters({ ...base, tiers: ['selfhost'] }, { onlyGuide: true }), false);
  assert.equal(FLI.matchQuotaFilters({ ...base, tiers: ['evaluation'] }, { onlyGuide: true }), true);
  assert.equal(FLI.matchQuotaFilters({ ...base, signup: 'card' }, { noCard: true }), false);
  assert.equal(FLI.matchQuotaFilters({ ...base, signup: 'phone' }, { noCard: true }), true);
  assert.equal(FLI.matchQuotaFilters({ ...base, tiers: ['onetime'] }, { longTerm: true }), false);
  assert.equal(FLI.matchQuotaFilters({ ...base, tiers: ['limited', 'selfhost'] }, { longTerm: true }), false);
  assert.equal(FLI.matchQuotaFilters({ ...base, tiers: ['evaluation'] }, { longTerm: true }), false);
  assert.equal(FLI.matchQuotaFilters({ ...base, tiers: ['recurring'] }, { longTerm: true }), true);
  assert.equal(FLI.matchQuotaFilters({ ...base, openai_compat: null }, { onlyCompat: true }), false);
  assert.equal(FLI.matchQuotaFilters(base, {
    part: 1, onlyGuide: true, noCard: true, longTerm: true, onlyCompat: true,
  }), true);
});

test('parseChangeLines: 多字段拆出中文标签与改前/改后，无箭头时保留原文', () => {
  const labels = { free_models: '免费模型', promotions: '活动' };
  const text = 'free_models：**旧模型** `m1` → **新模型** `m2`\npromotions：仅文字说明\n\nunknown_k：A → B';
  const lines = FLI.parseChangeLines(text, labels);
  assert.equal(lines.length, 3);
  assert.deepEqual(lines[0], {
    key: 'free_models',
    label: '免费模型',
    before: '旧模型 m1',
    after: '新模型 m2',
    raw: '旧模型 m1 → 新模型 m2',
    truncated: false,
  });
  assert.deepEqual(lines[1], {
    key: 'promotions',
    label: '活动',
    before: '',
    after: '',
    raw: '仅文字说明',
  });
  assert.equal(lines[2].label, 'unknown_k');
  assert.equal(lines[2].before, 'A');
  assert.equal(lines[2].after, 'B');
});

test('额度变化：截断后相同的历史值保留截断标记，不生成差异', () => {
  const clipped = '**' + '旧'.repeat(157) + '…';
  const [line] = FLI.parseChangeLines('free_models：' + clipped + ' → ' + clipped);
  assert.equal(line.truncated, true);
  assert.equal(FLI.diffExcerpt(line.before, line.after), null);
});

test('额度变化：隐藏长公共前后文，保留完整金额和有变化的折扣', () => {
  const prefix = '相同的说明'.repeat(40) + ' ，套餐升级限时 ';
  const suffix = ' 元/月；' + '相同的模型权益'.repeat(40);
  const diff = FLI.diffExcerpt(prefix + '5 折，低至 29.5' + suffix,
                               prefix + '7 折，低至 41.3' + suffix);
  assert.equal(diff.before, '5 折，低至 29.5');
  assert.equal(diff.after, '7 折，低至 41.3');
  assert.ok(diff.left.startsWith('…') && diff.right.endsWith('…'));
});

test('额度变化：字段内的箭头不影响改前、改后拆分', () => {
  const [line] = FLI.parseChangeLines('free_models：文字\u00a0→\u00a0图片 → 文字\u00a0→\u00a0视频');
  assert.equal(line.before, '文字 → 图片');
  assert.equal(line.after, '文字 → 视频');
  const [, added, removed] = FLI.parseChangeLines(
    'promotions：—\npromotions： → 首月免费\npromotions：首月免费 → '
  );
  assert.equal(FLI.diffExcerpt(added.before, added.after).after, '首月免费');
  assert.equal(FLI.diffExcerpt(removed.before, removed.after).before, '首月免费');
});

test('richTokens: 安全切分粗体与行内代码，未闭合定界符退回纯文本', () => {
  assert.deepEqual(FLI.richTokens('可用 `glm-4.7-flash` 与 **长期 0 元**'), [
    { type: 'text', value: '可用 ' },
    { type: 'code', value: 'glm-4.7-flash' },
    { type: 'text', value: ' 与 ' },
    { type: 'strong', value: '长期 0 元' },
  ]);
  assert.deepEqual(FLI.richTokens('未闭合 `abc 与 **def'), [
    { type: 'text', value: '未闭合 `abc 与 **def' },
  ]);
});

// ---- 图片密集内容的版式：logo 行 / 图组 / 数据卡（mdToHtml 的 decorateMedia） ----
// 背景：厂商文章常把「一排公司 logo」「一组截图」「logo + 大数字 + 一句说明」压成
// markdown 列表或连续段落，逐条渲染就是一列几百像素高的纵向图片柱。

test('mdToHtml: 整列表都是「链接包图片」→ logo 行', () => {
  const html = FLI.mdToHtml(
    '- [![Kikoff](https://x/k.svg)](https://kikoff.com/)\n' +
    '- [![Campfire](https://x/c.svg)](https://campfire.ai/)');
  assert.match(html, /<ul class="logo-row">/);
  assert.equal((html.match(/<img /g) || []).length, 2);
});

test('mdToHtml: 整列表都是裸图片 → 图组；图文混排保持普通列表', () => {
  const grid = FLI.mdToHtml('- ![](https://x/a.png)\n- ![](https://x/b.png)');
  assert.match(grid, /<ul class="media-grid">/);
  const mixed = FLI.mdToHtml('- ![](https://x/a.png)\n- 说明文字');
  assert.match(mixed, /<ul>/);
  assert.doesNotMatch(mixed, /class="(logo-row|media-grid)"/);
});

test('mdToHtml: 只有一项的图片列表不重排（形状不够明确）', () => {
  const html = FLI.mdToHtml('- ![](https://x/a.png)');
  assert.doesNotMatch(html, /media-grid/);
});

test('mdToHtml: 连续多段只有图 → 图组；单张图仍是普通段落', () => {
  const grid = FLI.mdToHtml('![](https://x/a.png)\n\n![](https://x/b.png)\n');
  assert.match(grid, /<div class="media-grid">/);
  assert.equal((grid.match(/<img /g) || []).length, 2);
  const one = FLI.mdToHtml('![](https://x/a.png)\n');
  assert.match(one, /<p><img /);
  assert.doesNotMatch(one, /media-grid/);
});

test('mdToHtml: 「logo + 数字 + 一句说明」连排两组 → 数据卡', () => {
  const md = [
    '![Campfire](https://x/c.svg)', '', '21', '', 'minutes from Slack mention to open PR', '',
    '![NavigateAI](https://x/n.svg)', '', '134', '', 'pull requests merged from Slack threads', '',
  ].join('\n');
  const html = FLI.mdToHtml(md);
  assert.match(html, /<div class="stat-grid">/);
  assert.equal((html.match(/class="stat-card"/g) || []).length, 2);
  assert.match(html, /class="stat-num">21</);
  assert.match(html, /class="stat-cap">minutes from Slack mention to open PR</);
});

test('mdToHtml: 只有一组「图 + 数字 + 说明」不认数据卡（别把正文拆坏）', () => {
  const html = FLI.mdToHtml('![x](https://x/1.svg)\n\n21\n\nminutes from Slack mention to open PR\n');
  assert.doesNotMatch(html, /stat-grid/);
});

test('mdToHtml: 图片带懒加载属性', () => {
  assert.match(FLI.mdToHtml('![](https://x/a.png)\n'), /loading="lazy"/);
});
