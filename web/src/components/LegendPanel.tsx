import React from "react"

export default function LegendPanel({
  showImpact,
  setShowImpact,
  compact = false
}: {
  showImpact: boolean
  setShowImpact: (v: boolean) => void
  compact?: boolean
}) {
  return (
    <div
      style={{
        background: "rgba(15,15,15,0.85)",
        color: "#fff",
        borderRadius: 12,
        padding: compact ? "10px 12px" : "14px 16px",
        boxShadow: "0 6px 20px rgba(0,0,0,0.35)",
        minWidth: 240
      }}
    >
      <div style={{ fontWeight: 700, marginBottom: 10 }}>Legend</div>

      <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10, cursor: "pointer" }}>
        <input type="checkbox" checked={showImpact} onChange={(e) => setShowImpact(e.target.checked)} />
        <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
          <span
            style={{
              width: 14,
              height: 14,
              borderRadius: 2,
              background: "#60a5fa",
              display: "inline-block",
              opacity: 0.6
            }}
          />
          Impact area (under water)
        </span>
      </label>

      <div style={{ fontSize: 12, opacity: 0.85, marginBottom: 6 }}>Risk zones</div>
      <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", rowGap: 6, columnGap: 8, marginBottom: 10 }}>
        <span style={{ width: 14, height: 14, borderRadius: 2, background: "#22c55e", opacity: 0.6 }} />
        <span>Low</span>
        <span style={{ width: 14, height: 14, borderRadius: 2, background: "#f59e0b", opacity: 0.6 }} />
        <span>Medium</span>
        <span style={{ width: 14, height: 14, borderRadius: 2, background: "#ef4444", opacity: 0.6 }} />
        <span>High</span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
        <span
          style={{
            width: 28,
            height: 0,
            borderTop: "3px dashed #4ea1ff",
            display: "inline-block"
          }}
        />
        <span>Transport routes</span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span
          style={{
            width: 14,
            height: 14,
            borderRadius: 7,
            background: "#22c55e",
            border: "2px solid #052e1a",
            display: "inline-block"
          }}
        />
        <span>Shelters</span>
      </div>
    </div>
  )
}
