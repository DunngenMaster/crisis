# Urban Crisis Response Planner

A web application that demonstrates how AI agents can coordinate disaster management in real time.  
It simulates an urban tsunami scenario for San Francisco, visualizing hazard zones, evacuation routes, shelters, and enabling a Crisis GPT chatbot for interactive planning queries.

## Features

- Interactive Map (Mapbox GL)  
  - Hazard zones (low/medium/high risk)  
  - Tsunami impact area overlay  
  - Transport routes with traffic-aware routing  
  - Shelter locations with capacity markers  

- Real-time Timer  
  - Countdown to expected impact  
  - Population at risk indicator  

- Scenario Upload  
  - Upload JSON scenarios with zones, demand, transport, and shelters  
  - Backend pipeline regenerates hazard, demand, transport, resources, and equity data  

- Crisis GPT  
  - Ask natural language questions such as:  
    - How many people do I need to move from Zone Z1?  
    - What are the top 3 priority zones?  
    - What is the minimum route risk margin?  
    - What is the estimated population in impact?  
    - What is total shelter capacity?  

## Architecture

Frontend: React + TypeScript + Vite  
- `MapCanvas.tsx` renders map layers (hazard, impact, routes, shelters, demand)  
- `ImpactTimer.tsx` shows countdown  
- `ChatPanel.tsx` connects to `/qa` endpoint for the Crisis GPT interface  
- `TopBar.tsx` allows uploading scenarios  

Backend: FastAPI (Python)  
- `/upload` runs `orchestrator.py` pipeline of agents: hazard, demand, transport, shelter, resources, equity, comm  
- `/state` serves current state as JSON  
- `/qa` answers natural-language questions using `services/qa.py` against the in-memory state  

## Getting Started

### Backend (FastAPI)
```bash
cd api
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
