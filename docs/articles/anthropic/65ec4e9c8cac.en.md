---
vendor: anthropic
title: Claude for Financial Advisors | Claude by Anthropic
original_title: Claude for Financial Advisors
url: https://claude.com/resources/articles/claude-for-financial-advisors
date: 2026-10-27
lang: en
captured: 2026-10-28
extractor: readability-v1
status: ok
body_sha: f4c9b5a745b2
---

Today we're releasing Claude for Financial Advisors, a suite of connectors and workflow skills designed to help with research, prep, and documentation tasks that occupy an advisor’s time and keep them from client-facing work.

Time is scarce among financial advisors. A typical advisory practice spends only a sixth of its time in client meetings, according to [Kitces research](https://www.kitces.com/kitces-report-how-financial-planners-actually-do-financial-planning/). The rest goes to work around those meetings, piecing together information across systems to prepare, plan, and

document what was discussed. Meanwhile, over four in 10 American workers say they don't know who to go to for good financial or retirement planning advice, according to [EBRI's 2026 Retirement Confidence Survey](https://www.ebri.org/docs/default-source/rcs/2026-rcs/rcs_26-fs-3_prep.pdf). Time an advisor saves on prep and paperwork can go to a current client or new household they don’t yet have capacity to serve.

Claude for Financial Advisors includes:

- **Connectors, **which let Claude access the custodians, asset managers, and wealth technology providers advisors rely on most, so an advisor can work with a client’s information in one place.
- **Skills, **which use that information to help with specific tasks, like meeting prep, portfolio analysis, and compliance checks, always in service of the advisor's own judgment and style.

## **Connectors to the tools advisors already use**

New connectors bring in the CRM, custodian, portfolio reporting, financial planning software, estate tools, and meeting capture that advisors rely on.

- **Addepar** brings investment intelligence into Claude, giving advisors governed access to portfolio data, analytics and workflows across public and private markets.
- **BlackRock** brings its portfolio construction expertise, model portfolios, and institutional analytics into Claude through Advisor Center, so advisors can deliver holistic advice across public and private markets.
- **CAIS** opens its alternative investment platform to advisors in Claude, so they can query fund data, review manager and fund performance, and see a client's public and private holdings together.
- **Charles Schwab** connects Claude to Schwab Advisor Services custodial data, including balances, positions, transactions, cost basis, alerts, and money-movement status, so advisors can review client information, see which clients need attention, and prepare for reviews.
- **Conquest Planning **brings its Strategic Advice Manager planning engine into Claude so advisors can create new client plans, review and apply strategies, update existing plans and prepare for client meetings all in one place.
- **Envestnet** lets advisors summarize Tamarac accounts and households in natural language, with a financial plan snapshot from MoneyGuide.
- **FactSet **brings multi-asset class content including funds and ETFs, news, company fundamentals, analyst estimates, and market data to Claude, so advisors can research the companies and securities in a client's portfolio.
- **FINNY,** the growth and prospecting platform, connects Claude to an advisor's campaign results by channel and sequence step, and lets advisors enrich prospect lists from their CRM, or upload new lists directly in Claude.
- **Flourish** connects Claude to financial advisors’ books of business, enabling them to work with client information, check rates, manage invitations, and prepare for client meetings, all within Claude.
- **Franklin Templeton** provides publicly approved fund and share-class information in Claude, including performance, fees, NAV, holdings, distributions, and fund documents, along with its published market and investment insights.
- **iCapital **brings a client's alternative investment holdings into Claude, enabling advisors to view NAV, commitments, unfunded capital, recent capital activity, and performance, while more easily connecting those insights to the client's broader portfolio.
- **Invesco** brings portfolio intelligence and practice management insights into Claude through its Invesco for Advisors connector.
- **J.P. Morgan Asset Management (55ip)** extends tax transition technology to Claude, so advisors can evaluate the tax impact of moving a client's holdings into a new portfolio.
- **Jump**, an AI platform for financial professionals, gives Claude client context (meetings, documents, tasks) and Jump-built skills that prepare next steps for the advisor’s review.
- **MSCI** brings its proprietary data and analytics into Claude, so wealth firms can assess investment options across public and private markets, monitor performance, and evaluate rebalancing opportunities.
- **Nevis**, the AI platform for wealth management, draws on client information from meetings, documents, and communications to support meeting prep and follow-up in Claude.
- **Orion** brings portfolio reporting and Redtail CRM insights into Claude for household reviews, opportunity analysis, meeting prep and follow-up*.*
- **SS&C Black Diamond **brings portfolio, performance, holdings and rebalancing data into Claude, so advisors can review their book, spot clients out of tolerance, surface tax loss harvesting opportunities, and generate client reports, tasks and rebalance sessions with their approval.
- **Wealthbox **connects Claude to client records and meeting history to power onboarding, meeting prep, and follow-up.
- **Wealth.com** gives Claude a structured view of each client's estate and tax picture, including trust and will summaries, tax return insights, and the full balance sheet, so advisors can begin planning with an organized summary of available information instead of documents spread across multiple systems.
- **Vanguard **brings information on its model portfolios and advisor investment solutions into Claude, so advisors can draw on Vanguard's trusted research, portfolio construction, and asset allocation expertise when making decisions for clients.
- **Zocks**, the AI meeting assistant for financial advisors, brings Claude the client intelligence it captures from every conversation, including profiles, goals, life events, and commitments.

These join other [connectors](https://claude.com/connectors) already available in Claude, including Microsoft 365, Salesforce, DocuSign, Box, S&P Global, Morningstar, and more.

The Claude for Financial Advisors plugin, which bundles advisor skills and connectors into a single install, works with BlackRock, Charles Schwab, Addepar, Envestnet, iCapital, Orion, Wealthbox, Wealth.com and Zocks, and advisors choose which of these to connect during guided setup. Some partners also offer their own plugins: BlackRock is launching one for Advisor Center, joining existing plugins from S&P Global and LSEG.

## **Skills built around an advisor’s day**

Each skill in the Claude for Financial Advisors plugin supports a specific moment in an advisor's day, from prepping for a client meeting to explaining a drifted portfolio, and routes to tools the firm already uses to run their business. Firms can adopt these skills as is from our Claude for financial advisors [skill repository](https://github.com/anthropics/claude-for-financial-advisors), or adapt them to their own workflows, service model and house style.

- **Advisor onboarding** connects a firm's tools and runs the first meeting prep automatically, helping a new advisor be productive on day one instead of week three.
- **Alternative investments brief** pulls a household's alternative investments from iCapital or Addepar into a meeting-ready summary, shown alongside the rest of the portfolio, instead of an advisor reconciling separate statements by hand.
- **Compliance and AI policy** highlights content that may warrant additional compliance review based on user-configured criteria, assists firms in documenting review workflows, and supports AI-governance documentation processes.
- **Estate and tax brief** checks a client's estate plan against actual account titling and beneficiaries, looks back at the prior year's taxes, and can create CRM follow-up tasks, so mismatches surface for the advisor to review.
- **Portfolio rebalance review** flags drift and concentrated positions against a client's target allocation, and creates a first draft explanation an advisor would otherwise write from scratch.
- **Post-meeting notes and follow-up** turns a transcript into a client summary, a recap email, and CRM tasks in one pass, instead of an advisor doing each by hand after the call.
- **Pre-meeting prep** consolidates information from connected systems (including a client's holdings, recent account activity, and open items from prior meetings) into a single brief for the advisor to review, so they can prepare for and walk in ready for a conversation about that client's specific situation instead of reconstructing context from three systems.
- **Prospect intake** organizes what a prospect shares into a summary, an analyst handoff, and a what-to-expect memo, so the first meeting starts with the basics already in place.

Together, the skills gather information, summarize it, and draft client communications across the advisor’s day. Investment recommendations, client communications, compliance determinations, and other regulated activities remain subject to human review and approval.

## **Built for regulated professionals**

Claude for Financial Advisors is designed so that the advisor stays in control, with approval required on critical tasks. Claude prepares briefs, summaries, and drafts analyses for advisor review, and stages administrative actions like CRM updates or draft client communications for the advisor's review and approval. The compliance skill screens client-facing language against the SEC Marketing Rule to flag potential issues, helps firms document review activities within their existing governance and recordkeeping processes, and includes a self-guided AI-policy workflow that helps firms document their use of AI under SEC rules. Workflow activities can be documented to assist firms in maintaining appropriate records and oversight processes.

## **More households served well**

When Claude handles administrative tasks like meeting prep, follow-up drafts and pipeline review, advisors can spend more of their time serving clients. Practices can expand their customer base, and offer more of the services they need, like tax, estate, insurance, and retirement planning.

Here’s what customers and ecosystem partners have told us about working with Claude:

![zocks](https://assets.claude.com/05a6a0c1132f543d0537102984022c0c90774dde.png)

> “Good financial advice depends on knowing what’s going on in a client’s life, not just what’s in their accounts,” said Mark Gilbert, CEO and Co-founder of Zocks. “The expanded collaboration between Claude and Zocks brings together data and personal client context that used to be fragmented across sources and systems. Now, every task and analysis through Claude is grounded in a more complete understanding of the client. It also gives enterprise firms greater flexibility to build AI workflows around how their advisors actually work.”

Mark Gilbert, CEO and Co-founder

![RFG Advisory](https://assets.claude.com/b85fd6f58a1f1a493b2cc9de09044b6b2164466e.png)

> “MCPs are fundamentally changing how we build technology for advisors. With Claude and Zocks integrated directly into our stack, problems that once required months of configuration and dependence on outside partners can increasingly be solved by our own development team. That gives us the freedom to move faster, work with best-in-class partners, and build around the way advisors actually operate. Instead of asking advisors to adapt to technology, we can make the technology adapt to them.”

Dr. Jordan Hutchison, Vice President of Technology and Operations

![Wealthbox](https://assets.claude.com/31be98f5c18121a5063482dbcb91cd4bb812e9c7.svg)

> “Advisors have spent years building deep client context in Wealthbox. This lets them bring that context straight into Claude and put a frontier model to work on it, such as preparing for meetings, handling follow-up, drafting communications, while everything stays connected to the CRM their practice runs on."”

John Rourke, CEO and Co-Founder

![BlackRock](https://assets.claude.com/d72d42304889c5ecd4f2ba410dfde53b13255b97.svg)

> “Advisors are navigating increasingly complex client needs while facing an accelerating pace of change across markets and technology. Our work with Anthropic is an important step in our broader effort to bring BlackRock’s portfolio intelligence and asset allocation expertise to more advisors to help them scale their business and build better portfolios. By making our institutional-quality portfolio analytics more accessible, we are helping more advisors leverage our portfolio intelligence so they can spend more time focused on client relationships.”

Jaime Magyera, Head of US Wealth & Retirement Businesses

![Mercer Advisors](https://assets.claude.com/e417bbb81bf909eb4ebe19fe0dee25370dbfd28e.svg)

> “Anthropic builds AI aligned with human values. Mercer Advisors builds family offices aligned with client interests. That shared obsession is core to both firms and anchors our partnership. Claude helps our teams to work seamlessly across clients’ financial lives, while judgment and accountability stay with the advisor. That is how AI should work in any profession built on trust.””

Daniel Gourvitch, President

![Rockefeller Capital Management](https://assets.claude.com/70a6a06de8cab56f6dea00611e665aa99e4d17a4.svg)

> “We are pleased to see Anthropic’s continued investment in capabilities tailored to the unique needs of financial advisors. Our collaboration is rooted in a shared belief that technology should support advisors, not replace them, helping them navigate complexity and more efficiently serve clients while keeping human judgment and discretion at the forefront.”

Ashley McCarthy, Chief Operating Officer & Counsel-Managing Director

![Vanguard](https://assets.claude.com/02f6ce25017d80f975786c571ae223b9da5eb42b.svg)

> “Vanguard is committed to helping advisors spend more time with clients and less time navigating complexity. Our integration with Claude expands access to Vanguard investment solutions, freeing up advisors’ time to deliver more personalized service.””

Sid Ratna, Head of Digital and Analytics, Financial Advisor Services

![Charles Schwab](https://assets.claude.com/ee30d9d9145114578de5ae6a8bdbf4d06f6b1848.svg)

> “The future of advisor technology will be defined by how well firms can connect trusted data, powerful intelligence, and everyday workflows. Our collaboration with Anthropic reflects Schwab’s commitment to helping registered investment advisors (RIAs) leverage innovation within the tools they already use, making it easier to serve clients, scale their practices, and grow with confidence."”

Jon Beatty, Head of Schwab Advisor Services

![Ritholtz Wealth Management](https://assets.claude.com/7337a170485b3c8f7db6f39e25cbdb18e35dc6d7.png)

> “AI is already part of the everyday workflow in the advice business. I don’t want my CFPs spending hours every week laboring over CRM updates and task assignments. I want them talking to clients and engaged in the planning itself, because that's the part clients truly value. Claude for Financial Advisors is the first thing I’ve seen that sits on top of the whole stack and does that work across it, with the compliance controls we need built in.”

Josh Brown, CEO

![Ritholtz Wealth Management](https://assets.claude.com/7337a170485b3c8f7db6f39e25cbdb18e35dc6d7.png)

> “Nobody at Ritholtz is going to be replaced by a chatbot. The math on this business is hours, not headcount: an advisor has a finite number of them, and most were going to prep and paperwork instead of the people who actually pay us. Claude for Financial Advisors can move that busy work forward across the systems we already use, with the advisor staying in the loop on anything that reaches the client. That gives us meaningful time back across the firm, so clients get faster responses and more focused attention.”

Michael Batnick, Managing Partner

![Dynasty Financial Partners](https://assets.claude.com/bf0c4721da997cf3b0cabe9b5b57a4df8e3bd702.png)

> “This is the moment the industry stops adapting to AI and starts running on it. The way we see it, Anthropic is the engine, Dynasty is the plane, and the advisor is always the pilot. We build the plane so advisors can fly it, at scale, safely, without ever touching the machinery underneath. The result is, we are not giving advisors another dashboard, we are giving them their time back!””

Shirl Penney, Chief Executive Officer and Founder

![Envestnet](https://assets.claude.com/8cb3d07594ed09df536f166bdacceed33d85eadf.svg)

> “Every hour an advisor spends assembling information is an hour not spent with a client. Bringing Claude together with Tamarac and MoneyGuide means an advisor can understand certain elements of a household or a financial plan in the time it takes to ask.”

Andrew Stavaridis, Chief Relationship Officer

![iCapital](https://assets.claude.com/8d7d47070da0c183b9e93c94a2ddb4cf3237318b.svg)

> “As private markets become a larger part of client portfolios, advisors need easier ways to navigate complexity. iCapital combines a comprehensive marketplace with the data and infrastructure to manage specialized investments, and connecting that data through Claude helps turn investment intelligence into actionable insights.”

Gary Gallagher, President

![SS&C](https://assets.claude.com/eeae4806401748e5b724e60461e592ce2ba81204.svg)

> “AI is most effective for advisors when it works with the data and systems they already use. Connecting Claude with SS&C Black Diamond Wealth Solutions allows advisors to bring client and portfolio information into their workflows, reducing preparation time and ensuring they remain in Control.”

Steve Leivent, Senior VP & Co-Head

![Addepar](https://assets.claude.com/fb76688c14d76e8ecea2860238c3074e4bf75a4e.svg)

> “Addepar has built the data and intelligence foundation that the world’s leading investment professionals rely on to manage nearly $10 trillion in assets, with the governance, rigor and controls built natively into our platform. Addepar’s collaboration with Anthropic brings our uniquely deep understanding of sophisticated investment portfolios into Claude, giving clients access to Addepar’s industry-leading portfolio intelligence wherever they work.”

Eric Poirier, CEO

![Wealth.com](https://assets.claude.com/7d2f8c61095816e9f787e52e70f871b8d7ebdfe8.svg)

> “Estate and tax are the layers of a client’s plan that have to be exact. Advisors already trust Wealth.com as the system of record for the estate and tax positions their clients actually have. Inside Claude, that record can answer questions directly, with every figure tracing back to the source document that produced it.”

Rafael Loureiro, CEO

![Salesforce](https://assets.claude.com/122680b4a90e354a227934e7b37b3cd62b0cc11f.svg)

> “Advisors do their best work with the full picture of a client in front of them. Connecting Salesforce to Claude lets the relationships firms have built on our platform travel with the advisor, within the permissions and controls they already have in place. Together with Anthropic we're giving firms more ways to put that trusted client data to work for the people they serve.”

Eran Agrios, SVP & GM, Financial Services

![Orion](https://assets.claude.com/43c094e940d801886608b78e8b4ad48d4852dd04.svg)

> “Clients never see the work behind a good meeting, but they feel it when it’s missing. Through our collaboration with Anthropic, Orion’s plugin for Claude for Financial Advisors brings a firm’s portfolio and CRM data into meeting prep, follow-up drafts and pipeline review, all within the firm’s existing permissions and controls. The technology handles more of the preparation in the background so the advisor can stay focused on the client and the conversation. Advisors walk in prepared, without spending hours pulling everything together.”

Reed Colley, President

![zocks](https://assets.claude.com/05a6a0c1132f543d0537102984022c0c90774dde.png)

> “Good financial advice depends on knowing what’s going on in a client’s life, not just what’s in their accounts,” said Mark Gilbert, CEO and Co-founder of Zocks. “The expanded collaboration between Claude and Zocks brings together data and personal client context that used to be fragmented across sources and systems. Now, every task and analysis through Claude is grounded in a more complete understanding of the client. It also gives enterprise firms greater flexibility to build AI workflows around how their advisors actually work.”

Mark Gilbert, CEO and Co-founder

![RFG Advisory](https://assets.claude.com/b85fd6f58a1f1a493b2cc9de09044b6b2164466e.png)

> “MCPs are fundamentally changing how we build technology for advisors. With Claude and Zocks integrated directly into our stack, problems that once required months of configuration and dependence on outside partners can increasingly be solved by our own development team. That gives us the freedom to move faster, work with best-in-class partners, and build around the way advisors actually operate. Instead of asking advisors to adapt to technology, we can make the technology adapt to them.”

Dr. Jordan Hutchison, Vice President of Technology and Operations

![Wealthbox](https://assets.claude.com/31be98f5c18121a5063482dbcb91cd4bb812e9c7.svg)

> “Advisors have spent years building deep client context in Wealthbox. This lets them bring that context straight into Claude and put a frontier model to work on it, such as preparing for meetings, handling follow-up, drafting communications, while everything stays connected to the CRM their practice runs on."”

John Rourke, CEO and Co-Founder

![BlackRock](https://assets.claude.com/d72d42304889c5ecd4f2ba410dfde53b13255b97.svg)

> “Advisors are navigating increasingly complex client needs while facing an accelerating pace of change across markets and technology. Our work with Anthropic is an important step in our broader effort to bring BlackRock’s portfolio intelligence and asset allocation expertise to more advisors to help them scale their business and build better portfolios. By making our institutional-quality portfolio analytics more accessible, we are helping more advisors leverage our portfolio intelligence so they can spend more time focused on client relationships.”

Jaime Magyera, Head of US Wealth & Retirement Businesses

![Mercer Advisors](https://assets.claude.com/e417bbb81bf909eb4ebe19fe0dee25370dbfd28e.svg)

> “Anthropic builds AI aligned with human values. Mercer Advisors builds family offices aligned with client interests. That shared obsession is core to both firms and anchors our partnership. Claude helps our teams to work seamlessly across clients’ financial lives, while judgment and accountability stay with the advisor. That is how AI should work in any profession built on trust.””

Daniel Gourvitch, President

![Rockefeller Capital Management](https://assets.claude.com/70a6a06de8cab56f6dea00611e665aa99e4d17a4.svg)

> “We are pleased to see Anthropic’s continued investment in capabilities tailored to the unique needs of financial advisors. Our collaboration is rooted in a shared belief that technology should support advisors, not replace them, helping them navigate complexity and more efficiently serve clients while keeping human judgment and discretion at the forefront.”

Ashley McCarthy, Chief Operating Officer & Counsel-Managing Director

1/18

## **Getting started**

The advisor plugin is available today. We recommend Enterprise plans for registered investment advisers, because it includes the audit logs that support recordkeeping. If you already have an Enterprise license, open Cowork and find "Claude for Financial Advisors" in the plugin browser, and install it and follow the guided setup to connect your tools (or install from the [marketplace here](http://github.com/anthropics/claude-for-financial-advisors)).

If you don't have an Enterprise license, request one using this [form](https://forms.gle/y9YmFF2j4moRinJA7) and an Anthropic team member will reach out with next steps. Firms that request a new license before the end of September 2026 will also receive a one-time usage credit to help them get started with the plugin.

Learn more [at our solutions page](https://claude.com/solutions/financial-services#financial-advisors) and join [our webinar](https://claude.com/resources/webinars/inside-claude-for-financial-advisors) this Friday 9/18 at 11AM ET.

*This article was originally published on September 14, 2026. It has been updated to include additional connectors from Anthropic partners.*

Article

Oct 26, 2026

### Expanding Claude for Nonprofits

Our new Claude for Nonprofits plugin brings new skills to every verified nonprofit organization, taking on the operational work that stretches small teams across fundraising, marketing, and hiring.

Article

Oct 23, 2026

### Claude Cowork and chat come together for Enterprise

Claude Enterprise

Article

Oct 23, 2026

### Claude Duet Safety, Privacy, and Security

Claude Duet is a proactive agent that works for you, even while you’re away. It builds on two layers of protection: safety training in the Claude model itself and the safeguards that exist in products like Claude Code and Claude Managed Agents. On top of those, we added new protections for working across your accounts and acting on your behalf.

Article

Oct 22, 2026

### The full Claude Platform, available on Google Cloud

Use Claude Models on Google Cloud (Anthropic managed) to access Claude Platform features with Google Cloud authentication, billing, and commitment retirement.

Claude Platform

## Transform how your organization operates with Claude

[See pricing](https://claude.com/pricing#api)[Contact sales](https://claude.com/contact-sales)

### Get the developer newsletter

Product updates, how-tos, community spotlights, and more. Delivered monthly to your inbox.

Please provide your email address if you'd like to receive our monthly developer newsletter. You can unsubscribe at any time.
