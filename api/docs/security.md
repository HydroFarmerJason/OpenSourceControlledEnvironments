# API Security

The REST API includes several lightweight protections:

- **API key authentication** via the `X-API-Key` header.
- **Rate limiting** of 60 requests per minute per IP address.
- **Input validation** for control actions (`toggle`, `on`, `off`).

Set an API key before starting the server:

```bash
export API_KEY=mysecret
python api/rest_api.py
```

Requests exceeding the rate limit will receive an HTTP `429` response.
Invalid or missing actions on `/api/control/{output}` return `400`.
