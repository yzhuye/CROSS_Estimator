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
  ReferenceLine,
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

function formatNumber(num: number | undefined | null): string {
  if (num === undefined || num === null || Number.isNaN(num)) return '0'
  if (num < 1000) return num.toFixed(2)
  return num.toExponential(2)
}

function prepareChartData(
  sternData: DataPoint[] | undefined,
  bjmmData: DataPoint[] | undefined,
  sternGData: DataPoint[] | undefined,
  showStern: boolean,
  showBjmm: boolean,
  showSternG: boolean,
) {
  const ellValues = new Set<number>()
  if (showStern)  sternData?.forEach((p) => ellValues.add(p.ell))
  if (showBjmm)   bjmmData?.forEach((p) => ellValues.add(p.ell))
  if (showSternG) sternGData?.forEach((p) => ellValues.add(p.ell))

  return Array.from(ellValues)
    .sort((a, b) => a - b)
    .map((ell) => {
      const point: Record<string, number> = { ell }
      if (showStern)  { const f = sternData?.find((p) => p.ell === ell);  if (f) point['Stern']   = f.time }
      if (showBjmm)   { const f = bjmmData?.find((p) => p.ell === ell);   if (f) point['BJMM']    = f.time }
      if (showSternG) { const f = sternGData?.find((p) => p.ell === ell); if (f) point['Stern_G'] = f.time }
      return point
    })
}

type Tone = 'teal' | 'indigo' | 'violet' | 'amber' | 'orange' | 'emerald'
type AccentColor = 'teal' | 'indigo' | 'violet' | 'orange' | 'emerald'

function MetricBlock({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: typeof Clock3
  label: string
  value: string
  tone: Tone
}) {
  const toneClass: Record<Tone, string> = {
    teal:    'bg-teal-50 text-teal-700 ring-teal-100',
    indigo:  'bg-indigo-50 text-indigo-700 ring-indigo-100',
    violet:  'bg-violet-50 text-violet-700 ring-violet-100',
    amber:   'bg-amber-50 text-amber-700 ring-amber-100',
    orange:  'bg-orange-50 text-orange-700 ring-orange-100',
    emerald: 'bg-emerald-50 text-emerald-700 ring-emerald-100',
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3">
      <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
        <span className={`flex size-7 items-center justify-center rounded-md ring-1 ${toneClass[tone]}`}>
          <Icon className="size-3.5" />
        </span>
        {label}
      </div>
      <p className="mt-3 font-mono text-xl font-semibold text-slate-950">{value}</p>
    </div>
  )
}

function ResultCard({
  title,
  time,
  memory,
  ell,
  dReg,
  accent,
}: {
  title: string
  time: number | null | undefined
  memory: number | null | undefined
  ell?: number | null
  dReg?: number | null
  accent: AccentColor
}) {
  const borderClass: Record<AccentColor, string> = {
    teal:    'border-t-teal-600',
    indigo:  'border-t-indigo-600',
    violet:  'border-t-violet-600',
    orange:  'border-t-orange-600',
    emerald: 'border-t-emerald-600',
  }
  const metricTone: Record<AccentColor, Tone> = {
    teal: 'teal', indigo: 'indigo', violet: 'violet', orange: 'orange', emerald: 'emerald',
  }

  if (time == null || memory == null) {
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

  return (
    <Card className={`rounded-lg border border-t-4 border-slate-200 bg-white shadow-sm ${borderClass[accent]}`}>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base text-slate-950">
          <Cpu className="size-4 text-slate-500" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid gap-3 sm:grid-cols-2">
          <MetricBlock icon={Clock3} label="Time Complexity" value={`2^${formatNumber(time)}`} tone={metricTone[accent]} />
          <MetricBlock icon={MemoryStick} label="Memory Complexity" value={`2^${formatNumber(memory)}`} tone="amber" />
        </div>
        {ell != null && (
          <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Sigma className="size-4 text-slate-400" />
              Optimal parameter
            </div>
            <p className="font-mono text-lg font-semibold text-slate-950">ell = {ell}</p>
          </div>
        )}
        {dReg != null && (
          <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Sigma className="size-4 text-slate-400" />
              Regularity degree
            </div>
            <p className="font-mono text-lg font-semibold text-slate-950">d_reg = {dReg}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function ResultsDisplay({ results, isLoading, error, selectedAttacks }: ResultsDisplayProps) {
  if (isLoading) {
    return (
      <div className="flex min-h-[420px] items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto size-9 animate-spin text-teal-700" />
          <p className="mt-3 text-sm font-medium text-slate-700">Calculating complexity...</p>
          <p className="mt-1 text-xs text-slate-500">Optimizing selected attack parameters</p>
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
          <p className="mt-4 text-base font-semibold text-slate-950">Results will appear here</p>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Select attacks and parameters, then calculate the estimation.
          </p>
        </div>
      </div>
    )
  }

  const showStern       = selectedAttacks.includes('stern')           && results.stern           != null
  const showBjmm        = selectedAttacks.includes('bjmm')            && results.bjmm            != null
  const showGroebner    = selectedAttacks.includes('groebner')        && results.groebner        != null
  const showSternG      = selectedAttacks.includes('stern_g')         && results.stern_g         != null
  const showCollision   = selectedAttacks.includes('collision_search') && results.collision_search != null

  const sternTime    = results.stern?.optimal?.time
  const sternMemory  = results.stern?.optimal?.memory
  const sternEll     = results.stern?.optimal?.ell

  const bjmmTime     = results.bjmm?.optimal?.time
  const bjmmMemory   = results.bjmm?.optimal?.memory
  const bjmmEll      = results.bjmm?.optimal?.ell

  const groebnerTime   = results.groebner?.optimal?.time
  const groebnerMemory = results.groebner?.optimal?.memory
  const groebnerDReg   = results.groebner?.optimal?.d_reg

  const sternGTime   = results.stern_g?.optimal?.time
  const sternGMemory = results.stern_g?.optimal?.memory
  const sternGEll    = results.stern_g?.optimal?.ell

  const csTime   = results.collision_search?.optimal?.time
  const csMemory = results.collision_search?.optimal?.memory
  const csJa     = results.collision_search?.optimal?.ja
  const csJb     = results.collision_search?.optimal?.jb

  const chartData = prepareChartData(
    results.stern?.data,
    results.bjmm?.data,
    results.stern_g?.data,
    showStern,
    showBjmm,
    showSternG,
  )
  const showChart = chartData.length > 0 || showGroebner

  const anyResult = results.stern ?? results.bjmm ?? results.groebner ?? results.stern_g
  const displayN = anyResult && 'n' in anyResult ? (anyResult as { n: number }).n : '—'
  const displayK = anyResult && 'k' in anyResult ? (anyResult as { k: number }).k : '—'

  const times: { label: string; time: number; memory: number }[] = []
  if (showStern    && sternTime    != null && sternMemory    != null) times.push({ label: 'Stern',    time: sternTime,    memory: sternMemory })
  if (showBjmm     && bjmmTime     != null && bjmmMemory     != null) times.push({ label: 'BJMM',     time: bjmmTime,     memory: bjmmMemory })
  if (showGroebner && groebnerTime != null && groebnerMemory != null) times.push({ label: 'Gröbner',  time: groebnerTime, memory: groebnerMemory })
  if (showSternG    && sternGTime != null && sternGMemory != null) times.push({ label: 'Stern_G',             time: sternGTime, memory: sternGMemory })
  if (showCollision && csTime    != null && csMemory    != null) times.push({ label: 'Submatrix Stern/Dumer', time: csTime,     memory: csMemory })

  const fastest = times.length > 0 ? times.reduce((a, b) => a.time   < b.time   ? a : b) : null
  const lowMem  = times.length > 0 ? times.reduce((a, b) => a.memory < b.memory ? a : b) : null

  return (
    <div className="w-full space-y-5">
      <div className="flex flex-col gap-3 border-b border-slate-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">Attack Complexity Results</h2>
          <p className="mt-1 text-sm text-slate-500">Values are expressed in logarithmic base 2 scale.</p>
        </div>
        <div className="inline-flex w-fit items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-600">
          <Database className="size-3.5 text-teal-700" />
          n = {displayN}, k = {displayK}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {showStern     && <ResultCard title="Stern Attack"                  time={sternTime}    memory={sternMemory}    ell={sternEll}      accent="teal"    />}
        {showBjmm      && <ResultCard title="BJMM Attack"                   time={bjmmTime}     memory={bjmmMemory}     ell={bjmmEll}       accent="indigo"  />}
        {showGroebner  && <ResultCard title="Gröbner Basis (F5)"            time={groebnerTime} memory={groebnerMemory} dReg={groebnerDReg} accent="violet"  />}
        {showSternG    && <ResultCard title="Stern R-SDP(G)"                time={sternGTime}   memory={sternGMemory}   ell={sternGEll}     accent="orange"  />}
        {showCollision && (
          <ResultCard
            title={`Submatrix Stern/Dumer${csJa != null ? ` (ja=${csJa}, jb=${csJb})` : ''}`}
            time={csTime}
            memory={csMemory}
            accent="emerald"
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
              Lower values indicate better estimated attack complexity.
              {showGroebner && groebnerTime != null && ' Dashed line: Gröbner (deterministic).'}
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-[360px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 12, right: 22, left: 0, bottom: 12 }}>
                  <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" />
                  <XAxis dataKey="ell" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: '#cbd5e1' }} tickLine={{ stroke: '#cbd5e1' }} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: '#cbd5e1' }} tickLine={{ stroke: '#cbd5e1' }} width={56} />
                  <Tooltip
                    formatter={(value: unknown) => [`2^${formatNumber(Number(value))}`, '']}
                    labelFormatter={(label: unknown) => `ell = ${label}`}
                    contentStyle={{ borderRadius: 8, borderColor: '#cbd5e1', boxShadow: '0 10px 30px rgba(15,23,42,0.10)' }}
                  />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  {showStern  && results.stern?.data  && results.stern.data.length  > 0 && (
                    <Line type="monotone" dataKey="Stern"   stroke="#0f766e" strokeWidth={2.5} dot={{ r: 3, strokeWidth: 2 }} activeDot={{ r: 6 }} />
                  )}
                  {showBjmm   && results.bjmm?.data   && results.bjmm.data.length   > 0 && (
                    <Line type="monotone" dataKey="BJMM"    stroke="#4f46e5" strokeWidth={2.5} dot={{ r: 3, strokeWidth: 2 }} activeDot={{ r: 6 }} />
                  )}
                  {showSternG && results.stern_g?.data && results.stern_g.data.length > 0 && (
                    <Line type="monotone" dataKey="Stern_G" stroke="#ea580c" strokeWidth={2.5} dot={{ r: 3, strokeWidth: 2 }} activeDot={{ r: 6 }} />
                  )}
                  {showGroebner && groebnerTime != null && (
                    <ReferenceLine
                      y={groebnerTime}
                      stroke="#7c3aed"
                      strokeWidth={2}
                      strokeDasharray="6 3"
                      label={{
                        value: `Gröbner: 2^${groebnerTime.toFixed(1)}`,
                        position: 'insideTopRight',
                        fill: '#7c3aed',
                        fontSize: 11,
                        fontWeight: 600,
                      }}
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {times.length >= 2 && fastest && lowMem && (
        <Card className="rounded-lg border border-slate-200 bg-slate-950 text-white shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-white">Comparison</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-white/10 bg-white/5 p-3">
              <p className="text-xs font-medium text-slate-300">Fastest Attack</p>
              <p className="mt-2 text-lg font-semibold">{fastest.label}</p>
              <p className="mt-1 text-xs text-slate-400">Min time: 2^{fastest.time.toFixed(2)}</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/5 p-3">
              <p className="text-xs font-medium text-slate-300">Lower Memory Usage</p>
              <p className="mt-2 text-lg font-semibold">{lowMem.label}</p>
              <p className="mt-1 text-xs text-slate-400">Min memory: 2^{lowMem.memory.toFixed(2)}</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
