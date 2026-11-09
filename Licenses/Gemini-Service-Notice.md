# Gemini API service

ChessLLM's REST adapter is part of the MIT-licensed application. It does not bundle Google's SDK or Gemini weights. Access to Google's service and model is governed by Google's terms and the user's API account.

- Model: https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite
- API terms: https://ai.google.dev/gemini-api/terms
- Key management: https://aistudio.google.com/apikey

No API key is included, persisted by the app, or embedded in public artifacts. The Gemini integration tests use a fake key and a local mock server; they never contact Google for generation.
