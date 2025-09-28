from shapely.geometry import shape, Polygon
from shapely.ops import unary_union

def demand_agent(scenario, hazard, prev):
    """
    Estimates impacted population per zone by intersecting each zone polygon
    with the hazard impact mask. Also returns a small point FeatureCollection
    (centroids) so you can visualize demand if needed.
    """
    zones = scenario.get("zones", [])
    impact = hazard.get("impact_mask") or hazard.get("impact") or {"type":"FeatureCollection","features":[]}

    merged = None
    if impact["features"]:
        merged = unary_union([shape(f["geometry"]) for f in impact["features"]])

    feats = []
    by_zone = {}
    total_impacted = 0

    for z in zones:
        pop = int(z.get("population", 1000))
        cx, cy = z.get("centroid", (None, None))
        if cx is not None and cy is not None:
            feats.append({"type":"Feature","properties":{"zone":z["id"],"population":pop},"geometry":{"type":"Point","coordinates":[cx,cy]}})

        if z.get("polygon") and merged:
            poly = Polygon(z["polygon"])
            inter = poly.intersection(merged)
            frac = 0.0 if poly.area == 0 else max(0.0, min(1.0, inter.area / poly.area))
        else:
            frac = 0.0 if not impact["features"] else 0.25

        impacted = int(round(pop * frac))
        by_zone[z["id"]] = {"population": pop, "impacted": impacted, "impact_fraction": round(frac, 3)}
        total_impacted += impacted

    return {
        "geojson": {"type":"FeatureCollection","features":feats},
        "by_zone": by_zone,
        "total_impacted": total_impacted
    }
