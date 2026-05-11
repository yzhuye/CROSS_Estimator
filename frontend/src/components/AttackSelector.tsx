import { AttackType } from '../lib/types'

interface AttackSelectorProps {
  selectedAttack: AttackType
  onAttackChange: (attack: AttackType) => void
}

export function AttackSelector({
  selectedAttack,
  onAttackChange,
}: AttackSelectorProps) {
  const attacks: { value: AttackType; label: string; description: string }[] =
    [
      {
        value: 'stern',
        label: 'Stern',
        description: 'Stern&apos;s information set decoding attack',
      },
    ]

  return (
    <div className="w-full space-y-4">
      <h2 className="text-xl font-semibold">Select Attack</h2>
      <div className="grid grid-cols-1 gap-2">
        {attacks.map((attack) => (
          <button
            key={attack.value}
            onClick={() => onAttackChange(attack.value)}
            className={`relative p-4 rounded-lg border-2 transition-all text-left ${
              selectedAttack === attack.value
                ? 'border-blue-600 bg-blue-50 dark:bg-blue-950'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
          >
            <div className="flex items-center">
              <div
                className={`w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center transition-colors ${
                  selectedAttack === attack.value
                    ? 'border-blue-600 bg-blue-600'
                    : 'border-gray-300'
                }`}
              >
                {selectedAttack === attack.value && (
                  <div className="w-1.5 h-1.5 bg-white rounded-full" />
                )}
              </div>
              <div>
                <p className="font-medium text-sm">{attack.label}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {attack.description}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
