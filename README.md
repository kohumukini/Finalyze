<div align="center">
    <h1>Finalyze</h1>
    <img src="https://img.shields.io/badge/Project_Status-In_Progress-red" height=25 />
    <p>
        <img src="https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white" height=25/>
        <img src="https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E" height=25/>
        <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" height=25/>
        <img src="https://img.shields.io/badge/fastapi-005571?style=for-the-badge&logo=fastapi" height=25/>
        <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" height=25/>
    </p>
</div>

## Overview
**Finalyze** was built to explore the internal mechanics of Retrieval-Augmented Generation (RAG) systems, bypassing black-box frameworks like LangChain or LlamaIndex. 

The primary goal was to design, develop, and deploy a fully functional RAG system to parse, store, and query dense documents accurately.

### Key Focus Areas
- **Full-Stack lifecycle and Project Management:** Designed, built, and version-controlled application from static HTML webpages, through containerized backends, into full-stack deployment on Render
- **RAG Pipeline:** Implemented chunking and ingestion pipeline, creating embeddings that are upserted into pgvector, an extension of PostgreSQL alongside tabular data
- **Deployment & Configuration:** Configured backend docker environment for testing, managed CORS headers, and implemented rate limiting for stability

### Key Takeaways

**1. Project Schema & Project Design:** Strategizing finalyze reduced workload and alleviated development bottlenecks. Finalyze, as various other projects do, require cascading decisions eased by proper planning and project management. Finalyze required decisions for the types of tools to use, the vector database and embedding model, the host, and iterative development strategies among various others.

**2. API Management & Rate Limiting:** Implemented middle-ware rate limiting to reduce API abuse and prevent LLM provider throttling. API management is a broad area that expands past rate limiting and routing. Finalyze is a stepping stone to build an understanding of API management.

**3. Deployment:** Configured deployment on Render ensuring proper routing between the static frontend assets and FastAPI endpoints.

**4. Testing on Real Data:** Example-based tests alone missed bugs that only appeared in full SEC filings (multi-level tables, double-spaced headings, page footers). Invariant tests run across 15 real 10-Ks check properties that must always hold: no number lost or invented, no leftover noise, and cleaning twice changes nothing. When an invariant fails, the first question is whether the code or the expectation is wrong.

**5. Embeddings and Tables:** Embeddings capture what a chunk is about, not which number belongs to which year. A raw markdown table and a regrouped one embed nearly identically, so tables are kept as-is. What matters for retrieval is that a chunk carries its labels, header row, and section heading. Exact figures are better served later by structured XBRL lookup alongside RAG.

## Architecture

**Query path**

```text
  +-------------------+    POST /chat (question + history)    +-----------------------+
  | Static Frontend   | ------------------------------------> | FastAPI               |
  | HTML / CSS / JS   | <------------------------------------ | (rate limited)        |
  +-------------------+    JSON: answer + cited sources       +-----------+-----------+
                                                                          |
                     1. Gatekeeper: is the question in scope?             v
                        rewrite it into search queries        +-----------------------+
                                                              | Groq: gpt-oss-20b     |
                                                              +-----------+-----------+
                                                                          |
                     2. Embed each query                                  v
                                                              +-----------------------+
                                                              | Gemini Embedding 2    |
                                                              +-----------+-----------+
                                                                          |
                     3. Vector search for matching chunks                 v
                                                              +-----------------------+
                                                              | PostgreSQL + pgvector |
                                                              +-----------+-----------+
                                                                          |
                     4. Answer from retrieved chunks + history            v
                                                              +-----------------------+
                                                              | Groq: gpt-oss-120b    |
                                                              +-----------------------+
```

**Ingestion path** (in progress)

```text
  edgartools (10-K markdown) -> clean_markdown -> chunk_doc -> Gemini Embedding 2 -> pgvector
```

## Tech

| Layer | Tech |
|---|---|
| **Frontend** | HTML, CSS, JavaScript (static; React/TypeScript migration planned) |
| **Backend** | Python, FastAPI, SQLAlchemy, SlowAPI (rate limiting) |
| **Database** | PostgreSQL + pgvector |
| **LLM** | Groq: gpt-oss-120b (answers), gpt-oss-20b (gatekeeper & query rewriting) |
| **Embeddings** | Gemini Embedding 2 (768 dimensions) |
| **Documents** | SEC 10-K filings via edgartools (Apple, Costco, T-Mobile) |
| **Testing** | pytest (golden-master cases + invariant tests on real filings) |
| **Deployment** | Render |

## Features

## Roadmap

- [x] Build & attach vectordb
- [x] MVP Completion 
  - Defined as: Full-stack web application with fully usable RAG
  - HTML & CSS Frontend
  - Hooked up server & backend (render & fastapi respectively)
  - Connected to LLM (Groq openai/gpt-oss-120b)
  - Data storage within server service
- [x] Implement LLM for query gatekeeping & multi-query generation
- [x] PyTest Suite
- [x] Render model output
- [x] Markdown cleaner for 10-K filings (golden-master cases + invariant tests on 15 real filings)
- [ ] Table-aware chunker
  - Cut only at sentence ends, block boundaries, table rows, or before headings (no mid-word cuts)
  - Repeat the table header row and prepend the section heading on split tables
  - No tiny leftover chunks
- [ ] Build document ingestion pipeline (edgartools → clean → chunk → embed → store, as one command)
- [ ] Merge to `main` and re-ingest (planned alongside the database reset)
- [ ] XBRL lookup for exact financial figures
- [ ] Migrate to React/TypeScript/Tailwind for frontend & adjust UI view
