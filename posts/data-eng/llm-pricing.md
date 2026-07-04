<!--
.. title: how i am pushing for llm cost control in my team
.. slug: llm-cost-control
.. date: 2026-07-04 14:18:00 UTC-03:00
.. tags: llm, agents, governance, token-cost
.. category: data-eng
.. author: rodigu
.. link: https://rodigu.github.io/
.. description: cost control for llms
-->

the real cost of llm use is [already hitting some large companies like a truck](https://www.forbes.com/sites/janakirammsv/2026/05/17/uber-burns-its-2026-ai-budget-in-four-months-on-claude-code/). and i expect individual developers will soon start to feel the costs too.

i have been talking about the end of the subsidies and how to prepare for the actual costs of llms with my peers for a while now. and at the information and data team at cejam, i have helped us prepare for it in three major ways: implementing a governance gateway for cost control, providing training on llm usage, and deploying cheaper models.

<!-- TEASER_END -->

## the end of the subsidies

current llm subscription models were heavily subsidised. be it for market capture or gathering more training data, those subsidies are starting to run out.

anthropic is [changing the way they charge users](https://www.techtimes.com/articles/317625/20260602/anthropic-ends-subscription-subsidy-agents-june-15-credit-pool-replaces-flat-rate-access.htm) and github [moved to usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/). the truth is the subsidized subscription model was unsustainable long-term, and the folks at the major ai companies most certainly knew that from the get-go.

while before, some companies had leaderboards for token use, now there is talk of a *tokenpocalipse*, and people are scrambling to reduce token usage[^1].

[^1]: 404 media has a great article about the [tokenpocalypse](https://www.404media.co/the-tokenpocalypse-is-here-companies-are-scrambling-to-stop-spending-so-much-on-ai/)

## bifrost as an llm gateway

i have been using microsoft foundry for a while now to deploy llms for my team.
the trouble with foundry is that it exposes a single project endpoint and token that are used for consuming llms from the api.

this is no good for a team with many members, where many people might be using the same llm at once. how do you keep track of costs and use? how do you control leaks and exploits?
microsoft offers their own api gateway solution, but the cheapest subscription is $150, and i knew i could find a better value proposition.

while looking for alternatives, i found litellm, which seems to be turning into a sort of industry standard. but the recent [supply chain incident](https://docs.litellm.ai/blog/security-update-march-2026) turned me away from it.
so i decided to go with [bifrost](https://github.com/maximhq/bifrost), a newer llm gateway written in go to be performant and lite.

with bifrost, we generate keys for team members and projects, setting budget limits for varying time frames. it also gives full governance over requests, letting me see exactly what is being sent to the llms.

## llms agents are not magic (though they sometimes feel like they are)

i have observed that even amongst the most avid llm agent power users, a fundamental lack of understanding of the basics of how llms work is still missing.
it is common to see users accumulating a massive context and moving the same session between tasks.

even a basic understanding of context windows, token caching, and how llm input and reasoning pricing[^2] works already helps a lot in giving users the fundamentals to make better use of llm agents.

[^2]: computerphile has recently posted a [great video](https://www.youtube.com/watch?v=-0HRzXk8vlk) on token pricing

## deploying cheaper models

open source models have been getting really exceptional in their cost-benefit.
deepseek v4 pro is *really* cheap for what it can do.

i am a strong believer that we will see more and more that llm performance improvements have to do with technique than model size: appropriate context handling, atomic tasks, agent management.

we are already seeing that with [cybersecurity](https://arxiv.org/html/2604.20801v1). smaller models can perform as well as mythos when given the [proper harness](https://www.aikido.dev/blog/mythos-vs-harness), for a fraction of the cost.

## the future

the frontier models are, from my standpoint, impractical to implement due to their cost. for instance, claude *sonnet* is 5x the base price of deepseek v4 pro.

the actual future of llm agent implementation in production will involve smaller models with very good harnesses and access to a limited set of tools, doing targeted, atomic, tasks.

as an anecdote, i see some people using llms to search for errors in log files.
the cost of loading a couple kilobytes of logs into the input tokens of a higher end model can get expensive very fast.
thankfully, i have given proper `grep` and `ls` tools for the agents i make available for my team, so when that happens (and that *has* happened), the cost stays negligible.
