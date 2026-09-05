# HEFIN Frontend

Next.js 14 frontend for HEFIN.

## Features

- Medical Galaxy landing experience
- Authenticated AI Assistant
- Document Vault upload and parse flow
- API client with JWT bearer authentication
- Responsive dark healthcare intelligence UI

## Run

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

The development server runs at `http://localhost:3000` and expects the FastAPI backend at `http://localhost:8000` unless `NEXT_PUBLIC_API_BASE_URL` is configured.
