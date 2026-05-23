import { AttackType, CrossParameters } from '../lib/types'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Calculator, Gauge, Ruler } from 'lucide-react'

interface ParameterPanelProps {
  parameters: CrossParameters
  onParametersChange: (params: CrossParameters) => void
  onCalculate: () => void
  isLoading: boolean
  selectedAttacks: AttackType[]
}

const FIELDS: { key: keyof CrossParameters; label: string; desc: string }[] = [
  { key: 'n', label: 'n (Code Length)',    desc: 'Length of the linear code' },
  { key: 'k', label: 'k (Code Dimension)', desc: 'Dimension of the linear code' },
  { key: 'z', label: 'z (Subgroup Order)', desc: 'Order of subgroup E — must divide p−1 (e.g. 3, 7)' },
]

const PRESETS: { label: string; values: CrossParameters }[] = [
  { label: 'NIST-1', values: { n: 127, k: 76,  z: 7 } },
  { label: 'NIST-3', values: { n: 187, k: 111, z: 7 } },
  { label: 'NIST-5', values: { n: 251, k: 150, z: 7 } },
]

const PRESETS_RSDPG: { label: string; values: CrossParameters }[] = [
  { label: 'NIST-1 (G)', values: { n: 55,  k: 36, z: 127, m: 25, p: 509 } },
  { label: 'NIST-3 (G)', values: { n: 79,  k: 48, z: 127, m: 40, p: 509 } },
  { label: 'NIST-5 (G)', values: { n: 106, k: 64, z: 127, m: 55, p: 509 } },
]

const PRESET_HOVER = [
  'hover:border-teal-200 hover:bg-teal-50 hover:text-teal-800',
  'hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-800',
  'hover:border-amber-200 hover:bg-amber-50 hover:text-amber-800',
]

const PRESET_HOVER_G = [
  'hover:border-orange-200 hover:bg-orange-50 hover:text-orange-800',
  'hover:border-orange-200 hover:bg-orange-50 hover:text-orange-800',
  'hover:border-orange-200 hover:bg-orange-50 hover:text-orange-800',
]

export function ParameterPanel({
  parameters,
  onParametersChange,
  onCalculate,
  isLoading,
  selectedAttacks,
}: ParameterPanelProps) {
  const showSternG = selectedAttacks.some((a) => a === 'stern_g' || a === 'collision_search')

  const handleChange = (field: keyof CrossParameters, value: number) => {
    onParametersChange({ ...parameters, [field]: value })
  }

  return (
    <div className="w-full space-y-5">
      <div>
        <div className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-md bg-teal-50 text-teal-700 ring-1 ring-teal-100">
            <Gauge className="size-4" />
          </span>
          <div>
            <h2 className="text-base font-semibold text-slate-950">R-SDP Parameters</h2>
            <p className="text-xs text-slate-500">CROSS NIST presets or custom instance.</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {FIELDS.map(({ key, label, desc }) => (
          <div key={key} className="space-y-2">
            <label htmlFor={key} className="flex items-center gap-1.5 text-sm font-medium text-slate-700">
              <Ruler className="size-3.5 text-slate-400" />
              {label}
            </label>
            <Input
              id={key}
              type="number"
              min="1"
              value={parameters[key] ?? ''}
              onChange={(e) => handleChange(key, parseInt(e.target.value, 10))}
              className="h-10 w-full border-slate-200 bg-slate-50/80 text-slate-950 shadow-inner shadow-slate-200/40 focus-visible:border-teal-500 focus-visible:ring-teal-500/20"
            />
            <p className="text-xs text-slate-500">{desc}</p>
          </div>
        ))}

        {showSternG && (
          <>
            <div className="space-y-2">
              <label htmlFor="m" className="flex items-center gap-1.5 text-sm font-medium text-slate-700">
                <Ruler className="size-3.5 text-slate-400" />
                m (Subgroup Dimension)
              </label>
              <Input
                id="m"
                type="number"
                min="1"
                value={parameters.m ?? 25}
                onChange={(e) => handleChange('m', parseInt(e.target.value, 10))}
                className="h-10 w-full border-slate-200 bg-slate-50/80 text-slate-950 shadow-inner shadow-slate-200/40 focus-visible:border-orange-500 focus-visible:ring-orange-500/20"
              />
              <p className="text-xs text-slate-500">Dimension of subgroup G ≤ n</p>
            </div>

            <div className="space-y-2">
              <label htmlFor="p" className="flex items-center gap-1.5 text-sm font-medium text-slate-700">
                <Ruler className="size-3.5 text-slate-400" />
                p (Field Size)
              </label>
              <Input
                id="p"
                type="number"
                min="2"
                value={parameters.p ?? 509}
                onChange={(e) => handleChange('p', parseInt(e.target.value, 10))}
                className="h-10 w-full border-slate-200 bg-slate-50/80 text-slate-950 shadow-inner shadow-slate-200/40 focus-visible:border-orange-500 focus-visible:ring-orange-500/20"
              />
              <p className="text-xs text-slate-500">Prime field size for R-SDP(G)</p>
            </div>
          </>
        )}
      </div>

      <div className="space-y-2">
        <h3 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          {showSternG ? 'R-SDP(G) Presets' : 'Parameter Presets'}
        </h3>
        <div className="grid grid-cols-3 gap-2">
          {(showSternG ? PRESETS_RSDPG : PRESETS).map(({ label, values }, i) => (
            <Button
              key={label}
              variant="outline"
              size="sm"
              onClick={() => onParametersChange(values)}
              className={`h-9 w-full border-slate-200 bg-white text-xs text-slate-700 ${
                showSternG ? PRESET_HOVER_G[i] : PRESET_HOVER[i]
              }`}
            >
              {label}
            </Button>
          ))}
        </div>
      </div>

      <Button
        onClick={onCalculate}
        disabled={isLoading}
        className="h-10 w-full bg-teal-700 text-white shadow-sm shadow-teal-900/20 hover:bg-teal-800"
      >
        <Calculator className="size-4" />
        {isLoading ? 'Calculating...' : 'Calculate Complexity'}
      </Button>
    </div>
  )
}
