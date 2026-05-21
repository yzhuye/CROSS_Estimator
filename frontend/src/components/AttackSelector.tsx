import { AttackType } from '../lib/types'

interface AttackSelectorProps {
  selectedAttacks: AttackType[]
  onAttackChange: (attacks: AttackType[]) => void
}

const ATTACKS: { value: AttackType; label: string; description: string }[] = [
  {
    value: 'stern',
    label: 'Stern',
    description: 'Stern/Dumer information set decoding attack',
  },
  {
    value: 'bjmm',
    label: 'BJMM',
    description: 'Becker-Joux-May-Meurer representation technique',
  },
]

export function AttackSelector({
  selectedAttacks,
  onAttackChange,
}: AttackSelectorProps) {
  const toggleAttack = (attack: AttackType) => {
    if (selectedAttacks.includes(attack)) {
      onAttackChange(selectedAttacks.filter((a) => a !== attack))
    } else {
      onAttackChange([...selectedAttacks, attack])
    }
  }

  return (
    <div className="w-full space-y-4">
      <h2 className="text-xl font-semibold">Select Attacks</h2>
      <div className="grid grid-cols-1 gap-2">
        {ATTACKS.map((attack) => (
          <button
            key={attack.value}
            onClick={() => toggleAttack(attack.value)}
            className={`relative p-4 rounded-lg border-2 transition-all text-left ${
              selectedAttacks.includes(attack.value)
                ? 'border-blue-600 bg-blue-50 dark:bg-blue-950'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
          >
            <div className="flex items-center">
              <div
                className={`w-4 h-4 rounded border-2 mr-3 flex items-center justify-center transition-colors ${
                  selectedAttacks.includes(attack.value)
                    ? 'border-blue-600 bg-blue-600'
                    : 'border-gray-300'
                }`}
              >
                {selectedAttacks.includes(attack.value) && (
                  <svg
                    className="w-3 h-3 text-white"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M5 13l4 4L19 7" />
                  </svg>
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
      
      {selectedAttacks.length === 0 && (
        <p className="text-sm text-red-500 dark:text-red-400">
          Please select at least one attack
        </p>
      )}
    </div>
  )
}