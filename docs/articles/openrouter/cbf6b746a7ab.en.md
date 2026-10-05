---
vendor: openrouter
title: OpenRouter Outages on February 17 and 19, 2026
original_title: OpenRouter Outages on February 17 and 19, 2026
url: https://openrouter.ai/blog/announcements/openrouter-outages-on-february-17-and-19-2026
date: 2026-02-20
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 91c68c948795
---

# OpenRouter Outages on February 17 and 19, 2026

OpenRouter Engineering ·2/20/2026 · Updated 6/24/2026

On February 17th and 19th, OpenRouter experienced related outages caused by failures in a third-party caching dependency. A portion of users saw 500 or 401 errors on all API endpoints for 38 minutes starting at 5:27 AM UTC on February 17th, and for 35 minutes starting at 7:36 AM UTC on February 19th. The chatroom was also degraded during these periods.

Any outage of our systems is unacceptable, and we know we let our customers down. We’re sharing these details so you can understand the root cause, how we addressed it, and what we’re doing to prevent it from happening again. While the root cause was a failure in an external dependency, delivering high availability systems with redundancy against failures in our dependencies is our responsibility, not theirs.

## What Happened

OpenRouter relies on an external caching layer for fast API key lookups against our database. Under normal operation, the vast majority of authentication checks are served from this cache, with only a small fraction of requests hitting the database directly.

During both incidents, this caching layer dropped all connections to our database and began returning errors. The initial impact was partial: roughly 20% of requests failed with 500 errors. Within minutes, the cache began to recover and reconnect, but because all cached entries had been invalidated, every incoming request needed a fresh database lookup. Our database was unable to handle this sudden spike in lookup volume, and the resulting timeouts were returned to users as 401 “User not found” errors.

We want to call out the 401 errors specifically. Returning an authentication error for what was actually an infrastructure problem caused real confusion: some customers spent time debugging their own API key configurations when nothing on their side was wrong. That should not have happened, and one of our immediate remediations was to ensure we return accurate error codes when our service is unable to complete authorization lookups.

**Why the second outage happened.** A denial-of-service attack was ramping up at the same time the caching layer failed on February 17th. Because DoS attacks can cause cascading problems across the stack, and because this particular caching dependency has historically been extremely reliable, we initially attributed the outage to the DoS and prioritized hardening our systems against that attack vector. The caching provider also began investigating immediately after the first incident, but diagnosing and fixing the underlying issue took time. When the same caching failure recurred on February 19th without an accompanying DoS, the true root cause became clear. We deployed targeted protections within hours.

## Impact

During the February 17th outage, approximately 20% of API requests failed between 5:27 AM and 5:40 AM UTC, followed by 80-90% failure rates between 5:40 AM and 6:05 AM UTC. The February 19th outage followed a similar pattern, with partial failures between 7:36 AM and 7:42 AM UTC and near-total downtime between 7:42 AM and 8:11 AM UTC.

## Remediations

The following changes have been deployed:

**Circuit breaker mechanisms.** We have implemented circuit breakers that detect caching layer failures and limit their blast radius. These mechanisms also prevent the thundering herd problem that caused the 401 errors: rather than allowing every request to fall through to the database simultaneously when the cache is cold, we now manage cache repopulation in a controlled way. Brief periods of downtime for the caching layer will no longer result in downtime for OpenRouter.

**Accurate error codes.** When our service is unable to complete an authorization lookup due to infrastructure issues, we now return a 503 (service unavailable) rather than a 401. This ensures customers can distinguish between a genuine authentication problem and a transient infrastructure issue.

**Provider-side fixes.** The caching provider has deployed fixes to address the failure mode that caused both incidents.

## What’s Next

A core part of OpenRouter’s promise is reliability. We exist to give you a stable, unified interface to AI inference, including resilience against any individual provider outage. An outage on our own infrastructure undercuts that promise, and we take that seriously. We will soon be rolling out a fallback caching mechanism that will make OpenRouter resilient to even extended downtime in the caching layer.

## Timeline

### February 17 (UTC)

| Time | Status |
| --- | --- |
| 5:20 AM | Caching layer began logging occasional errors with no user-facing impact. |
| 5:27 AM | Cache dropped all database connections and began returning errors. Users started seeing 500 errors. |
| 5:28 AM | Internal alert triggered. Response team online and investigating. |
| 5:40 AM | Cache began to recover, but all cached entries were invalidated. Database unable to handle lookup volume. Users started seeing 401 “User not found” errors. |
| 5:50 AM | We identified a concurrent denial-of-service attack and deployed WAF rules to block it. |
| 6:05 AM | Cache fully repopulated. Service restored. |

### February 19 (UTC)

| Time | Status |
| --- | --- |
| 7:16 AM | Caching layer began logging occasional errors with no user-facing impact. |
| 7:36 AM | Cache dropped all database connections and began returning errors. Users started seeing 500 errors. |
| 7:38 AM | Internal alert triggered. Response team online and investigating. |
| 7:42 AM | Cache began to recover with all entries invalidated. Database unable to handle lookup volume. Users started seeing 401 errors. |
| 8:11 AM | Cache fully repopulated. Service restored. |
