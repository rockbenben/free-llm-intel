---
vendor: cerebras
title: What It Took to Build Wafer-Scale, and Why It Lasts
original_title: From our CEO: What It Took to Build Wafer Scale, and Why It Lasts — read more >
url: https://www.cerebras.ai/blog/what-it-took-to-build-wafer-scale-and-why-it-lasts
date: 
lang: en
captured: 2026-11-06
extractor: readability-v1
status: ok
body_sha: 779a12f085b9
---

Nov 05 2026

# What It Took to Build Wafer-Scale, and Why It Lasts

[Andrew Feldman](https://www.cerebras.ai/author/andrewcerebras-net)

Last week, a short seller, Culper Research published a report arguing that Cerebras wafers wear out after about two years. Nearly every financial conclusion in that report, from our margins to the value of our OpenAI agreement, depends on that one number.

That number is wrong.

How long our systems last is a fair question for customers and shareholders alike, so we want to address the topic plainly.

### **The problem was hard**

For decades the industry considered wafer-scale computing impossible to scale, especially after Gene Amdahl's Trilogy Systems, one of the best-funded startups of its era, abandoned the attempt in the 1980s. A processor the size of a dinner plate has to be powered, cooled, and connected without cracking.

The hardest part is mechanical. Silicon and the circuit board beneath it expand at different rates as they warm and cool. At wafer scale, that mismatch is large enough to break connections, or the wafer itself, if it is not managed.

The report is right that this is hard. It took us years to solve this problem. But we learned from every failure, worked with our customers, improved the design as we went, and now we are on our third generation, transitioning to our fourth. We have a highly reliable product whose lifetime will be constrained not by thermal-induced failure but by future generations of Cerebras silicon competing for the power and space it consumes.

Part of our development process was learning what did not work. The report asserts that we use a third-party material, called a PariPoser, as the connector in our systems. From that, the report concludes that Cerebras has not innovated and not solved the thermal expansion problems key to wafer-scale reliability.

This is among the many inaccuracies in the report. To be clear, we don’t use the PariPoser and have never shipped a single system that uses it.

### **How we solved it**

The answer to solving wafer scale was never a single material. It is an assembly, patented since 2019, that runs under a primary operating rule: moderate abrupt temperature changes on the wafer, both over time and across its surface. This enables reliable operation over long periods of time while achieving industry-leading performance.

- **Power changes gradually.** As our systems power up or down, circuitry on every core smooths sudden swings in current. Accordingly, power changes gradually to avoid damaging spikes. The “dummy operations” the report describes are one of the tools that do this; controlled power draw is an established engineering technique in our industry (NVIDIA’s B300 design includes a “power burner” mode that maintains GPU power consumption when useful work drops, then ramps it down to smooth power consumption).
- **Temperature stays even across the wafer.** The report found that we keep our wafers at a steady temperature. That is correct and deliberate. A steady temperature is how you prevent mechanical fatigue, for the same reason power plants avoid frequent cold starts. Culper’s mistake is assuming that steady means hot. It does not. 
Chilled water reaches every region of the wafer through many short loops, and compute work is spread so no region runs much cooler than its neighbors. These innovations protect the wafer from uneven thermal expansion and are enforced by hardware so that even faulty software cannot damage the wafer.
- **Every connection to the wafer is flexible**. The electrical connection to the board flexes, and the interface to the cold plate slides, so wafer and board move without straining each other when temperature rises or falls. Just like the joints in a suspension bridge, “mechanical flex” in our systems safeguard against stress-induced failures.

### **Understanding what the data says about our silicon**

Silicon is retired for one of three reasons: it fails mechanically, heat wears it out, or it is no longer economically attractive to keep using it.

**Mechanical. 
**Cerebras implemented techniques to ensure steady, even temperatures precisely to reduce the mechanical risk caused by large, abrupt fluctuations in temperature.

**Heat. 
**Chips age faster when they run hot. Assuming that Cerebras wafers run hot, the report reached a two-year lifetime conclusion in two ways. Both are wrong.

The authors took the five-to-seven-year economic life of GPUs and scaled that down by their estimate of how much harder our wafers work. But GPUs are retired because newer chips make them uneconomic, not because they wear out. Scaling an economic life by a physical ratio is a logical error and yields a number that describes nothing.

The authors also sought to apply the Arrhenius equation to estimate the lifespan of a wafer prior to thermally induced failure. While this is the correct equation, the report uses the wrong inputs.

The Arrhenius equation requires: (1) a valid lifetime at a known reference temperature and (2) the actual operating temperature. The report used neither of these.

The Cerebras wafer is qualified by TSMC, its manufacturer, for 10 years of continuous operation at 105°C, twenty degrees above our maximum. Across our deployed fleet of CS-3s, the wafers’ average junction temperature is less than 65°C and doesn’t exceed 85°C. Both are well within industry norms.

Using these inputs, the Arrhenius model shows that a wafer held at its maximum temperature of 85°C every hour of every day would last **33 years** before heat wore it out. A wafer held at an average junction temperature of 65°C would last more than a century.

No one will run a CS-3 for 33 years. The point is that heat induced failure is not what will retire it.

This is consistent with our field data – since the introduction of the CS-3 in 2024, less than half of one percent of all CS-3 wafers deployed have been decommissioned.

Nearly all of the report’s conclusions rest on the assumption of short wafer life. But the wafers’ life isn’t short, it’s long. Without that assumption, the conclusions from the report fall apart.

**Economics**. 
Most silicon is retired for economic reasons – newer generations of silicon do more per dollar and per watt. We believe that like GPUs, CPUs and nearly all silicon at market, our solutions will be retired when there are more efficient ways to use the power and space that they consume.

This is a different concept than how accountants measure depreciation and useful life.

The accounting for useful life reflects how long Cerebras gets value from our fixed assets. When we filed our first S-1, the compute equipment we used internally was primarily for R&D labs. Our engineers received the latest generation of our chips, wrote software, and conducted heavy performance testing. Our estimate of useful life was informed by the wear and tear of lab testing, but more importantly by when our engineers cut over to start testing the next generation of our product: CS-1 was introduced in 2020, CS-2 in 2022, and CS-3 in 2024. Accordingly, we estimated 1-3 years.

By the next update of our S-1, we had set out to build a private cloud; the reason was that AI native customers and developers asked us to. One consequence was that the mix of fixed assets we used internally had changed to include production systems we owned for the cloud business. We therefore modified our depreciation schedule to 3-5 years, reflecting both our internal use lab equipment and the economic life of our owned and operated cloud production assets. Most cloud providers currently report AI equipment with 5-6 year useful lives, placing us comparatively on the more conservative end. Finally, all of these management estimates, including useful life, are part of the annual audits conducted by KPMG.

### **A decade of work**

Wafer-scale computing was considered impossible because the technical hurdles were real. We spent ten years solving them, and our earliest customers lived through part of that learning curve with us. Each generation has improved on performance, features, and reliability. Today's systems run steady and cool, and they are built to outlast their economic life by many years.

As fast inference becomes a larger share of AI workloads, we understand the desire to model Cerebras’ product lifetimes. We also recognize that, as with any new and pioneering technology, there are not decades of data available. And as with all new and fundamentally different architectures, there is a learning curve around the trade-offs we made. We appreciate the curiosity and interest in our technology.

We love building silicon and are happy to engage in technical discussions on this or other topics related to fast inference with the community.

Andrew Feldman
CEO and Co-Founder

Disclosure: I am long Cerebras stock.
