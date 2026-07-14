# AI-First HCP CRM Frontend

React + TypeScript + Redux Toolkit frontend for the AI-first CRM HCP interaction assignment.

The application provides:

- A split-screen interaction workspace
- A read-only HCP interaction form on the left
- A conversational AI assistant on the right
- Redux state management
- Session restoration through the FastAPI backend
- Visual indicators for all five LangGraph tools
- Responsive desktop and mobile layouts

## Important behavior

The left-side form has no manual editing handlers. It changes only when the backend returns a new `current_form` from `POST /api/chat`.

## Prerequisites

- Node.js 18 or newer
- The FastAPI backend running on `http://127.0.0.1:8000`
- Backend CORS configured with `FRONTEND_URL=http://localhost:5173`

## Setup

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Open:

```text
http://localhost:5173
```

## Environment variables

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_BACKEND_URL=http://127.0.0.1:8000
```

## Build verification

```powershell
npm run build
```

## Main frontend flow

```text
Chat prompt
  -> Redux submitChatMessage thunk
  -> POST /api/chat
  -> LangGraph agent and selected CRM tool
  -> FastAPI current_form response
  -> Redux currentForm replacement
  -> Read-only interaction panel rerender
```

## Five demo prompts

### Log Interaction

```text
Today I met Dr. Anjali Mehta at Fortis Hospital in person. We discussed CardioPlus efficacy and dosing. Her sentiment was positive and I shared a product brochure.
```

### Edit Interaction

```text
Correction: the sentiment was neutral and I also shared the safety study.
```

### Search HCP

```text
Find Dr. Priya Nair from Manipal Hospital.
```

### Get Interaction History

```text
Show the last two interactions with Dr. Anjali Mehta.
```

### Schedule Follow-up

```text
Schedule a high-priority follow-up call next Monday to discuss the safety data.
```

## Project structure

```text
src/
├── app/
│   ├── hooks.ts
│   └── store.ts
├── components/
│   ├── AppHeader.tsx
│   ├── ChatPanel.tsx
│   ├── ChipList.tsx
│   ├── InteractionPanel.tsx
│   ├── ReadonlyField.tsx
│   └── SectionCard.tsx
├── features/crm/
│   └── crmSlice.ts
├── services/
│   └── crmApi.ts
├── types/
│   └── crm.ts
├── utils/
│   └── session.ts
├── App.tsx
├── main.tsx
└── styles.css
```
