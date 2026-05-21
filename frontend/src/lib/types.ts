export type AttackType = 'stern' | 'bjmm' | 'both'

export interface CrossParameters {
  n: number
  k: number
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
  time: number
  memory: number
  ell: number
  optimal: {
    ell: number
    time: number
    memory: number
  }
  data: DataPoint[]
}

export interface BJMMResult {
  algorithm: string
  n: number
  k: number
  "n-k": number
  time: number
  memory: number
  ell: number
  nu1: number
  nu2: number
  delta1: number
  delta2: number
  optimal: {
    ell: number
    time: number
    memory: number
  }
  data: DataPoint[]
}

export interface EstimationResult {
  stern?: SternResult
  bjmm?: BJMMResult
}