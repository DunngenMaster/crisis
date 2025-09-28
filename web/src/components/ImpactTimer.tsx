import { useEffect, useMemo, useState } from "react"
import { usePlanStore } from "../lib/store"

function fmt(ms: number) {
  if (ms < 0) return "00:00:00"
  const s = Math.floor(ms / 1000)
  const h = Math.floor(s / 3600).toString().padStart(2, "0")
  const m = Math.floor((s % 3600) / 60).toString().padStart(2, "0")
  const sec = (s % 60).toString().padStart(2, "0")
  return `${h}:${m}:${sec}`
}

export default function ImpactTimer() {
  const ev = usePlanStore((s) => s.event)
  const hazard = usePlanStore((s) => s.hazard)
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [])

  const impactAtMs = useMemo(() => {
    if (!ev) return null
    if (ev.impactAt) {
      const t = Date.parse(ev.impactAt)
      if (!Number.isNaN(t)) return t
    }
    if (typeof ev.etaMin === "number") return Date.now() + ev.etaMin * 60_000
    return null
  }, [ev])

  const remaining = impactAtMs == null ? null : impactAtMs - now
  const affected = hazard?.impact_population_total

  if (!ev) return null

  return (
    <div style={{ position: "absolute", top: 12, left: 12, zIndex: 10 }}>
      <div style={{ background: "rgba(12,14,20,.92)", border: "1px solid #222", borderRadius: 12, padding: "10px 12px", color: "#eaeaea", minWidth: 240 }}>
        <div style={{ fontSize: 12, opacity: .8 }}>{ev.locationName || "Location"}</div>
        <div style={{ fontWeight: 800, marginTop: 4 }}>{(ev.type || "Event").toUpperCase()} Expected Impact Time</div>
        <div style={{ fontSize: 28, lineHeight: "32px", marginTop: 2 }}>{remaining != null ? fmt(remaining) : "--:--:--"}</div>
        {typeof affected === "number" && <div style={{ fontSize: 12, opacity: .85, marginTop: 6 }}>Est. population in impact: {affected.toLocaleString()}</div>}
      </div>
    </div>
  )
}
