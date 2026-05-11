export interface CrossParameters {
  n: number
  k: number
}

export interface BJMMResult {
  time: number
  memory: number
}

export interface SternResult {
  time: number
  memory: number
  l: number
}

export interface EstimationResult {
  bjmm?: BJMMResult
  stern?: SternResult
}

export type AttackType = 'bjmm' | 'stern' | 'both'
