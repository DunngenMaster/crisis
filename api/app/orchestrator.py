from pathlib import Path
import json
from datetime import datetime, timedelta, timezone

from .swarms.agents.land import land_agent
from .swarms.agents.hazard import hazard_agent
from .swarms.agents.demand import demand_agent
from .swarms.agents.transport import transport_agent
from .swarms.agents.shelter import shelter_agent
from .swarms.agents.resources import resources_agent
from .swarms.agents.equity import equity_agent
from .swarms.agents.comm import comms_agent

def impact_time_agent(scenario, hazard, prev):
    cut = (hazard or {}).get("cutoffs") or {}
    if cut:
        eta = max(10, min(cut.values()))
    else:
        eta = int((scenario.get("event") or {}).get("eta_min", 120))
    return {"eta_min": eta}

def run_pipeline(scenario_path: Path, out_dir: Path, prev: dict):
    scenario = json.loads(scenario_path.read_text())

    land = land_agent(scenario, prev.get("land"))  # <-- NEW
    # Inject land mask into scenario so hazard clips to coastline instead of rectangles
    if land and land.get("geojson"):
        scenario["land_mask"] = land["geojson"]

    hazard = hazard_agent(scenario, prev.get("hazard"))  # uses scenario["land_mask"] if present :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
    demand = demand_agent(scenario, hazard, prev.get("demand"))  # :contentReference[oaicite:2]{index=2}
    transport = transport_agent(scenario, hazard, demand, prev.get("transport"))  # :contentReference[oaicite:3]{index=3}
    shelter = shelter_agent(scenario, hazard, prev.get("shelter"))  # :contentReference[oaicite:4]{index=4}
    resources = resources_agent(scenario, demand, transport, shelter, prev.get("resources"))  # :contentReference[oaicite:5]{index=5}
    equity = equity_agent(scenario, demand, transport, shelter, resources, prev.get("equity"))  # :contentReference[oaicite:6]{index=6}

    it = impact_time_agent(scenario, hazard, prev.get("impact_time"))
    eta_min = it["eta_min"]
    ev_type = (scenario.get("event") or {}).get("type", "tsunami")
    loc_name = (scenario.get("location") or {}).get("name")
    impact_at = (datetime.now(timezone.utc) + timedelta(minutes=eta_min)).isoformat()

    plan = {
        "version": (prev.get("version") or 0) + 1,
        "assignments": transport.get("assignments", []),
        "coverage": resources.get("coverage", 0.0),
        "fairnessIndex": equity.get("fairnessIndex", 1.0),
        "riskMarginMin": transport.get("riskMarginMin", 0),
        "unmetDemand": resources.get("unmetDemand", 0),
    }
    comms = comms_agent(scenario, plan, prev.get("comms"))  # :contentReference[oaicite:7]{index=7}
    event = {"type": ev_type, "etaMin": eta_min, "impactAt": impact_at, "locationName": loc_name}

    outputs = {
        "land": land,  # <-- NEW (so frontend could visualize/debug if desired)
        "hazard": hazard,
        "demand": demand,
        "transport": transport,
        "shelter": shelter,
        "resources": resources,
        "equity": equity,
        "comms": comms,
        "plan": plan,
        "event": event,
        "impact_time": it,
        "version": plan["version"],
        "updatedAt": impact_at,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    for k, v in outputs.items():
        (out_dir / f"{k}.json").write_text(json.dumps(v))
    return outputs
