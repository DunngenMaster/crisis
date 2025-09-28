from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from .orchestrator import run_pipeline
from .state import State
from .services.qa import answer

app = FastAPI()

# Enable CORS so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent state
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
state = State(DATA_DIR)

# ---------- Models ----------
class StateOut(BaseModel):
    hazard: dict | None
    demand: dict | None
    transport: dict | None
    shelter: dict | None
    resources: dict | None
    equity: dict | None
    comms: dict | None
    plan: dict | None
    event: dict | None
    version: int
    updatedAt: str | None

class QAIn(BaseModel):
    query: str

class QAOut(BaseModel):
    answer: str

# ---------- Routes ----------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    raw = await file.read()
    scenario_path = DATA_DIR / "scenario.json"
    scenario_path.write_bytes(raw)

    outputs = run_pipeline(scenario_path, DATA_DIR, prev=state.snapshot())
    state.set_all(outputs)
    return {"ok": True, "version": state.version}

@app.get("/state", response_model=StateOut)
def get_state():
    return state.snapshot()

@app.post("/qa", response_model=QAOut)
async def qa_endpoint(in_: QAIn):
    # Pass snapshot (dict) instead of State object
    ans = answer(in_.query, state.snapshot())
    return QAOut(answer=ans)
