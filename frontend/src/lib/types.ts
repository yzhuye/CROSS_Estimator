export type AttackType = 'stern' | 'bjmm' | 'groebner' | 'stern_g'

export interface CrossParameters {
  n: number
  k: number
  z: number
  m?: number
  p?: number
}

export interface DataPoint {
  ell: number
  time: number
}

export interface SternResult {
  algorithm: string
  n: number
  k: number
  "n-k": number
  optimal: { ell: number; time: number; memory: number }
  data: DataPoint[]
}

export interface BJMMResult {
  algorithm: string
  n: number
  k: number
  "n-k": number
  optimal: { ell: number; time: number; memory: number }
  data: DataPoint[]
}

export interface GroebnerResult {
  algorithm: string
  n: number
  k: number
  z: number
  omega: number
  optimal: { d_reg: number; time: number | null; memory: number | null }
}

export interface SternGResult {
  algorithm: string
  n: number
  k: number
  m: number
  z: number
  optimal: {
    ell: number | null
    time: number | null
    memory: number | null
  }
  data: DataPoint[]
}

export interface EstimationResult {
  stern?:    SternResult
  bjmm?:     BJMMResult
  groebner?: GroebnerResult
  stern_g?:  SternGResult
}