from shapely.geometry import Point, shape

def shelter_agent(scenario, hazard, prev):
    shelters = scenario.get("shelters", [])
    impact = (hazard or {}).get("impact")
    impact_geom = None
    if impact and impact.get("features"):
        impact_geom = shape(impact["features"][0]["geometry"])

    feats = []
    for s in shelters:
        p = Point(s["coord"][0], s["coord"][1])
        if impact_geom and impact_geom.contains(p):
            continue
        feats.append({
            "type": "Feature",
            "properties": {"id": s["id"], "name": s.get("name", s["id"]), "cap": s.get("capacity", 200)},
            "geometry": {"type": "Point", "coordinates": s["coord"]}
        })
    return {"geojson": {"type": "FeatureCollection", "features": feats}}
