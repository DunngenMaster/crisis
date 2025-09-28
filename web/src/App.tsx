import TopBar from "./components/TopBar"
import MapCanvas from "./components/MapCanvas"
import ChatPanel from "./components/chatPanel"

export default function App() {
  return (
    <div style={{ display: "grid", gridTemplateRows: "56px 1fr", height: "100vh" }}>
      <TopBar />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", minHeight: 0 }}>
        <div style={{ minHeight: 0, minWidth: 0 }}>
          <MapCanvas />
        </div>
        <aside style={{ borderLeft: "1px solid #222", padding: 16, color: "#d6d6d6", background: "#0f1115" }}>
          <ChatPanel />
        </aside>
      </div>
    </div>
  )
}
