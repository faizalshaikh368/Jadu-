# AI Kubernetes Agent

AI-powered Kubernetes troubleshooting system that investigates cluster issues and provides root cause analysis with suggested fixes.

## Architecture

```text
Frontend (Next.js)
    ↓
FastAPI Backend (Orchestrator)
    ↓
Kubernetes Investigation Layer
    ↓
AI Kubernetes Agent
    ↓
LLM Reasoning (OpenRouter)
    ↓
Root Cause + Suggested Fix
    ↓
Frontend Diagnosis
```

## Features

- **Kubernetes Investigation**: Automatically collects evidence from pods, logs, events, deployments, and networking
- **AI-Powered Diagnosis**: Uses LLM to analyze evidence and provide root cause analysis
- **Actionable Fixes**: Suggests specific kubectl commands to resolve issues
- **Confidence Scoring**: Provides confidence levels for each diagnosis

## Tech Stack

### Backend
- FastAPI
- Python 3.12+
- Uvicorn
- Pydantic
- Loguru
- HTTPX

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Axios
- React Query

### Infrastructure
- Docker
- Docker Compose

## Project Structure

```text
ai-kubernetes-agent/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── core/             # Configuration and logging
│   ├── kubernetes/       # Kubernetes investigation layer
│   │   ├── kubectl_executor.py
│   │   ├── pod_inspector.py
│   │   ├── logs_collector.py
│   │   ├── events_analyzer.py
│   │   ├── deployment_inspector.py
│   │   ├── network_inspector.py
│   │   └── investigation_service.py
│   ├── ai/               # AI reasoning engine
│   │   ├── prompt_builder.py
│   │   ├── llm_client.py
│   │   ├── root_cause_analyzer.py
│   │   └── fix_recommendation_engine.py
│   ├── services/         # Business logic orchestration
│   ├── models/           # Pydantic schemas
│   ├── main.py           # FastAPI app entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx
│   │       ├── layout.tsx
│   │       └── globals.css
│   ├── package.json
│   └── Dockerfile
├── docs/                 # Documentation
├── prompts/              # AI prompts
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (minikube, kind, or cloud)
- kubectl configured with cluster access
- OpenRouter API key

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-kubernetes-agent
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
KUBECONFIG_PATH=~/.kube/config
```

### 3. Ensure Kubernetes Access

Make sure your kubeconfig is properly configured:

```bash
kubectl config current-context
kubectl get nodes
```

### 4. Start the Application

```bash
docker compose up --build
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Health Check: http://localhost:8000/api/v1/health

## API Endpoints

### GET /api/v1/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-kubernetes-agent"
}
```

### POST /api/v1/investigate
Investigate Kubernetes cluster and return diagnosis

**Request:**
```json
{
  "cluster_name": "optional-cluster-name"
}
```

**Response:**
```json
{
  "status": "success",
  "investigation": {
    "pods": {...},
    "logs": {...},
    "events": {...},
    "deployments": {...},
    "network": {...}
  },
  "diagnosis": {
    "root_cause": "DATABASE_URL missing",
    "explanation": "Application failed during startup",
    "fix": "Add missing environment variable",
    "kubectl_command": "kubectl edit deployment payment-service",
    "prevention": "Use ConfigMaps for configuration",
    "confidence": 92
  }
}
```

### GET /api/v1/clusters
Get list of available Kubernetes clusters

**Response:**
```json
{
  "success": true,
  "clusters": ["minikube", "docker-desktop"],
  "current": "minikube"
}
```

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## How It Works

### 1. Kubernetes Investigation Layer

The system collects evidence from your cluster:

- **Pod Inspector**: Detects unhealthy pods (CrashLoopBackOff, ImagePullBackOff, OOMKilled, etc.)
- **Logs Collector**: Gathers logs from problematic pods
- **Events Analyzer**: Analyzes Kubernetes events for warnings
- **Deployment Inspector**: Checks deployment health and replica status
- **Network Inspector**: Validates services and networking

### 2. AI Reasoning Engine

The collected evidence is sent to an LLM (via OpenRouter) which:

- Analyzes the evidence
- Correlates logs, events, and deployment state
- Identifies root cause
- Suggests actionable fixes
- Provides confidence score

### 3. Frontend Dashboard

Users can:

- Click "Investigate Cluster" to start analysis
- View real-time investigation progress
- See diagnosis with root cause and fix
- Review investigation details

## Troubleshooting

### Backend won't start

- Ensure Docker is running
- Check that port 8000 is not in use
- Verify kubeconfig path is correct

### Frontend won't start

- Ensure Docker is running
- Check that port 3000 is not in use
- Verify backend is running on port 8000

### Investigation fails

- Ensure kubectl is configured: `kubectl config current-context`
- Verify cluster access: `kubectl get nodes`
- Check OpenRouter API key is set
- Review backend logs for errors

## License

MIT

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.