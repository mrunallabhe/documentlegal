## Frontend Dashboard

Lightweight React/Vite app (scaffold-ready) for uploads, case monitoring, and report previews.

### Development
1. `npm create vite@latest frontend -- --template react`
2. Install dependencies: `npm install`
3. Configure API base URL via `.env` (`VITE_API_URL=http://localhost:8000`)

### Pages / Components
- `UploadForm` – drag-and-drop upload, calls `/evidence/upload`.
- `ProcessingPanel` – trigger `/evidence/process`.
- `TimelineView` – fetch `/reports/{case_id}` and plot events.
- `InconsistencyList` – display conflicts and missing evidence suggestions.

Current repository contains a static HTML mockup (`public/index.html`) to illustrate layout while React scaffolding is prepared.

