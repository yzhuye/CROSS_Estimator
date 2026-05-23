import { CrossParameters, SternResult, BJMMResult, GroebnerResult, SternGResult } from '../lib/types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function post<T>(path: string, params: CrossParameters): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`${path} failed: ${res.statusText}`)
  return res.json()
}

export const estimateComplexity = {
  stern:    (p: CrossParameters) => post<SternResult>('/cross/stern', p),
  bjmm:     (p: CrossParameters) => post<BJMMResult>('/cross/bjmm', p),
  groebner: (p: CrossParameters) => post<GroebnerResult>('/cross/groebner', p),
  stern_g:  (p: CrossParameters) => post<SternGResult>('/rsdpg/stern', p),
}