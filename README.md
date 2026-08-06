<div align="center">
    <h1>Finalyze</h1>
    <img src="https://img.shields.io/badge/Project_Status-In_Progress-red" height=25 />
    <p>
        <img src="https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB" height=25/>
        <img src="https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white" height=25/>
        <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" height=25/>
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

## Architecture

```
  +-----------------+
  | Static Frontend |
  +--------+--------+
           | User Input
           v
  +-----------------+       Fetch Request        +-----------------+
  | JavaScript Form | -------------------------> |  FastAPI App    |
  +--------+--------+ <------------------------- +--+-----------+--+
           |                Return JSON             ↑           |
           | Create elements                        |           | 1. Query for Embeddings
           v                                        |           v    & Context
  +-----------------+                               |   +------------------+
  | DOM Manipulation|                               |   | PostgreSQL +     |
  +--------+--------+                               |   | pgvector DB      |
           | Update                                 |   +--------+---------+
           v                                        |            |
  +-----------------+                               |            | 2. Return Retrieved
  | Static Frontend |                               |            |    Context Chunks
  +-----------------+                               |            v
                                                    |   +------------------+
                                                    +-->| Groq API         |
                                                        | (Llama 3.3)      |
                                                        +------------------+
                                                          3. Send Context +
                                                             User Prompt
```
## Tech

| Layer | Tech |
|---|---|
| **Frontend** | <span style="color: gray">React, Typescript, Tailwind CSS, Vite</span> - HTML, CSS, JavavScript
| **Backend**  | Python, FastAPI, SQLAlchemy
| **Database** | PostgreSQL
| **Deployment** | Render

## Features

## Roadmap

- [] Build & attach vectordb
- [] Allow for document uploads & storage
- [] Implement pdf parsing & improve chunking system
- [] Convert to React/TypeScript building components and type validation
- [] Implement personal dashboard with stats
- [] Build user sections & google login system
- [] Finish UI touches
