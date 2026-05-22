import { EstimationResult, AttackType, DataPoint } from '../lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import {
  AlertCircle,
  BarChart3,
  Clock3,
  Cpu,
  Database,
  Loader2,
  MemoryStick,
  Sigma,
} from 'lucide-react'
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
  if (num === undefined || num === null || Number.isNaN(num)) {
    return '0'
  }

  if (num < 1000) {
    return num.toFixed(2)
  }
  return num.toExponential(2)
}

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

function MetricBlock({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: typeof Clock3
  label: string
  value: string
  tone: 'teal' | 'indigo' | 'amber'
}) {
  const toneClass = {
    teal: 'bg-teal-50 text-teal-700 ring-teal-100',
    indigo: 'bg-indigo-50 text-indigo-700 ring-indigo-100',
    amber: 'bg-amber-50 text-amber-700 ring-amber-100',
  }[tone]

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3">
      <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
        <span
          className={`flex size-7 items-center justify-center rounded-md ring-1 ${toneClass}`}
        >
          <Icon className="size-3.5" />
        </span>
        {label}
      </div>
      <p className="mt-3 font-mono text-xl font-semibold text-slate-950">
        {value}
      </p>
    </div>
  )
}

function ResultCard({
  title,
  time,
  memory,
  ell,
  accent,
}: {
  title: string
  time: number | undefined
  memory: number | undefined
  ell?: number
  accent: 'teal' | 'indigo'
}) {
  if (time === undefined || memory === undefined) {
    return (
      <Card className="rounded-lg border-slate-200 bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="text-base text-slate-950">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">No data available</p>
        </CardContent>
      </Card>
    )
  }

  const accentClass =
    accent === 'teal'
      ? 'border-t-teal-600'
      : 'border-t-indigo-600'

  return (
    <Card
      className={`rounded-lg border border-t-4 border-slate-200 bg-white shadow-sm ${accentClass}`}
    >
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base text-slate-950">
          <Cpu className="size-4 text-slate-500" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid gap-3 sm:grid-cols-2">
          <MetricBlock
            icon={Clock3}
            label="Time Complexity"
            value={`2^${formatNumber(time)}`}
            tone={accent === 'teal' ? 'teal' : 'indigo'}
          />
          <MetricBlock
            icon={MemoryStick}
            label="Memory Complexity"
            value={`2^${formatNumber(memory)}`}
            tone="amber"
          />
        </div>

        {ell !== undefined && (
          <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Sigma className="size-4 text-slate-400" />
              Optimal parameter
            </div>
            <p className="font-mono text-lg font-semibold text-slate-950">
              ell = {ell}
            </p>
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
      <div className="flex min-h-[420px] items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto size-9 animate-spin text-teal-700" />
          <p className="mt-3 text-sm font-medium text-slate-700">
            Calculating complexity...
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Optimizing selected attack parameters
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
        <AlertCircle className="mt-0.5 size-5 shrink-0" />
        <div>
          <p className="text-sm font-semibold">Estimation error</p>
          <p className="mt-1 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  if (!results || selectedAttacks.length === 0) {
    return (
      <div className="flex min-h-[420px] items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50/70 p-8">
        <div className="max-w-sm text-center">
          <div className="mx-auto flex size-12 items-center justify-center rounded-lg bg-white text-teal-700 ring-1 ring-slate-200">
            <BarChart3 className="size-6" />
          </div>
          <p className="mt-4 text-base font-semibold text-slate-950">
            Results will appear here
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Select attacks and parameters, then calculate the estimation.
          </p>
        </div>
      </div>
    )
  }

  const showStern =
    selectedAttacks.includes('stern') && results.stern !== undefined
  const showBjmm = selectedAttacks.includes('bjmm') && results.bjmm !== undefined

  const sternDataRaw = results.stern
  const sternTime = sternDataRaw?.optimal?.time
  const sternEll = sternDataRaw?.optimal?.ell
  const sternChartData = sternDataRaw?.data
  const sternMemory = sternDataRaw?.optimal?.memory

  const bjmmDataRaw = results.bjmm
  const bjmmTime = bjmmDataRaw?.optimal?.time
  const bjmmEll = bjmmDataRaw?.optimal?.ell
  const bjmmChartData = bjmmDataRaw?.data
  const bjmmMemory = bjmmDataRaw?.optimal?.memory ?? bjmmDataRaw?.memory

  const chartData = prepareChartData(
    sternChartData,
    bjmmChartData,
    showStern,
    showBjmm
  )
  const showChart = chartData.length > 0 && selectedAttacks.length >= 1

  return (
    <div className="w-full space-y-5">
      <div className="flex flex-col gap-3 border-b border-slate-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">
            Attack Complexity Results
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Values are expressed in logarithmic base 2 scale.
          </p>
        </div>
        <div className="inline-flex w-fit items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-600">
          <Database className="size-3.5 text-teal-700" />
          n = {sternDataRaw?.n ?? bjmmDataRaw?.n}, k ={' '}
          {sternDataRaw?.k ?? bjmmDataRaw?.k}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {showStern && (
          <ResultCard
            title="Stern Attack"
            time={sternTime}
            memory={sternMemory}
            ell={sternEll}
            accent="teal"
          />
        )}

        {showBjmm && (
          <ResultCard
            title="BJMM Attack"
            time={bjmmTime}
            memory={bjmmMemory}
            ell={bjmmEll}
            accent="indigo"
          />
        )}
      </div>

      {showChart && (
        <Card className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base text-slate-950">
              <BarChart3 className="size-4 text-slate-500" />
              Time Complexity vs ell Parameter
            </CardTitle>
            <p className="text-sm text-slate-500">
              Lower curve values indicate better estimated attack complexity.
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-[360px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={chartData}
                  margin={{ top: 12, right: 22, left: 0, bottom: 12 }}
                >
                  <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" />
                  <XAxis
                    dataKey="ell"
                    tick={{ fill: '#64748b', fontSize: 12 }}
                    axisLine={{ stroke: '#cbd5e1' }}
                    tickLine={{ stroke: '#cbd5e1' }}
                  />
                  <YAxis
                    tick={{ fill: '#64748b', fontSize: 12 }}
                    axisLine={{ stroke: '#cbd5e1' }}
                    tickLine={{ stroke: '#cbd5e1' }}
                    width={56}
                  />
                  <Tooltip
                    formatter={(value: unknown) => [
                      `2^${formatNumber(Number(value))}`,
                      '',
                    ]}
                    labelFormatter={(label: unknown) => `ell = ${label}`}
                    contentStyle={{
                      borderRadius: 8,
                      borderColor: '#cbd5e1',
                      boxShadow: '0 10px 30px rgba(15, 23, 42, 0.10)',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  {showStern && sternChartData && sternChartData.length > 0 && (
                    <Line
                      type="monotone"
                      dataKey="Stern"
                      stroke="#0f766e"
                      strokeWidth={2.5}
                      dot={{ r: 3, strokeWidth: 2 }}
                      activeDot={{ r: 6 }}
                    />
                  )}
                  {showBjmm && bjmmChartData && bjmmChartData.length > 0 && (
                    <Line
                      type="monotone"
                      dataKey="BJMM"
                      stroke="#4f46e5"
                      strokeWidth={2.5}
                      dot={{ r: 3, strokeWidth: 2 }}
                      activeDot={{ r: 6 }}
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {showStern &&
        showBjmm &&
        bjmmTime !== undefined &&
        sternTime !== undefined && (
          <Card className="rounded-lg border border-slate-200 bg-slate-950 text-white shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base text-white">Comparison</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <p className="text-xs font-medium text-slate-300">
                  Faster Attack
                </p>
                <p className="mt-2 text-lg font-semibold">
                  {bjmmTime < sternTime ? 'BJMM' : 'Stern'}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  Difference: {Math.abs(bjmmTime - sternTime).toFixed(2)} bits
                </p>
              </div>

              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <p className="text-xs font-medium text-slate-300">
                  Lower Memory Usage
                </p>
                <p className="mt-2 text-lg font-semibold">
                  {(bjmmMemory ?? Infinity) < (sternMemory ?? Infinity)
                    ? 'BJMM'
                    : 'Stern'}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  Difference:{' '}
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
