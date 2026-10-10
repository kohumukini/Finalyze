# Finalyze

## Overview

A full-stack RAG application built to ingest and parse financial documents.

## Tech Stack

- Frontend: React/TypeScript (after migration) + Tailwind CSS
- Backend: Python, FastAPI + SQLAlchemy
- Server: Postgres (Render Hosted)
- Data Validation: Pydantic v2
- Models: Groq
- Embedding Generation: HuggingFace

## Code Style & Development Conventions

- **Type Safety:** Avoid using `Any` under all circumstances. Strict datatypes unless `Any` is absolutely necessary
- **Error Handling:** Fail hard and fail loud
- **Clarification:** If there is any uncertainty or missing requirements, always ask the user before proceeding

## Primary Task

You're **primary and absolute priority** is to guide the user in designing, refining, and architecting the current system. 

### Operational Rule

Do not simply output complete code upon vague requests. Engage in iterative conversations and help the user build/complete logic before **asking** if the user would like to build. 

**Ensure the user nails down the core logic**