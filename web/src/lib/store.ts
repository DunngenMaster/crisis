import { create } from "zustand"

type EventInfo = {
  type: string
  etaMin: number
  impactAt?: string | null
  locationName?: string | null
}

type AgentOutputs = {
  hazard: any | null
  demand: any | null
  transport: any | null
  shelter: any | null
  resources: any | null
  equity: any | null
  comms: any | null
  plan: any | null
  event: EventInfo | null
  version: number
  updatedAt: string | null
}

type S = AgentOutputs & {
  setAll: (p: Partial<AgentOutputs>) => void
  reset: () => void
}

const init: AgentOutputs = {
  hazard: null,
  demand: null,
  transport: null,
  shelter: null,
  resources: null,
  equity: null,
  comms: null,
  plan: null,
  event: null,
  version: 0,
  updatedAt: null
}

export const usePlanStore = create<S>((set) => ({
  ...init,
  setAll: (p) => set((s) => ({ ...s, ...p })),
  reset: () => set(init)
}))
