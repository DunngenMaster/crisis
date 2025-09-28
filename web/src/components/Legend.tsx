import { useState } from "react"

export default function Legend({ showImpact, setShowImpact }:{showImpact:boolean; setShowImpact:(v:boolean)=>void}) {
  return (
    <div style={{ position: "absolute", top: 12, right: 12, zIndex: 10 }}>
      <div style={{ background: "rgba(12,14,20,.92)", border: "1px solid #222", borderRadius: 12, padding: 12, color: "#eaeaea", minWidth: 220 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>Legend</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", marginBottom: 6 }}>
          <input type="checkbox" checked={showImpact} onChange={(e)=>setShowImpact(e.target.checked)} />
          <span>Impact area (under water)</span>
        </label>
        <div style={{ marginLeft: 22, marginBottom: 6 }}><span style={{ background:"#ff6b00", padding:"2px 6px", borderRadius:4, marginRight:6 }}></span>Hazard zones</div>
        <div style={{ marginLeft: 22, marginBottom: 6 }}><span style={{ borderBottom:"3px dashed #4ea1ff", paddingRight:24 }}></span> Transport routes</div>
        <div style={{ marginLeft: 22 }}><span style={{ width:10, height:10, background:"#22c55e", display:"inline-block", borderRadius:999, marginRight:10 }}></span> Shelters</div>
      </div>
    </div>
  )
}
