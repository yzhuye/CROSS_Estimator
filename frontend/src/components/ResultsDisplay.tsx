import { EstimationResult, AttackType } from '../lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'

interface ResultsDisplayProps {
  results: EstimationResult | null
  isLoading: boolean
  error: string | null
  selectedAttack: AttackType
}

function formatNumber(num: number): string {
  if (num < 1000) {
    return num.toFixed(2)
  }
  return num.toExponential(2)
}

function ResultCard({
  title,
  time,
  memory,
  l,
}: {
  title: string
  time: number
  memory: number
  l?: number
}) {
  return (
    <Card className="bg-white dark:bg-slate-950 border border-gray-200 dark:border-gray-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-1">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Time Complexity
          </p>
          <p className="text-2xl font-bold text-blue-600">
            2<sup>{formatNumber(time)}</sup>
          </p>
          <p className="text-xs text-gray-500">binary operations</p>
        </div>

        <div className="space-y-1">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Memory Complexity
          </p>
          <p className="text-2xl font-bold text-green-600">
            2<sup>{formatNumber(memory)}</sup>
          </p>
          <p className="text-xs text-gray-500">bits</p>
        </div>

        {l !== undefined && (
          <div className="space-y-1 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Optimal Parameter (l)
            </p>
            <p className="text-xl font-bold text-purple-600">{l}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function ResultsDisplay({
  results,
  isLoading,
  error,
  selectedAttack,
}: ResultsDisplayProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-40">
        <div className="text-center">
          <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin mb-2" />
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Calculating...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-sm font-medium text-red-900 dark:text-red-200">
          Error: {error}
        </p>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="flex items-center justify-center h-40">
        <p className="text-gray-600 dark:text-gray-400 text-center">
          Enter parameters and calculate to see results
        </p>
      </div>
    )
  }

  return (
    <div className="w-full space-y-6">
      <h2 className="text-xl font-semibold">Attack Complexity Results</h2>

      {(selectedAttack === 'bjmm' || selectedAttack === 'both') &&
        results.bjmm && (
          <ResultCard
            title="BJMM Attack"
            time={results.bjmm.time}
            memory={results.bjmm.memory}
            l={results.bjmm.ell}
          />
        )}

      {(selectedAttack === 'stern' || selectedAttack === 'both') &&
        results.stern && (
          <ResultCard
            title="Stern Attack"
            time={results.stern.time}
            memory={results.stern.memory}
            l={results.stern.ell}
          />
        )}

      {selectedAttack === 'both' && results.bjmm && results.stern && (
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 border border-blue-200 dark:border-blue-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Comparison</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Faster Attack
              </p>
              <p className="text-lg font-bold">
                {results.bjmm.time < results.stern.time ? 'BJMM' : 'Stern'}
              </p>
              <p className="text-xs text-gray-500">
                Time advantage:{' '}
                {Math.abs(results.bjmm.time - results.stern.time).toFixed(2)}{' '}
                bits
              </p>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Lower Memory Usage
              </p>
              <p className="text-lg font-bold">
                {results.bjmm.memory < results.stern.memory ? 'BJMM' : 'Stern'}
              </p>
              <p className="text-xs text-gray-500">
                Memory advantage:{' '}
                {Math.abs(results.bjmm.memory - results.stern.memory).toFixed(2)}{' '}
                bits
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
