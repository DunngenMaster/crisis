from shapely.geometry import Polygon, mapping

def _sf_peninsula_mask():
    # Rough but coastline-shaped outline for San Francisco peninsula (clockwise)
    coords = [
        (-122.5300, 37.7000), (-122.5245, 37.7075), (-122.5185, 37.7135),
        (-122.5145, 37.7200), (-122.5115, 37.7280), (-122.5095, 37.7380),
        (-122.5085, 37.7485), (-122.5075, 37.7585), (-122.5050, 37.7720),
        (-122.5000, 37.7880), (-122.4920, 37.8010), (-122.4800, 37.8095),
        (-122.4675, 37.8130), (-122.4520, 37.8140), (-122.4355, 37.8125),
        (-122.4185, 37.8100), (-122.4065, 37.8100), (-122.3975, 37.8085),
        (-122.3895, 37.8040), (-122.3810, 37.7975), (-122.3755, 37.7920),
        (-122.3715, 37.7835), (-122.3700, 37.7715), (-122.3715, 37.7570),
        (-122.3755, 37.7450), (-122.3810, 37.7350), (-122.3890, 37.7230),
        (-122.3970, 37.7135), (-122.4065, 37.7075), (-122.4170, 37.7035),
        (-122.4280, 37.7005), (-122.4415, 37.6985), (-122.4580, 37.6985),
        (-122.4760, 37.7000), (-122.4950, 37.7040), (-122.5120, 37.7080),
        (-122.5250, 37.7105), (-122.5300, 37.7000)
    ]
    poly = Polygon(coords).buffer(0)
    return {"type": "FeatureCollection",
            "features": [{"type": "Feature",
                          "properties": {"name": "SF_land"},
                          "geometry": mapping(poly)}]}

def land_agent(scenario, prev):
    loc_name = ((scenario.get("location") or {}).get("name") or "").lower()
    if "san francisco" in loc_name or not scenario.get("land_mask"):
        geo = _sf_peninsula_mask()
    else:
        # Fallback to whatever is already in scenario (if present)
        geo = scenario.get("land_mask")
    return {"geojson": geo}
