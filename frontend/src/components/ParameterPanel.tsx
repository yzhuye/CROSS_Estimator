import { CrossParameters } from '../lib/types'
import { Button } from './ui/button'
import { Input } from './ui/input'

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
    <div className="w-full max-w-md space-y-6">
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">CROSS Parameters</h2>

        <div className="space-y-2">
          <label htmlFor="n" className="block text-sm font-medium">
            n (Code Length)
          </label>
          <Input
            id="n"
            type="number"
            min="1"
            value={parameters.n}
            onChange={(e) => handleChange('n', parseInt(e.target.value, 10))}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            Length of the linear code
          </p>
        </div>

        <div className="space-y-2">
          <label htmlFor="k" className="block text-sm font-medium">
            k (Code Dimension)
          </label>
          <Input
            id="k"
            type="number"
            min="1"
            value={parameters.k}
            onChange={(e) => handleChange('k', parseInt(e.target.value, 10))}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            Dimension of the linear code
          </p>
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-medium">Parameter Presets</h3>
        <div className="grid grid-cols-3 gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => applyPreset(presets.cross64)}
            className="w-full text-xs"
          >
            NIST-1
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => applyPreset(presets.cross128)}
            className="w-full text-xs"
          >
            NIST-3
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => applyPreset(presets.cross256)}
            className="w-full text-xs"
          >
            NIST-5
          </Button>
        </div>
      </div>

      <Button
        onClick={onCalculate}
        disabled={isLoading}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white"
      >
        {isLoading ? 'Calculating...' : 'Calculate Complexity'}
      </Button>
    </div>
  )
}
