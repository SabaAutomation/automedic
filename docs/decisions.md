# Decisions

- **Ollama instead of a paid API:** keeps the project free and runnable offline.
- **Simulated workflow first:** lets the agent be built and tested before adding n8n.
- **Model in .env:** swapping models needs no code changes.
- **Text tool-call fallback:** some small models do not emit proper tool calls.