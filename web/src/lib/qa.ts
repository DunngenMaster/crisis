export type AppState = {
  hazard?: any
  demand?: any
  transport?: any
  shelter?: any
  resources?: any
  equity?: any
  plan?: any
  event?: any
  version?: number
  updatedAt?: string | null
}

function norm(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim()
}

function takeDemandByZone(demand: any) {
  const out: Record<string, { id: string; name: string; population: number; risk?: number }> = {}
  const feats = demand?.geojson?.features || demand?.features || []
  for (const f of feats) {
    const p = f?.properties || {}
    const id = String(p.id || p.zone_id || p.zone || p.name || "").trim()
    if (!id) continue
    const name = String(p.name || p.zone_name || id)
    const pop = Number(p.population || p.pop || p.demand || p.count || 0)
    const risk = p.risk ?? p.baseline_risk ?? p.priority
    if (!out[id]) out[id] = { id, name, population: 0, risk: typeof risk === "number" ? risk : undefined }
    out[id].population += isFinite(pop) ? pop : 0
    if (typeof risk === "number") out[id].risk = risk
  }
  return Object.values(out)
}

function bestRouteMargin(transport: any) {
  const r = Number(transport?.riskMarginMin)
  return isFinite(r) ? r : undefined
}

function priorityZones(demand: any, hazard: any) {
  const zones = takeDemandByZone(demand)
  zones.sort((a, b) => (b.risk ?? 0) - (a.risk ?? 0) || b.population - a.population)
  return zones
}

export function answer(query: string, state: AppState) {
  const q = norm(query)
  const zones = takeDemandByZone(state.demand)
  if (/how many .*people.*zone/.test(q)) {
    const m = q.match(/zone\s+([a-z0-9\- ]+)/)
    const key = m?.[1]?.trim()
    if (key) {
      const k = norm(key)
      const z = zones.find(z => norm(z.id) === k || norm(z.name).includes(k))
      if (z) return `Estimated evacuees in ${z.name}: ${z.population.toLocaleString()}`
      return `I couldn't find a zone matching "${key}".`
    }
  }
  if (/priority\s+zone|which\s+zone\s+first|evac.*priority/.test(q)) {
    const list = priorityZones(state.demand, state.hazard).slice(0, 3)
    if (list.length) {
      const s = list.map((z, i) => `${i + 1}. ${z.name} (${z.population.toLocaleString()}${z.risk != null ? `, risk ${z.risk}` : ""})`).join("\n")
      return `Top priority zones:\n${s}`
    }
    return "I don't have enough data to rank zones."
  }
  if (/risk\s+margin|min.*risk.*route/.test(q)) {
    const m = bestRouteMargin(state.transport)
    if (m != null) return `Minimum route risk margin: ${m} minutes`
    return "No route risk margin available."
  }
  if (/total\s+impact|population\s+in\s+impact|how many.*affected/.test(q)) {
    const n = Number(state.hazard?.impact_population_total)
    if (isFinite(n)) return `Estimated population in impact: ${Math.round(n).toLocaleString()}`
  }
  if (/shelter\s+capacity|beds|total\s+capacity/.test(q)) {
    const feats = state.shelter?.geojson?.features || []
    let total = 0
    for (const f of feats) total += Number(f?.properties?.capacity || 0)
    if (total > 0) return `Total shelter capacity: ${total.toLocaleString()}`
    return "Shelter capacity data not found."
  }
  if (/help|what can i ask|examples/.test(q)) {
    return [
      "Examples:",
      "• How many people do I need to move from Zone Z1?",
      "• What are the top 3 priority zones?",
      "• What is the minimum route risk margin?",
      "• What’s the estimated population in impact?",
      "• What’s total shelter capacity?"
    ].join("\n")
  }
  return "I can answer about zones, evacuees, priorities, routes, shelters, and impact. Try: “How many people to move from Zone Z1?”"
}
