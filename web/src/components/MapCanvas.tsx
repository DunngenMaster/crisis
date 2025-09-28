const MAPBOX_TOKEN = "pk.eyJ1IjoiYXNodXRvc2hrdW1hd2F0IiwiYSI6ImNtZzJycmtlMjExcTcyam9pNGZmejBwaGIifQ.8XK87_UyRkn5YoJofBiAQQ"

import "mapbox-gl/dist/mapbox-gl.css"
import { useEffect, useMemo, useState } from "react"
import Map, { Source, Layer } from "react-map-gl"
import { usePlanStore } from "../lib/store"
import ImpactTimer from "./ImpactTimer"
import LegendPanel from "./LegendPanel"

const INIT = { longitude: -122.431297, latitude: 37.773972, zoom: 12 }

async function getRouteGeoJSON(start: [number, number], end: [number, number]) {
  const url =
    `https://api.mapbox.com/directions/v5/mapbox/driving-traffic/` +
    `${start[0]},${start[1]};${end[0]},${end[1]}?overview=full&geometries=geojson&access_token=${MAPBOX_TOKEN}`
  const res = await fetch(url)
  if (!res.ok) throw new Error("Directions API failed")
  const data = await res.json()
  const geom = data?.routes?.[0]?.geometry
  if (!geom) throw new Error("No route")
  return { type: "Feature", properties: {}, geometry: geom } as GeoJSON.Feature
}

export default function MapCanvas() {
  const hazard = usePlanStore((s) => s.hazard)
  const transport = usePlanStore((s) => s.transport)
  const shelters = usePlanStore((s) => s.shelter)
  const demand = usePlanStore((s) => s.demand)

  const hazardGeo = useMemo(() => hazard?.geojson || hazard?.threat_boxes || null, [hazard])
  const impactGeo = useMemo(() => hazard?.impact || hazard?.impact_mask || null, [hazard])
  const routesGeo = useMemo(() => transport?.routes || null, [transport])
  const sheltersGeo = useMemo(() => shelters?.geojson || null, [shelters])
  const demandGeo = useMemo(() => demand?.geojson || null, [demand])

  const [view, setView] = useState(INIT)
  const [showImpact, setShowImpact] = useState(true)
  const [roadRoutes, setRoadRoutes] = useState<GeoJSON.FeatureCollection | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      if (!routesGeo?.features?.length) {
        setRoadRoutes(null)
        return
      }
      const out: GeoJSON.Feature[] = []
      for (const f of routesGeo.features) {
        if (f.geometry?.type !== "LineString") continue
        const coords = (f.geometry as any).coordinates as [number, number][]
        if (!coords?.length) continue
        const start = coords[0]
        const end = coords[coords.length - 1]
        try {
          const routed = await getRouteGeoJSON(start, end)
          out.push({ ...routed, properties: { ...(f.properties || {}), style: "route_dotted" } })
        } catch {
          out.push(f)
        }
        if (cancelled) return
      }
      if (!cancelled) setRoadRoutes({ type: "FeatureCollection", features: out })
    })()
    return () => {
      cancelled = true
    }
  }, [routesGeo])

  if (!MAPBOX_TOKEN) return <div style={{ color: "#ddd", padding: 16 }}>Add Mapbox token</div>

  return (
    <div style={{ position: "relative", width: "100%", minHeight: "calc(100vh - 64px)" }}>
      <ImpactTimer />
      <div style={{ position: "absolute", top: 12, right: 12, zIndex: 10 }}>
        <LegendPanel showImpact={showImpact} setShowImpact={setShowImpact} compact />
      </div>

      <Map
        mapboxAccessToken={MAPBOX_TOKEN}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        initialViewState={view}
        onMove={(e) => setView(e.viewState)}
        style={{ position: "absolute", inset: 0 }}
        reuseMaps
      >
        {/* Risk-colored subzones from hazard.geojson */}
        {hazardGeo && (
          <Source id="hazard" type="geojson" data={hazardGeo}>
            <Layer
              id="hazard-fill-risk"
              type="fill"
              paint={{
                "fill-color": [
                  "match",
                  ["get", "risk_band"],
                  "red", "#ef4444",
                  "orange", "#f97316",
                  "green", "#22c55e",
                  "#22c55e"
                ],
                "fill-opacity": 0.25
              }}
            />
            <Layer
              id="hazard-line-basezones"
              type="line"
              paint={{ "line-color": "#9aa0a6", "line-width": 1 }}
            />
          </Source>
        )}

        {showImpact && impactGeo && (
          <Source id="impact" type="geojson" data={impactGeo}>
            <Layer id="impact-fill" type="fill" paint={{ "fill-color": "#60a5fa", "fill-opacity": 0.2 }} />
            <Layer id="impact-line" type="line" paint={{ "line-color": "#60a5fa", "line-width": 1.5, "line-opacity": 0.9 }} />
          </Source>
        )}

        {(roadRoutes || routesGeo) && (
          <Source id="routes" type="geojson" data={roadRoutes || routesGeo!}>
            <Layer id="routes-line" type="line" paint={{ "line-color": "#4ea1ff", "line-width": 3, "line-dasharray": [2, 2] }} />
          </Source>
        )}

        {sheltersGeo && (
          <Source id="shelters" type="geojson" data={sheltersGeo}>
            <Layer
              id="shelters-circle"
              type="circle"
              paint={{
                "circle-radius": 6,
                "circle-stroke-width": 2,
                "circle-color": "#22c55e",
                "circle-stroke-color": "#052e1a"
              }}
            />
          </Source>
        )}

        {demandGeo && (
          <Source id="demand" type="geojson" data={demandGeo}>
            <Layer id="demand-circle" type="circle" paint={{ "circle-radius": 4, "circle-color": "#38bdf8" }} />
          </Source>
        )}
      </Map>
    </div>
  )
}
