from shapely.geometry import Polygon, MultiPolygon, Point, box, mapping, MultiPoint
from shapely.ops import unary_union, voronoi_diagram
import math, random
from pathlib import Path
from .landmask import resolve_landmask

KM_DEG = 1 / 111.32

def _amoeba_blob(center, radius_km=5.0, lobes=5, jitter=0.3):
    lon, lat = center
    r = radius_km * KM_DEG
    pts = []
    steps = max(36, lobes * 24)
    for i in range(steps):
        t = 2 * math.pi * i / steps
        wobble = 1 + jitter * 0.5 * math.sin(lobes * t + 0.7) + jitter * 0.3 * random.uniform(-1, 1)
        rr = r * wobble
        pts.append((lon + rr * math.cos(t), lat + rr * math.sin(t)))
    return Polygon(pts).buffer(0.002)

def _impact_polygon_raw(scenario):
    seed = (scenario.get("impact_seed") or {})
    center = seed.get("coastline_anchor") or (scenario.get("location") or {}).get("center")
    if not center:
        return None
    radius = float(seed.get("radius_km", 5.0))
    lobes = int(seed.get("lobes", 5))
    jitter = float(seed.get("jitter", 0.3))
    return _amoeba_blob(center, radius, lobes, jitter)

def _iter_polys(geom):
    if geom is None:
        return
    if isinstance(geom, Polygon):
        if not geom.is_empty:
            yield geom
        return
    if isinstance(geom, MultiPolygon):
        for g in geom.geoms:
            if not g.is_empty:
                yield g
        return
    try:
        for g in geom.geoms:
            if isinstance(g, (Polygon, MultiPolygon)) and not g.is_empty:
                yield from _iter_polys(g)
    except Exception:
        return

def _largest_polygon(geom):
    best = None
    best_area = 0.0
    for g in _iter_polys(geom):
        a = g.area
        if a > best_area:
            best = g
            best_area = a
    return best

def _land_union_from_zones(scenario):
    zones = scenario.get("zones") or []
    geoms = []
    for z in zones:
        if z.get("polygon"):
            try:
                geoms.append(Polygon(z["polygon"]))
            except Exception:
                pass
    if not geoms:
        return None
    return unary_union(geoms).buffer(0.0008)

def _clip_impact_to_land(impact_poly, scenario):
    if impact_poly is None:
        return None
    data_dir = Path(__file__).resolve().parents[2] / "data"
    land_union = resolve_landmask(scenario, data_dir)
    if land_union is None:
        return impact_poly
    inter = impact_poly.intersection(land_union)
    if inter.is_empty:
        return None
    return inter.buffer(0)

def _densify_polygon(poly: Polygon, max_seg_km=0.05):
    max_seg_deg = max_seg_km * KM_DEG
    def densify_ring(coords):
        out = []
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            out.append((x1, y1))
            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            n = max(0, int(dist / max_seg_deg) - 1)
            for j in range(1, n + 1):
                t = j / (n + 1)
                out.append((x1 + dx * t, y1 + dy * t))
        out.append(coords[-1])
        return out
    ext = densify_ring(list(poly.exterior.coords))
    holes = [densify_ring(list(r.coords)) for r in poly.interiors]
    return Polygon(ext, holes).buffer(0)

def _densify_any(geom, max_seg_km=0.05):
    parts = []
    for g in _iter_polys(geom):
        parts.append(_densify_polygon(g, max_seg_km))
    if not parts:
        return None
    return unary_union(parts).buffer(0)

def _poly_area_km2(poly: Polygon, lat_ref=None):
    if lat_ref is None:
        lat_ref = poly.centroid.y
    km_per_deg_lat = 111.32
    km_per_deg_lon = 111.32 * math.cos(math.radians(lat_ref))
    return poly.area * km_per_deg_lat * km_per_deg_lon

def _random_point_in_poly(poly: Polygon):
    minx, miny, maxx, maxy = poly.bounds
    for _ in range(1000):
        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        p = Point(x, y)
        if poly.contains(p):
            return p
    return poly.representative_point()

def _poisson_points(poly: Polygon, count: int):
    pts = []
    for _ in range(count):
        pts.append(_random_point_in_poly(poly))
    return pts

def _centroid_of(poly: Polygon):
    c = poly.representative_point()
    return Point(c.x, c.y)

def _lloyd_relax(poly: Polygon, pts, iterations=2):
    for _ in range(iterations):
        mp = MultiPoint(pts)
        vd = voronoi_diagram(mp, envelope=poly.envelope.buffer(1.0), tolerance=0.0)
        new_pts = []
        for cell in vd.geoms:
            cell_clip = cell.intersection(poly)
            for g in _iter_polys(cell_clip):
                new_pts.append(_centroid_of(g))
        if new_pts:
            pts = new_pts
    return pts

def _voronoi_cells(poly: Polygon, pts):
    mp = MultiPoint(pts)
    vd = voronoi_diagram(mp, envelope=poly.envelope.buffer(1.0), tolerance=0.0)
    cells = []
    for cell in vd.geoms:
        cell_clip = cell.intersection(poly)
        for g in _iter_polys(cell_clip):
            cells.append(g)
    return cells

def _min_distance_to_boundary_km(poly_like, point: Point):
    min_deg = None
    for p in _iter_polys(poly_like):
        d = point.distance(p.exterior)
        if min_deg is None or d < min_deg:
            min_deg = d
    if min_deg is None:
        return 0.0
    km_per_deg_lat = 111.32
    km_per_deg_lon = 111.32 * math.cos(math.radians(point.y))
    return min_deg * max(km_per_deg_lat, km_per_deg_lon)

def _generate_voronoi_subzones(impact_poly, scenario):
    if impact_poly is None or impact_poly.is_empty:
        return []

    conf = (scenario.get("auto_subzones") or {})
    target_km2 = float(conf.get("target_km2", 0.6))
    count = conf.get("count")
    density_default = float((scenario.get("defaults") or {}).get("density_per_km2", 4000))
    cutoff_min = int((scenario.get("defaults") or {}).get("cutoff_min", 60))

    area_km2 = _poly_area_km2(impact_poly)
    n_core = int(max(1, round(area_km2 / target_km2))) if not count else int(count)

    dens = _densify_any(impact_poly, max_seg_km=0.15)
    main_poly = _largest_polygon(dens) or _largest_polygon(impact_poly) or next(_iter_polys(impact_poly))
    boundary = list(main_poly.exterior.coords)

    boundary_pts = []
    skip = max(1, len(boundary) // max(n_core // 2, 1))
    for i, (x, y) in enumerate(boundary):
        if i % skip == 0:
            boundary_pts.append(Point(x, y))

    core_pts = _poisson_points(main_poly, n_core)
    pts = _lloyd_relax(main_poly, boundary_pts + core_pts, iterations=2)
    cells = _voronoi_cells(main_poly, pts)

    subzones = []
    idx = 1
    for g in cells:
        km2 = _poly_area_km2(g)
        if km2 < target_km2 * 0.25:
            continue

        est_pop = int(round(km2 * density_default))
        dens_val = est_pop / max(km2, 1e-6)

        c = g.representative_point()
        dist_km = _min_distance_to_boundary_km(main_poly, c)

        edge_risk = max(0.0, min(1.0, 1.0 - (dist_km / 1.5)))
        dens_risk = max(0.0, min(1.0, dens_val / 9000.0))
        risk = round(0.6 * edge_risk + 0.4 * dens_risk, 3)

        if risk >= 0.66:
            band = "red"
        elif risk >= 0.33:
            band = "orange"
        else:
            band = "green"

        subzones.append({
            "id": f"auto-{idx}",
            "name": f"Impact Subzone {idx}",
            "label": idx,
            "polygon": list(g.exterior.coords),
            "centroid": [c.x, c.y],
            "population": est_pop,
            "density_per_km2": int(dens_val),
            "cutoff_min": cutoff_min,
            "risk": risk,
            "risk_band": band,
            "generated": True
        })
        idx += 1
    return subzones

def hazard_agent(scenario, prev):
    # Build and clip impact to land, then densify (works for Polygon or MultiPolygon)
    impact_raw = _impact_polygon_raw(scenario)
    impact_poly = _clip_impact_to_land(impact_raw, scenario)
    if impact_poly:
        impact_poly = _densify_any(impact_poly, max_seg_km=0.05)

    zones = scenario.get("zones") or []
    cutoffs, per_zone = {}, {}
    impacted_zone_features = []
    affected_total = 0

    # Authored zones intersecting the impact
    if impact_poly:
        for z in zones:
            cutoffs[z["id"]] = z.get("cutoff_min", 60)
            if not z.get("polygon"):
                continue
            try:
                poly = Polygon(z["polygon"])
            except Exception:
                continue
            inter = poly.intersection(impact_poly)
            if not inter.is_empty:
                frac = inter.area / poly.area if poly.area else 0.0
                est = int(round(frac * z.get("population", 0)))
                per_zone[z["id"]] = {
                    "population": z.get("population", 0),
                    "affected_est": est,
                    "impact_fraction": frac
                }
                affected_total += est
                baseline = z.get("baseline_risk", 0.3)
                band = "red" if baseline >= 0.66 else "orange" if baseline >= 0.33 else "green"
                impacted_zone_features.append({
                    "type": "Feature",
                    "properties": {
                        "zone": z["id"],
                        "name": z.get("name"),
                        "severity": baseline,
                        "risk_band": band
                    },
                    "geometry": mapping(poly)
                })

    # Generated sub-zones
    generated = _generate_voronoi_subzones(impact_poly, scenario) if impact_poly else []
    for gz in generated:
        cutoffs[gz["id"]] = gz.get("cutoff_min", 60)
        per_zone[gz["id"]] = {
            "population": gz["population"],
            "affected_est": gz["population"],
            "impact_fraction": 1.0
        }
        affected_total += gz["population"]
        impacted_zone_features.append({
            "type": "Feature",
            "properties": {
                "zone": gz["id"],
                "name": gz["name"],
                "generated": True,
                "risk": gz["risk"],
                "risk_band": gz["risk_band"]
            },
            "geometry": mapping(Polygon(gz["polygon"]))
        })

    impact_geo = None
    if impact_poly:
        impact_geo = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "properties": {"type": "impact"}, "geometry": mapping(impact_poly)}
            ]
        }

    return {
        "geojson": {"type": "FeatureCollection", "features": impacted_zone_features},
        "cutoffs": cutoffs,
        "impact": impact_geo,
        "impact_population_total": affected_total,
        "impact_by_zone": per_zone,
        "generated_zones": generated
    }
