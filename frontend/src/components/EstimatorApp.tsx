import { useState } from 'react'
import { Activity, Binary, Braces, ShieldCheck } from 'lucide-react'
import { CrossParameters, EstimationResult, AttackType } from '../lib/types'
import { estimateComplexity } from '../services/api'
import { ParameterPanel } from './ParameterPanel'
import { AttackSelector } from './AttackSelector'
import { ResultsDisplay } from './ResultsDisplay'

const DEFAULT_PARAMETERS: CrossParameters = { n: 127, k: 76, z: 7 }

export function EstimatorApp() {
  const [parameters, setParameters] = useState<CrossParameters>(DEFAULT_PARAMETERS)
  const [selectedAttacks, setSelectedAttacks] = useState<AttackType[]>(['stern'])
  const [results, setResults] = useState<EstimationResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCalculate = async () => {
    if (selectedAttacks.length === 0) { setError('Please select at least one attack'); return }
    setIsLoading(true)
    setError(null)
    try {
      const result: EstimationResult = {}
      if (selectedAttacks.includes('stern'))    result.stern    = await estimateComplexity.stern(parameters)
      if (selectedAttacks.includes('bjmm'))     result.bjmm     = await estimateComplexity.bjmm(parameters)
      if (selectedAttacks.includes('groebner')) result.groebner = await estimateComplexity.groebner(parameters)
      if (selectedAttacks.includes('stern_g'))  result.stern_g  = await estimateComplexity.stern_g(parameters)
      setResults(result)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(20,184,166,0.12),transparent_34rem),linear-gradient(180deg,#f8fbfb_0%,#eef3f5_100%)]">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="mb-6 border-b border-slate-200/80 pb-5">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <div className="mb-3 flex flex-wrap items-center gap-2 text-xs font-medium uppercase tracking-[0.16em] text-teal-700">
                <span className="inline-flex items-center gap-2 rounded-md border border-teal-200 bg-white/75 px-2.5 py-1 shadow-sm">
                  <ShieldCheck className="size-3.5" />
                  Post-Quantum Cryptography
                </span>
                <span className="text-slate-400">R-SDP Problem · CROSS Case Study</span>
              </div>
              <h1 className="text-3xl font-semibold leading-tight text-slate-950 sm:text-4xl">
                R-SDP Attack Complexity Estimator
              </h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
                Quantitative security analysis of attacks on the Restricted Syndrome Decoding problem, evaluated on CROSS parameters.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-2 rounded-lg border border-slate-200 bg-white/75 p-2 shadow-sm shadow-slate-200/50 backdrop-blur">
              <div className="min-w-0 rounded-md bg-slate-50 px-3 py-2">
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <Binary className="size-3.5 text-teal-700" />Field
                </div>
                <p className="mt-1 text-sm font-semibold text-slate-900">F<sub>{parameters.n === 251 ? 509 : 127}</sub></p>
              </div>
              <div className="min-w-0 rounded-md bg-slate-50 px-3 py-2">
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <Braces className="size-3.5 text-indigo-600" />Subgroup
                </div>
                <p className="mt-1 text-sm font-semibold text-slate-900">z = {parameters.z}</p>
              </div>
              <div className="min-w-0 rounded-md bg-slate-50 px-3 py-2">
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <Activity className="size-3.5 text-amber-600" />Attacks
                </div>
                <p className="mt-1 text-sm font-semibold text-slate-900">{selectedAttacks.length}</p>
              </div>
            </div>
          </div>
        </header>

        <div className="grid flex-1 grid-cols-1 gap-5 lg:grid-cols-[360px_minmax(0,1fr)]">
          <aside className="space-y-5">
            <section className="rounded-lg border border-slate-200 bg-white/90 p-5 shadow-sm shadow-slate-200/60">
              <ParameterPanel parameters={parameters} onParametersChange={setParameters} onCalculate={handleCalculate} isLoading={isLoading} selectedAttacks={selectedAttacks} />
            </section>
            <section className="rounded-lg border border-slate-200 bg-white/90 p-5 shadow-sm shadow-slate-200/60">
              <AttackSelector selectedAttacks={selectedAttacks} onAttackChange={setSelectedAttacks} />
            </section>
          </aside>

          <main className="min-w-0 rounded-lg border border-slate-200 bg-white/90 p-5 shadow-sm shadow-slate-200/60 lg:p-6">
            <ResultsDisplay results={results} isLoading={isLoading} error={error} selectedAttacks={selectedAttacks} />
          </main>
        </div>
      </div>
    </div>
  )
}