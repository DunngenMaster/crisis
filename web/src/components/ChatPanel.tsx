import { useEffect, useRef, useState } from "react"

type Msg = { role: "user" | "assistant"; content: string }

export default function ChatPanel() {
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: "assistant", content: "Ask about zones, evacuees, priorities, routes, shelters, or impact." }
  ])
  const [q, setQ] = useState("")
  const [busy, setBusy] = useState(false)
  const scRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scRef.current?.scrollTo({ top: scRef.current.scrollHeight })
  }, [msgs])

  async function send() {
    const text = q.trim()
    if (!text) return
    setQ("")
    setMsgs(m => [...m, { role: "user", content: text }])
    setBusy(true)
    try {
      const r = await fetch("http://127.0.0.1:8080/qa",{
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text })
      })
      const data = await r.json()
      const a = data?.answer || "Sorry, I couldn't answer that."
      setMsgs(m => [...m, { role: "assistant", content: a }])
    } catch {
      setMsgs(m => [...m, { role: "assistant", content: "Request failed." }])
    } finally {
      setBusy(false)
    }
  }

  function quick(t: string) {
    setQ(t)
  }

  return (
    <div style={{ height: "100%", display: "grid", gridTemplateRows: "auto 1fr auto", gap: 12, minWidth: 0 }}>
      <div style={{ fontWeight: 600 }}>Crisis GPT</div>
      <div ref={scRef} style={{ border: "1px solid #222", borderRadius: 12, padding: 12, background: "#0f1115", overflow: "auto", minHeight: 0 }}>
        {msgs.map((m, i) => (
          <div key={i} style={{ whiteSpace: "pre-wrap", margin: "8px 0", color: m.role === "user" ? "#eaeaea" : "#9cd2ff" }}>
            <div style={{ fontSize: 12, opacity: .7, marginBottom: 2 }}>{m.role === "user" ? "You" : "Assistant"}</div>
            {m.content}
          </div>
        ))}
      </div>
      <div style={{ display: "grid", gap: 8 }}>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={q}
            onChange={e => setQ(e.target.value)}
            onKeyDown={e => e.key === "Enter" && send()}
            placeholder="Ask: How many people from Zone Z1? Which zone is priority?"
            style={{ flex: 1, padding: "10px 12px", borderRadius: 10, border: "1px solid #2a2f3a", background: "#0f1115", color: "#eaeaea" }}
          />
          <button onClick={send} disabled={busy} style={{ padding: "10px 14px", borderRadius: 10, border: "1px solid #2a2f3a", background: "#17191f", color: "#eaeaea" }}>
            {busy ? "…" : "Send"}
          </button>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button onClick={() => quick("How many people do I need to move from Zone Z1?")} style={chipStyle}>Evacuees Z1</button>
          <button onClick={() => quick("What are the top 3 priority zones?")} style={chipStyle}>Priority zones</button>
          <button onClick={() => quick("What is the minimum route risk margin?")} style={chipStyle}>Route risk</button>
          <button onClick={() => quick("What’s the estimated population in impact?")} style={chipStyle}>Impact pop</button>
          <button onClick={() => quick("What’s total shelter capacity?")} style={chipStyle}>Shelter capacity</button>
        </div>
      </div>
    </div>
  )
}

const chipStyle: React.CSSProperties = {
  padding: "6px 10px",
  borderRadius: 999,
  border: "1px solid #2a2f3a",
  background: "#0f1115",
  color: "#d6d6d6",
  fontSize: 12,
  cursor: "pointer"
}
