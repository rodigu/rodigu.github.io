<!--
.. title: a simple shared memory system for llms
.. slug: llm-shared-memory
.. date: 2026-06-19 21:30:08 UTC-03:00
.. tags: llm, llm-tooling
.. category: data-eng
.. author: rodigu
.. link: https://rodigu.github.io/
.. description: a simple memory system for llms
-->

how can we share complex context between llm agent sessions?

that's the question i wanted to answer for my team.
as we integrate llm agents more and more into our workflows, sharing how each team member is doing that is important for sustainable development practices: why did an agent go with this solution? what decisions drove such and such implementation?

so i built a shared memory for my team's llms to fix these issues.

<!-- TEASER_END -->

the basic requirements i had for this system were:

- crud (create, read, update, delete): the ability to perform all 4 basic operations on the data
- easy search: a simple, straight-forward way to search through the data so llms can easily retrieve relevant context

i did consider using a vector database, implementing a rag. rags do semantic search over unstructured text, and fuzzy matching when you don't know the exact terms. useful, but not free: you need vector databases deployed and embedding models to interface with them, adding to token costs.

for our use case the trade-off didn't make sense. our memories are short, and we enforce consistent tagging at creation time, the llm itself proposes tags when creating a memory, and the user can edit them before confirming. grep on structured, consistent tags gives us what we need without extra infrastructure. rag solves a different problem: finding relevant context in a large, messy, unstructured corpus. we didn't have that problem. if our memories were thousands of long, inconsistently written documents, i'd have gone with rag.

so i designed a system that wouldn't require a lot of overhead on operations.

## the jsonl solution

in my experience, llms work best with short, well structured information. if they are given too much room to hallucinate, they will do it. this is why i don't think llm wikis are much of a good idea, the information is just not structured enough.

the first solution i came up with was to adopt [pi](pi.dev)'s (the npm llm agent) style of using `jsonl` files to store session data. each memory had its own uuid, update date, description, tags and content.

jsonl files are more structured than markdown, restricting the data format llms have to operate under.

```ts
interface MemorySearch {
    id: string;
    description: string;
    tags: Array<string>;
}

interface MemoryEdit {
    id: string;
    description?: string;
    tags?: Array<string>;
}

interface MemoryCreate extends MemorySearch {
    content: string;
}

interface MemoryQuery extends MemoryCreate {
    changedAt: Date;
    deletedAt?: Date;
}
```

the `changedAt` property doubles as a created at property. since the memories work as a type 2 slowly changing dimension[^3], each memory edited adds a new line to the jsonl.
with this system, `deletedAt` becomes a soft delete, and we get to keep historical data on past memories.

[^3]: instead of changing the original memory, edits add new lines with the updated data

the tags served to help llms search for relevant memories, and the description helped them decide if a memory is relevant and should be read.
i also created five tools: search, create, edit, read, delete.

```ts
function search(keyWords: Array<string>): Array<MemorySearch>
function create(newMemory: MemoryCreate)
function edit(memory: MemoryEdit)
function read(id: string): MemoryQuery
function delete(id: string)
```

search receives keywords that were searched for in tags and description, returning the id, description and tags for matches.

however, scaling simple jsonl files to multiple users presented one key issue.

how do we sync memories across agents? using git would still introduce merge problems. the main trouble is deciding what happens when two users edit the same memory.
because memories were stored in a single file, any operation on memories would involve affecting memories that come after it in the file.

## sql server table

keeping the same tools, i changed the implementation to use a memory table in our production server instead.

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

this solved the issues with the jsonl implementation, as concurrency is built into the server itself. before, with shared memory files, we'd have to go through the trouble of merge conflicts. now we just offload this complexity to sql server.

this evolution was only really possible because of the architecture decisions taken before writing any code.

i defined the tool signatures first: what the llm needs to call, and what it gets back. the storage layer is invisible to the agent. it doesn't know or care whether memories live in a jsonl file or a sql table. all it sees are the same five functions: search, create, edit, read, delete.

the llm interface is a contract. when i migrated from jsonl to sql, not a single tool definition changed. the agent's behavior stayed the same. only the storage changed.

this is why defining interfaces before implementation pays off. llm tool use is still early — storage backends will change, infra will shift, team needs will evolve. if your tool definitions are coupled to your storage, every backend change breaks every agent using your system. decoupling them from day one meant my migration cost me an afternoon instead of a rewrite.

the cost of the final solution was marginal, as we already had a sql server instance running.
