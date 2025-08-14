# YouTube to Newsletter

A system that converts YouTube video content into newsletter-ready summaries using a microservices architecture.

## Features
- Summarizes YouTube videos
- Generates newsletter content
- Modular microservices (summarizer, recommendation, user management, newsletter generator)
- GraphQL API
- Dockerized deployment

## Project Structure
- `frontend/` – React app (Vite)
- `graphql/` – GraphQL schema and resolvers
- `services/` – Microservices (Python)
- `infrastructure/` – Deployment configs (Docker, Cloud Run, Pub/Sub)
- `docs/` – Documentation

## Getting Started
See `docs/setup-guide.md` for installation and usage instructions.

## License
MIT License
