import { EstimationResult, AttackType, DataPoint } from '../lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface ResultsDisplayProps {
  results: EstimationResult | null
  isLoading: boolean
  error: string | null
  selectedAttacks: AttackType[]
}

function formatNumber(num: number | undefined): string {
  if (num === undefined || num === null || isNaN(num)) {
    return '0'
  }
  
  if (num < 1000) {
    return num.toFixed(2)
  }
  return num.toExponential(2)
}

// Preparar datos para el gráfico
function prepareChartData(
  sternData: DataPoint[] | undefined,
  bjmmData: DataPoint[] | undefined,
  showStern: boolean,
  showBjmm: boolean
) {
  const allPoints: { ell: number; Stern?: number; BJMM?: number }[] = []
  const ellValues = new Set<number>()

  if (showStern) {
    sternData?.forEach((p) => ellValues.add(p.ell))
  }
  if (showBjmm) {
    bjmmData?.forEach((p) => ellValues.add(p.ell))
  }

  const sortedEll = Array.from(ellValues).sort((a, b) => a - b)

  sortedEll.forEach((ell) => {
    const point: { ell: number; Stern?: number; BJMM?: number } = { ell }
    const sternPoint = sternData?.find((p) => p.ell === ell)
    const bjmmPoint = bjmmData?.find((p) => p.ell === ell)

    if (sternPoint && showStern) {
      point.Stern = sternPoint.time
    }
    if (bjmmPoint && showBjmm) {
      point.BJMM = bjmmPoint.time
    }
    allPoints.push(point)
  })

  return allPoints
}

function ResultCard({
  title,
  time,
  memory,
  l,
}: {
  title: string
  time: number | undefined
  memory: number | undefined
  l?: number
}) {
  if (time === undefined || memory === undefined) {
    return (
      <Card className="bg-white dark:bg-slate-950 border border-gray-200 dark:border-gray-700">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500">No data available</p>
        </CardContent>
      </Card>
    )
  }

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
              Optimal Parameter (ℓ)
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
  selectedAttacks,
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

  if (!results || selectedAttacks.length === 0) {
    return (
      <div className="flex items-center justify-center h-40">
        <p className="text-gray-600 dark:text-gray-400 text-center">
          Select attacks and parameters, then click "Calculate Complexity"
        </p>
      </div>
    )
  }

  // CORREGIDO: Usar selectedAttacks.includes() correctamente
  const showStern = selectedAttacks.includes('stern') && results.stern !== undefined
  const showBjmm = selectedAttacks.includes('bjmm') && results.bjmm !== undefined

  const sternData_raw = results.stern
  const sternTime = sternData_raw?.optimal?.time
  const sternEll = sternData_raw?.optimal?.ell
  const sternChartData = sternData_raw?.data
  const sternMemory = sternData_raw?.optimal?.memory

  const bjmmData_raw = results.bjmm
  const bjmmTime = bjmmData_raw?.optimal?.time
  const bjmmEll = bjmmData_raw?.optimal?.ell
  const bjmmChartData = bjmmData_raw?.data
  const bjmmMemory = bjmmData_raw?.optimal?.memory ?? bjmmData_raw?.memory

  const chartData = prepareChartData(
    sternChartData,
    bjmmChartData,
    showStern,
    showBjmm
  )
  const showChart = chartData.length > 0 && selectedAttacks.length >= 1

  return (
    <div className="w-full space-y-6">
      <h2 className="text-xl font-semibold">Attack Complexity Results</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {showBjmm && (
          <ResultCard
            title="BJMM Attack"
            time={bjmmTime}
            memory={bjmmMemory}
            l={bjmmEll}
          />
        )}

        {showStern && (
          <ResultCard
            title="Stern Attack"
            time={sternTime}
            memory={sternMemory}
            l={sternEll}
          />
        )}
      </div>

      {/* Gráfica de complejidad vs ℓ */}
      {showChart && (
        <Card className="bg-white dark:bg-slate-950 border border-gray-200 dark:border-gray-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">
              Time Complexity vs ℓ Parameter
            </CardTitle>
            <p className="text-sm text-gray-500">
              Best ℓ is marked with the lowest time complexity
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-[400px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={chartData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="ell"
                    label={{ value: 'ℓ parameter', position: 'bottom', offset: 0 }}
                  />
                  <YAxis
                    label={{
                      value: 'log₂(time complexity)',
                      angle: -90,
                      position: 'insideLeft',
                    }}
                  />
                  <Tooltip
                    formatter={(value: any) => [`2^${formatNumber(value)}`, '']}
                    labelFormatter={(label) => `ℓ = ${label}`}
                  />
                  <Legend />
                  {showStern && sternChartData && sternChartData.length > 0 && (
                    <Line
                      type="monotone"
                      dataKey="Stern"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  )}
                  {showBjmm && bjmmChartData && bjmmChartData.length > 0 && (
                    <Line
                      type="monotone"
                      dataKey="BJMM"
                      stroke="#ef4444"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Comparación entre ataques (solo si ambos están seleccionados y existen) */}
      {showStern && showBjmm && bjmmTime !== undefined && sternTime !== undefined && (
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
                {bjmmTime < sternTime ? 'BJMM' : 'Stern'}
              </p>
              <p className="text-xs text-gray-500">
                Time advantage:{' '}
                {Math.abs(bjmmTime - sternTime).toFixed(2)}{' '}
                bits
              </p>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Lower Memory Usage
              </p>
              <p className="text-lg font-bold">
                {(bjmmMemory ?? Infinity) < (sternMemory ?? Infinity) ? 'BJMM' : 'Stern'}
              </p>
              <p className="text-xs text-gray-500">
                Memory advantage:{' '}
                {Math.abs((bjmmMemory ?? 0) - (sternMemory ?? 0)).toFixed(2)}{' '}
                bits
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}