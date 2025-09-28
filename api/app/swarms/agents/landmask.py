# api/app/swarms/agents/landmask.py
from pathlib import Path
import json
from shapely.geometry import Polygon, MultiPolygon, shape
from shapely.ops import unary_union

def _load_landmask_from_scenario(scenario):
    feats = (scenario.get("land_mask") or {}).get("features")
    if not feats:
        return None
    polys = []
    for f in feats:
        try:
            g = shape(f["geometry"])
            if isinstance(g, (Polygon, MultiPolygon)) and not g.is_empty:
                polys.append(g)
        except Exception:
            continue
    return unary_union(polys).buffer(0) if polys else None

def _load_landmask_from_file(path: Path):
    try:
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        feats = data.get("features") or []
        polys = []
        for f in feats:
            try:
                g = shape(f["geometry"])
                if isinstance(g, (Polygon, MultiPolygon)) and not g.is_empty:
                    polys.append(g)
            except Exception:
                continue
        return unary_union(polys).buffer(0) if polys else None
    except Exception:
        return None

def _land_union_from_zones(scenario):
    zones = scenario.get("zones") or []
    geoms = []
    for z in zones:
        if z.get("polygon"):
            try:
                geoms.append(Polygon(z["polygon"]))
            except Exception:
                pass
    return unary_union(geoms).buffer(0.0008) if geoms else None

def resolve_landmask(scenario, data_dir: Path):
    """
    Returns a shapely geometry representing land:
    1) scenario.land_mask (if provided)
    2) data/ne_50m_land.geojson (if present)
    3) union of zone polygons (fallback)
    """
    lm = _load_landmask_from_scenario(scenario)
    if lm is not None:
        return lm
    ne = _load_landmask_from_file(data_dir / "ne_50m_land.geojson")
    if ne is not None:
        return ne
    return _land_union_from_zones(scenario)

__all__ = ["resolve_landmask"]
