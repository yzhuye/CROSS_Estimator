import { useState } from 'react'
import { CrossParameters, EstimationResult, AttackType } from '../lib/types'
import { estimateComplexity } from '../services/api'
import { ParameterPanel } from './ParameterPanel'
import { AttackSelector } from './AttackSelector'
import { ResultsDisplay } from './ResultsDisplay'

const DEFAULT_PARAMETERS: CrossParameters = {
  n: 127,
  k: 76,
}

export function EstimatorApp() {
  const [parameters, setParameters] = useState<CrossParameters>(
    DEFAULT_PARAMETERS
  )
  const [selectedAttacks, setSelectedAttacks] = useState<AttackType[]>(["stern"]);
  const [results, setResults] = useState<EstimationResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCalculate = async () => {
    if (selectedAttacks.length === 0) {
      setError('Please select at least one attack')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result: EstimationResult = {}

      // ──── STERN ────────────────────────────────────
      if (selectedAttacks.includes('stern')) {
        result.stern = await estimateComplexity.stern(parameters)
      }

      // ──── BJMM ─────────────────────────────────────
      if (selectedAttacks.includes('bjmm')) {
        result.bjmm = await estimateComplexity.bjmm(parameters)
      }

      setResults(result)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      console.error('[v0] Estimation error:', message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 text-slate-900 dark:text-white">
            CROSS Complexity Estimator
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-300">
            Estimate the computational complexity of attacks against the CROSS
            cryptographic scheme
          </p>
        </div>

        {/* Main content */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left sidebar */}
          <div className="lg:col-span-4 space-y-8">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6 border border-slate-200 dark:border-slate-700">
              <ParameterPanel
                parameters={parameters}
                onParametersChange={setParameters}
                onCalculate={handleCalculate}
                isLoading={isLoading}
              />
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6 border border-slate-200 dark:border-slate-700">
              <AttackSelector
                selectedAttacks={selectedAttacks}
                onAttackChange={setSelectedAttacks}
              />
            </div>
          </div>

          {/* Right content area */}
          <div className="lg:col-span-8">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm p-6 border border-slate-200 dark:border-slate-700">
              <ResultsDisplay
                results={results}
                isLoading={isLoading}
                error={error}
                selectedAttacks={selectedAttacks}
              />
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="mt-12 text-center text-sm text-slate-600 dark:text-slate-400">
          <p>
            This tool estimates attack complexity based on the CROSS
            specification. Results are approximations and should be validated
            against academic literature.
          </p>
        </div>
      </div>
    </div>
  )
}