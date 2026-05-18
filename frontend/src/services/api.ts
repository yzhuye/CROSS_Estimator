import { CrossParameters, SternResult, BJMMResult } from '../lib/types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const estimateComplexity = {
  stern: async (params: CrossParameters): Promise<SternResult> => {
    const res = await fetch(`${API_BASE}/cross/stern`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    })
    if (!res.ok) throw new Error(`Stern failed: ${res.statusText}`)
    return res.json()
  },

  bjmm: async (params: CrossParameters): Promise<BJMMResult> => {
    const res = await fetch(`${API_BASE}/cross/bjmm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    })
    if (!res.ok) throw new Error(`BJMM failed: ${res.statusText}`)
    return res.json()
  },
}