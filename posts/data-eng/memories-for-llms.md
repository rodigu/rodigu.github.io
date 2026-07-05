<!--
.. title: a simple shared memory system for llms
.. slug: llm-shared-memory
.. date: 2026-06-19 21:30:08 UTC-03:00
.. tags: llm, llm-tooling
.. category: data-eng
.. status: draft
.. author: rodigu
.. link: https://rodigu.github.io/
.. description: a simple memory system for llms
-->

i wanted an easy way to share context between sessions for the members of my team.

the basic first requirements i had for this system were:

- crud: the ability to perform all 4 basic operations on the data
- easy search: a simple, straight-forward way to search through the data so llms can easly retrieve relevant context

i did consider using a vector database, implementing a rag. but rags are not free to develop, run and maintain (talking mainly about infra costs here). i also think they would have been overkill[^1], a simple grep would sufice on well tagged data.

[^1]: why go for simplicity when you can overcomplicate everything

in my experience, llms work best with short, well structured information. if they are given too much room to halucinate, they will do it[^2].

[^2]: reasons why i find the idea of an [llm wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) so silly. the diagrams in the comments are silly too

## the jsonl solution
