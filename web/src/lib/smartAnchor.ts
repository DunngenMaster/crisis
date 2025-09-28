export async function proposeCoastAnchor(
  place: string,
  toast?: (m: string) => void
): Promise<[number, number] | null> {
  try {
    const mb = import.meta.env.VITE_MAPBOX_TOKEN
    if (mb) {
      const q = encodeURIComponent(place)
      const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${q}.json?limit=1&access_token=${mb}`
      const r = await fetch(url)
      if (r.ok) {
        const j = await r.json()
        const c = j?.features?.[0]?.center
        if (Array.isArray(c) && c.length === 2) return c as [number, number]
      }
    }
  } catch {}
  try {
    const k = import.meta.env.VITE_OPENAI_API_KEY
    if (!k) return null
    const prompt = `Return a JSON object with "lon" and "lat" for a coastline point suitable as tsunami impact anchor for ${place}. Prefer an exposed, open-ocean shoreline near the city.`
    const r = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${k}` },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: prompt }],
        response_format: { type: "json_object" }
      })
    })
    if (!r.ok) return null
    const j = await r.json()
    const txt = j?.choices?.[0]?.message?.content
    const o = JSON.parse(txt || "{}")
    const lon = Number(o?.lon), lat = Number(o?.lat)
    if (Number.isFinite(lon) && Number.isFinite(lat)) return [lon, lat]
  } catch {}
  return null
}
