<!--
.. title: minimalist shared memory system for llms
.. slug: llm-shared-memory
.. date: 2026-06-19 21:30:08 UTC-03:00
.. tags: llm, llm-tooling
.. category: data-eng
.. author: rodigu
.. link: https://rodigu.github.io/
.. description: a simple memory system for llms
-->

<p align="center">
    <img src="../../images/memories-for-llms.jpg" width="400">
</p>

my team at cejam are increasingly integrating llm agents into the work we do. we have been hitting a problem: each agent session knew nothing of the others. someone's agent solved a bug one way, mine had to figure out how to solve it again and we had no record of why decisions were made.

i needed a shared memory for our llms.

<!-- TEASER_END -->

my initial requirements were:

- tools to create, read, update, delete memories
- easy search so agents can find relevant context

i considered a vector database with retrieval-augmented generation a rag that does semantic search over unstructured text. useful, but expensive: you need vector databases deployed, embedding models to interface with them, and more tokens.

the llm memories we need to share are short. we can enforce consistent tagging at creation time-the llm proposes tags, and the user edits before confirming. a basic grep on structured tags and well written descriptions gives us what we need. rag solves a different problem we don't have: finding context in large, messy, unstructured corpora.

## the jsonl solution

llms work best with short, structured information. given too much room, they hallucinate. that's why i believe llm wikis don't work well, the information isn't structured enough.

for a first proof of concept, i used [pi](pi.dev)'s approach: jsonl files for session data. each memory has a uuid, update date, description, tags, and content.

```ts
interface MemoryBase {
    id: string;
    description: string;
    tags: Array<string>;
}

interface MemoryEdit {
    id: string;
    description?: string;
    tags?: Array<string>;
}

interface MemoryCreate extends MemoryBase {
    content: string;
}

interface MemoryQuery extends MemoryCreate {
    changedAt: Date;
    deletedAt?: Date;
}
```

the `changedAt` property works as both created-at and updated-at. memories act as a type 2 slowly changing dimension: edits add new lines with updated data instead of changing the original. `deletedAt` is a soft delete, and we get to keep history for each memory.

tags help llms search for relevant memories. descriptions help them decide if a memory is worth reading.

here are the signatures for the five tools: search, create, edit, read, delete.

```ts
function search(keyWords: Array<string>): Array<MemoryBase>
function create(newMemory: MemoryCreate)
function edit(memory: MemoryEdit)
function read(id: string): MemoryQuery
function delete(id: string)
```

search checks keywords against tags and descriptions. returns id, description, and tags for matches.

but scaling to multiple users broke this. git would introduce merge conflicts, and we had to decide what happens when two users edit the same memory every time it happened. worse, memories stored in a single file meant any operation in a single memory affected all memories.

## sql server table

i kept the same tools. changed storage to a memory table in our production server.

```sql
CREATE TABLE Memories (
    pk INT IDENTITY(1,1) PRIMARY KEY,
    id UNIQUEIDENTIFIER NOT NULL,
    description NVARCHAR(500) NOT NULL,
    tags NVARCHAR(MAX) NOT NULL, -- stored as json array
    content NVARCHAR(MAX) NOT NULL,
    changedAt DATETIME2 NOT NULL,
    deletedAt DATETIME2
);
```

sql server now handles concurrency, and we get no more merge conflicts.

the migration worked because of the architecture. i defined tool signatures first: what the llm calls, what it gets back. storage is invisible to the agent, it doesn't know or care whether memories live in a jsonl file or a sql table.

the llm interface is a contract. when i migrated from jsonl to sql, no tool definitions changed. agent behavior stayed the same. only storage changed.

defining interfaces before implementation is what allowed this. llm tool use is early-storage backends will change, infra will shift, team needs will evolve. if tool definitions are coupled to storage, every backend change breaks every agent. decoupling from day one meant migration cost little development time.

the final solution's cost was minimal since we already had a sql server instance running (no new costs setting up a new server or database).
