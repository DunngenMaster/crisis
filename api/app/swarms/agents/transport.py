import math
from typing import Dict, Any, List
from shapely.geometry import shape, Point

def _haversine_km(a, b):
    from math import radians, sin, cos, sqrt, atan2
    lon1, lat1 = a
    lon2, lat2 = b
    R = 6371.0
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    x = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(math.sqrt(x), math.sqrt(1 - x))
    return R * c

def _nearest_shelter(z_centroid, shelters):
    best = None
    best_km = 1e9
    for s in shelters:
        d = _haversine_km(z_centroid, s["coord"])
        if d < best_km:
            best_km = d
            best = s
    return best, best_km

def transport_agent(scenario: Dict[str, Any], hazard: Dict[str, Any], demand: Dict[str, Any], prev: Dict[str, Any] | None):
    base_zones: List[Dict[str, Any]] = scenario.get("zones", [])
    gen_zones: List[Dict[str, Any]] = (hazard or {}).get("generated_zones") or []
    zones: List[Dict[str, Any]] = base_zones + gen_zones

    # Downsample routes for generated sub-zones to reduce clutter
    route_every = int(((scenario.get("auto_subzones") or {}).get("route_every", 4)))
    def _skip_generated(zid: str) -> bool:
        if not zid.startswith("auto-"):
            return False
        try:
            n = int(zid.split("-")[1])
        except Exception:
            return True
        return (n % max(route_every, 1)) != 0

    raw_shelters: List[Dict[str, Any]] = scenario.get("shelters", [])

    impact = (hazard or {}).get("impact")
    impact_geom = None
    if impact and impact.get("features"):
        impact_geom = shape(impact["features"][0]["geometry"])

    safe_shelters = []
    for s in raw_shelters:
        p = Point(s["coord"][0], s["coord"][1])
        if impact_geom and impact_geom.contains(p):
            continue
        safe_shelters.append(s)

    routes = []
    assignments = []
    MIN_PER_KM = 3.0
    cutoffs = (hazard or {}).get("cutoffs", {}) or {}
    impacted_zone_ids = set(((hazard or {}).get("impact_by_zone") or {}).keys())
    risk_margins = []

    for z in zones:
        zid = z.get("id")
        if zid not in impacted_zone_ids:
            continue
        if not z.get("centroid"):
            continue
        if not safe_shelters:
            continue
        if _skip_generated(zid):
            continue

        s, km = _nearest_shelter(z["centroid"], safe_shelters)
        eta_min = max(1, int(round(km * MIN_PER_KM)))
        z_name = z.get("name", zid or "Z")
        s_name = s.get("name", s.get("id", "S"))
        cutoff = int(cutoffs.get(zid, 60))
        risk_margin = cutoff - eta_min
        risk_margins.append(risk_margin)

        routes.append({
            "type": "Feature",
            "properties": {
                "from": z_name,
                "to": s_name,
                "eta_min": eta_min,
                "label": f"{z_name} → {s_name} ({eta_min} min)"
            },
            "geometry": {"type": "LineString", "coordinates": [z["centroid"], s["coord"]]}
        })

        assignments.append({
            "zone": zid,
            "shelter": s.get("id"),
            "eta_min": eta_min,
            "risk_margin": risk_margin
        })

    routes_fc = {"type": "FeatureCollection", "features": routes}
    min_margin = min(risk_margins) if risk_margins else 0
    return {"routes": routes_fc, "assignments": assignments, "riskMarginMin": min_margin}
