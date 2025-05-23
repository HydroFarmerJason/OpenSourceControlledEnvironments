# API Authentication

All API requests require an API key provided via the `X-API-Key` header.

Example using `curl`:

```bash
curl -H "X-API-Key: YOUR_KEY" http://localhost:5000/api/status
```

Generate a key and set it as the environment variable `API_KEY` before starting the API server.
