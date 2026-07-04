# Frontend - React + Vite

Modern React frontend for the Enterprise Sales AI Analytics System.

## Features

- ✅ Chat interface for natural language questions
- ✅ Real-time answer display
- ✅ SQL evidence panel (expandable)
- ✅ Confidence score visualization
- ✅ Validation status indicator
- ✅ Cache hit/miss tracking
- ✅ Retry count display
- ✅ Token usage breakdown
- ✅ Execution time metrics
- ✅ Query history panel
- ✅ API health status
- ✅ Responsive design (mobile & desktop)

## Setup

### Development

```bash
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Production

```bash
npm run preview
```

## Environment Variables

Create `.env.local` (optional):

```env
VITE_API_URL=http://localhost:8000
```

Defaults to `http://localhost:8000` if not set.

## Project Structure

```
src/
├── components/
│   ├── Header.tsx          # Top navigation
│   ├── ChatInput.tsx        # Question input area
│   ├── Message.tsx          # Response display with metadata
│   ├── QueryHistory.tsx     # Query history panel
│   └── StatusBar.tsx        # API health status
├── services/
│   └── api.ts              # API client (axios)
├── App.tsx                 # Main app component
├── main.tsx                # Entry point
└── index.css               # Tailwind styles
```

## API Integration

The frontend communicates with the FastAPI backend:

- `POST /ask` - Submit a question
- `GET /health` - Check API health
- `GET /history` - Get query history

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide Icons** - Icons
- **date-fns** - Date formatting
