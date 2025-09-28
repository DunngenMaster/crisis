import { useState } from "react"
import { proposeCoastAnchor } from "../lib/smartAnchor"

export default function SmartAnchor({ onPick }:{ onPick:(c:[number,number])=>void }) {
  const [q, setQ] = useState("")
  const [busy, setBusy] = useState(false)
  async function go() {
    setBusy(true)
    const c = await proposeCoastAnchor(q)
    setBusy(false)
    if (c) onPick(c)
  }
  return (
    <div style={{ display:"flex", gap:8 }}>
      <input value={q} onChange={e=>setQ(e.target.value)} placeholder="City or coastline (e.g., San Francisco Ocean Beach)" />
      <button onClick={go} disabled={busy}>{busy ? "Finding…" : "Suggest Anchor"}</button>
    </div>
  )
}
