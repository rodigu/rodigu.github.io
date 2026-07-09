<!--
.. title: small language models (slms) on android
.. status: draft
.. slug: slm-android
.. date: 2026-07-09 19:17:25 UTC-03:00
.. tags: android, termux, llm, slm
.. category: data-eng
.. link: https://rodigu.github.io/
.. description: running slms on android with ollama
-->

small language models are getting really good, and *very* tiny.
from last year, [google already had been using gemma 3 1b](https://developers.googleblog.com/en/google-ai-edge-small-language-models-multimodality-rag-function-calling/) as on-device models that even have tool-calling capabilities. apple has also launched [openelm](https://machinelearning.apple.com/research/openelm), a family of models targeting local inferencing, with models as small as 270 million parameters.

for fun, here are some tokens per second benchmarks for a few slms running on my [samsung galaxy a15](https://www.gsmarena.com/samsung_galaxy_a15-12637.php) (an almost 3 years old phone).

<!-- TEASER_END -->

i am running these models on termux using ollama.
i only asked the models `what is the capital of france`.

|model|size|avg tokens per second|tokens|reasoning time|
|-|-|-|-|-|
| [qwen 3.5](https://ollama.com/library/qwen3.5:0.8b)| 0.8b | 5.5 |1340|5 minutes|
| [lfm2.5](https://ollama.com/library/lfm2.5-thinking:1.2b)| 1.2b | 4 |260|1 minutes|
| [gemma3](https://www.ollama.com/library/gemma3)| 1b | 7 |30|non-reasoning|
| [gemma3](https://www.ollama.com/library/gemma3)| 270m | 10 |30|non-reasoning|

of course, this simple question isn't necessarily a good benchmark for actual practical use. qwen 3.5, for instance, is great at tool calling. it can run on my 5 year old galaxy book at 27 tokens per second, and can do basic calls (read, edit, write) on python scripts, which is impressive.

the gemma3 models are non-reasoning, and because of that they answer very fast. the 270m model in particular gets to 11 t/s at times. of course, it *is* the least capable at well in terms of encyclopedic knowledge. but i do like how straight to the point it is. unlike gemma3 1b, the smaller cousin does not use emojis at all. the smaller models are mostly useful as cognitive cores that pull information from elsewhere and call tools.
