# Docker Support

This project includes a lightweight Docker setup for the REST API. Build and run with:

```bash
cd docker
docker compose up --build
```

The container exposes port `5000` for API access. Configuration files in `config/` are mounted into the container for read-only access.
