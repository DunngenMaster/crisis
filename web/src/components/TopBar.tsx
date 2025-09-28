import { useRef, useState } from "react"
import { usePlanStore } from "../lib/store"
import { uploadScenario, fetchState } from "../lib/api"

export default function TopBar() {
  const inputRef = useRef<HTMLInputElement>(null)
  const setAll = usePlanStore((s) => s.setAll)
  const [busy, setBusy] = useState(false)

  async function onPick(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (!f) return
    setBusy(true)
    try {
      await uploadScenario(f)
      const state = await fetchState()
      setAll({
        hazard: state.hazard,
        demand: state.demand,
        transport: state.transport,
        shelter: state.shelter,
        resources: state.resources,
        equity: state.equity,
        comms: state.comms,
        plan: state.plan,
        event: state.event,
        version: state.version,
        updatedAt: state.updatedAt
      })
    } finally {
      setBusy(false)
      if (inputRef.current) inputRef.current.value = ""
    }
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", borderBottom: "1px solid #222", background: "#0f1115", color: "#eaeaea" }}>
      <div style={{ fontWeight: 600 }}>Urban Crisis Planner</div>
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 10 }}>
        <button onClick={() => inputRef.current?.click()} disabled={busy} style={{ background: "#17191f", border: "1px solid #2a2f3a", padding: "8px 12px", borderRadius: 8, color: "#eaeaea", cursor: "pointer" }}>
          {busy ? "Processing…" : "Upload Scenario"}
        </button>
        <input ref={inputRef} type="file" accept=".json,.zip" style={{ display: "none" }} onChange={onPick} />
      </div>
    </div>
  )
}
