import { AttackType } from '../lib/types'
import { Check, GitBranch, Network } from 'lucide-react'

interface AttackSelectorProps {
  selectedAttacks: AttackType[]
  onAttackChange: (attacks: AttackType[]) => void
}

const ATTACKS: {
  value: AttackType
  label: string
  description: string
  icon: typeof Network
  accent: string
}[] = [
  {
    value: 'stern',
    label: 'Stern',
    description: 'Stern/Dumer information set decoding attack',
    icon: Network,
    accent: 'teal',
  },
  {
    value: 'bjmm',
    label: 'BJMM',
    description: 'Becker-Joux-May-Meurer representation technique',
    icon: GitBranch,
    accent: 'indigo',
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
      <div>
        <h2 className="text-base font-semibold text-slate-950">
          Select Attacks
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          Choose one or more algorithms to compare.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-2">
        {ATTACKS.map((attack) => {
          const selected = selectedAttacks.includes(attack.value)
          const Icon = attack.icon
          const selectedClass =
            attack.accent === 'teal'
              ? 'border-teal-300 bg-teal-50/80 text-teal-950'
              : 'border-indigo-300 bg-indigo-50/80 text-indigo-950'
          const iconClass =
            attack.accent === 'teal'
              ? 'bg-teal-100 text-teal-700 ring-teal-200'
              : 'bg-indigo-100 text-indigo-700 ring-indigo-200'

          return (
            <button
              key={attack.value}
              onClick={() => toggleAttack(attack.value)}
              className={`relative rounded-lg border p-3 text-left transition-all hover:-translate-y-0.5 hover:shadow-sm ${
                selected
                  ? selectedClass
                  : 'border-slate-200 bg-white text-slate-800 hover:border-slate-300'
              }`}
            >
              <div className="flex items-start gap-3">
                <span
                  className={`flex size-9 shrink-0 items-center justify-center rounded-md ring-1 ${
                    selected ? iconClass : 'bg-slate-50 text-slate-500 ring-slate-200'
                  }`}
                >
                  <Icon className="size-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold">{attack.label}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    {attack.description}
                  </p>
                </div>
                <span
                  className={`flex size-5 shrink-0 items-center justify-center rounded border ${
                    selected
                      ? 'border-teal-700 bg-teal-700 text-white'
                      : 'border-slate-300 bg-white text-transparent'
                  }`}
                >
                  <Check className="size-3.5" />
                </span>
              </div>
            </button>
          )
        })}
      </div>

      {selectedAttacks.length === 0 && (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          Please select at least one attack
        </p>
      )}
    </div>
  )
}
