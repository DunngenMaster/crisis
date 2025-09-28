export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8080"

export async function uploadScenario(file: File) {
  const fd = new FormData()
  fd.append("file", file)
  const r = await fetch(`${API_BASE}/upload`, { method: "POST", body: fd })
  if (!r.ok) throw new Error("upload failed")
  return r.json()
}

export async function fetchState() {
  const r = await fetch(`${API_BASE}/state`)
  if (!r.ok) throw new Error("state failed")
  return r.json()
}

export async function postQA(query: string) {
  const r = await fetch(`${API_BASE}/qa`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  })
  if (!r.ok) throw new Error("qa failed")
  return r.json()
}
