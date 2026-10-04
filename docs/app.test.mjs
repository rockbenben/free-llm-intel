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

test('vendorList: 同名跨条目合并，feed 取第一个非空', () => {
  const all = [
    { vendor: 'X', vendorId: 'x', feed: '' },
    { vendor: 'X', vendorId: 'x', feed: 'https://f/x.xml' },
  ].map((x) => ({ title: '', link: '', orig: '', date: '', ...x }));
  const list = FLI.vendorList(all, {});
  assert.equal(list.length, 1);
  assert.equal(list[0].feed, 'https://f/x.xml');
  assert.equal(list[0].n, 2);
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

test('visible: 关键词大小写不敏感、匹配标题；厂商筛选按显示名', () => {
  const all = [
    { vendor: 'OpenAI', title: 'GPT-6 Released', link: '', orig: '', date: '' },
    { vendor: 'Anthropic', title: 'Claude update', link: '', orig: '', date: '' },
  ];
  assert.equal(FLI.visible(all, null, 'gpt-6', false, 20).length, 1);
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

test('cacheAgeLabel: <60 分钟报分钟，否则报小时（一位小数）', () => {
  const now = 1_000_000_000_000;
  assert.equal(FLI.cacheAgeLabel(now - 5 * 60000, now), '5 分钟');
  assert.equal(FLI.cacheAgeLabel(now - 59 * 60000, now), '59 分钟');
  assert.equal(FLI.cacheAgeLabel(now - 90 * 60000, now), '1.5 小时');
});
