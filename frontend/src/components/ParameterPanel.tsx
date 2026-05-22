import { CrossParameters } from '../lib/types'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Calculator, Gauge, Ruler } from 'lucide-react'

interface ParameterPanelProps {
  parameters: CrossParameters
  onParametersChange: (params: CrossParameters) => void
  onCalculate: () => void
  isLoading: boolean
}

export function ParameterPanel({
  parameters,
  onParametersChange,
  onCalculate,
  isLoading,
}: ParameterPanelProps) {
  const handleChange = (field: keyof CrossParameters, value: number) => {
    onParametersChange({
      ...parameters,
      [field]: value,
    })
  }

  const presets = {
    cross64: { n: 127, k: 76 },
    cross128: { n: 187, k: 111 },
    cross256: { n: 251, k: 150 },
  }

  const applyPreset = (preset: CrossParameters) => {
    onParametersChange(preset)
  }

  return (
    <div className="w-full space-y-5">
      <div>
        <div className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-md bg-teal-50 text-teal-700 ring-1 ring-teal-100">
            <Gauge className="size-4" />
          </span>
          <div>
            <h2 className="text-base font-semibold text-slate-950">
              CROSS Parameters
            </h2>
            <p className="text-xs text-slate-500">NIST presets or custom code.</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <label
            htmlFor="n"
            className="flex items-center gap-1.5 text-sm font-medium text-slate-700"
          >
            <Ruler className="size-3.5 text-slate-400" />
            n (Code Length)
          </label>
          <Input
            id="n"
            type="number"
            min="1"
            value={parameters.n}
            onChange={(e) => handleChange('n', parseInt(e.target.value, 10))}
            className="h-10 w-full border-slate-200 bg-slate-50/80 text-slate-950 shadow-inner shadow-slate-200/40 focus-visible:border-teal-500 focus-visible:ring-teal-500/20"
          />
          <p className="text-xs text-slate-500">
            Length of the linear code
          </p>
        </div>

        <div className="space-y-2">
          <label
            htmlFor="k"
            className="flex items-center gap-1.5 text-sm font-medium text-slate-700"
          >
            <Ruler className="size-3.5 text-slate-400" />
            k (Code Dimension)
          </label>
          <Input
            id="k"
            type="number"
            min="1"
            value={parameters.k}
            onChange={(e) => handleChange('k', parseInt(e.target.value, 10))}
            className="h-10 w-full border-slate-200 bg-slate-50/80 text-slate-950 shadow-inner shadow-slate-200/40 focus-visible:border-teal-500 focus-visible:ring-teal-500/20"
          />
          <p className="text-xs text-slate-500">
            Dimension of the linear code
          </p>
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
          Parameter Presets
        </h3>
        <div className="grid grid-cols-3 gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => applyPreset(presets.cross64)}
            className="h-9 w-full border-slate-200 bg-white text-xs text-slate-700 hover:border-teal-200 hover:bg-teal-50 hover:text-teal-800"
          >
            NIST-1
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => applyPreset(presets.cross128)}
            className="h-9 w-full border-slate-200 bg-white text-xs text-slate-700 hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-800"
          >
            NIST-3
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => applyPreset(presets.cross256)}
            className="h-9 w-full border-slate-200 bg-white text-xs text-slate-700 hover:border-amber-200 hover:bg-amber-50 hover:text-amber-800"
          >
            NIST-5
          </Button>
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
