export type AttackType = 'stern' | 'bjmm' | 'both'

export interface CrossParameters {
  n: number
  k: number
}

export interface SternResult {
  algorithm: string
  n: number
  k: number
  "n-k": number
  time: number
  memory: number
  ell: number
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
}

export interface EstimationResult {
  stern?: SternResult
  bjmm?: BJMMResult
}