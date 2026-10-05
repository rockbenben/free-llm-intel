---
vendor: openrouter
title: GPT 5.6 Discounts & Jevons Paradox
original_title: GPT 5.6 Discounts & Jevons Paradox
url: https://openrouter.ai/blog/insights/gpt-5-6-discounts-jevons-paradox
date: 2026-08-25
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 7a12c323df95
---

# GPT 5.6 Discounts & Jevons Paradox

OpenRouter ·8/25/2026 · Updated 8/27/2026

OpenAI introduced large discounts on their new Terra and Luna models from July 27th through August 14th. What impact did these discounts have on token volumes, total spend, and the competition?

## Highlights

- **Tokens spiked:** Daily Terra token usage rose 5.6x during the discount window, while daily Luna token usage jumped 13.8x. The Sol model, which remained a list price, saw only a gentle bump of 1.1x over the same period.
- **Share was reconfigured:** Most of the share gained by the OpenAI discounts came from other labs as opposed to cannibalization within the OpenAI family of models.
- **Users stuck around:** Nearly a third of users who tried a discounted OpenAI model during the discount window kept using it after the discounts expired.

## Discount impact on token usage

![Indexed daily token usage by model group, showing Terra and Luna spiking during the discount window while Sol and other groups stay near their pre-period levels](https://openrouter.ai/blog/images/gpt-5-6-discounts-token-index.png)

The moment GPT 5.6 discounts kicked in, the token volume exploded.

If you compare the in-program token usage to the pre-period daily averages, the effect is crystal clear: Terra tokens rose 5.6x and Luna 13.8x. The Sol model, which remained un-discounted, saw a minor 1.11x bump while other OpenAI models actually fell slightly in tokens used. Outside the OpenAI family, the other models rose gently.

## Competitive displacement

![Stacked daily token share by model group, with the Terra and Luna band expanding and the pooled competitor band shrinking during the discount window](https://openrouter.ai/blog/images/gpt-5-6-discounts-token-share.png)

Terra/Luna went from 0.7% to 7.8% of all OpenRouter tokens between the pre-period and the program, a gain of 7.1 share points. All competitors are pooled into the light-grey segment, and the label above each color stack is the combined OpenAI-family share (Terra + Luna + Sol + other OpenAI).

Competitors gave up 5.3 points and other OpenAI models gave up 1.9 points over the same comparison, so roughly three quarters of the gain came from outside OpenAI. Across the whole OpenAI family, token share grew from 7.1% to 12.4% and occasionally crested over 15% in specific days during the discount period.

![Daily tokens by model author, with OpenAI volume roughly doubling and holding after the program while Anthropic declines](https://openrouter.ai/blog/images/gpt-5-6-discounts-tokens-by-author.png)

Tokens mostly rose across key model authors, though Anthropic did not in this timeframe. OpenAI token volume nearly doubled on average and has maintained that higher level after the discount program ended.

## Users retention

![Retention of customers who used Terra or Luna during the program, split between those with any post-program usage and those running at or above their program pace](https://openrouter.ai/blog/images/gpt-5-6-discounts-retention.png)

Clearly the discounts drove increased token usage during the program period, but did those users stick around after the discounts had ended?

Of the 100K+ customers with Terra/Luna usage during the program, about 32% retained some usage in the subsequent days and 18% ran at or above their program pace. To be clear, this is a count of customers, not weighted by tokens. Obviously the post-program period is quite a bit shorter than the full discount timeframe (6 days so far vs a 19-day program), so the story may change as more data comes in.

If you look instead at the daily Terra/Luna token volume, the post-program period saw 1.38x the tokens of the discount period on average, which implies the retained accounts are far larger than the median program user.

![Daily Sol token volume staying flat through the Terra and Luna program, then jumping when Sol receives its own 50% discount on August 17](https://openrouter.ai/blog/images/gpt-5-6-discounts-sol-daily.png)

Sol averaged 79.1B tokens/day during the Terra/Luna program against 71.2B/day pre-period, an effectively flat control group.

However, the shaded region in the chart above from Aug 17 onward is Sol’s own 50% discount. Sol jumps immediately, reproducing the Terra/Luna pattern.

## Methodology & Notes

Data Details

- Pre: Jul 8 to Jul 26 | Program: Jul 27 to Aug 14 | Post: Aug 15 to Aug 20
- Jul 30: OpenAI cut its own list prices (Luna 80%, Terra 20%) on top of the 50% discount through OpenRouter. As such, effective discounts from Jul 30 were Luna 90% and Terra 60%.
- Notes: Terra, Luna and Sol all launched Jul 9. Sol is a useful control up until it got its own 50% discount on Aug 17.

Methodology

- Exclusions: banned, deleted, admin, data-deletion-requested, internal and churned accounts are dropped.
- Aug 20 is the last day in the window and may be partial.
- Sol is a valid control only through Aug 16. The post-period is 6 days.
