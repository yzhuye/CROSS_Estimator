import { CrossParameters, SternResult } from '../lib/types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const estimateComplexity = {
  stern: async (params: CrossParameters): Promise<SternResult> => {
    const response = await fetch(`${API_BASE}/cross`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`Stern estimation failed: ${response.statusText}`)
    }

    return response.json()
  },
}
