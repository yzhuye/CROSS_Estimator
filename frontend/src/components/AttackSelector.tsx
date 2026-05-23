import { AttackType } from '../lib/types'
import { Check, GitBranch, Network, FlaskConical, Layers, Zap } from 'lucide-react'

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
  {
    value: 'groebner',
    label: 'Gröbner Basis',
    description: 'F5 algebraic attack on R-SDP polynomial system',
    icon: FlaskConical,
    accent: 'violet',
  },
  {
    value: 'stern_g',
    label: 'Stern R-SDP(G)',
    description: 'Generic ISD on R-SDP(G) — ignores subgroup structure',
    icon: Layers,
    accent: 'orange',
  },
  {
    value: 'collision_search',
    label: 'Submatrix Stern/Dumer',
    description: 'Hybrid attack on R-SDP(G) — exploits subgroup G structure (Theorem 15)',
    icon: Zap,
    accent: 'emerald',
  },
]

export function AttackSelector({ selectedAttacks, onAttackChange }: AttackSelectorProps) {
  const toggleAttack = (attack: AttackType) => {
    if (selectedAttacks.includes(attack)) {
      onAttackChange(selectedAttacks.filter((a) => a !== attack))
    } else {
      onAttackChange([...selectedAttacks, attack])
    }
  }

  const getColors = (accent: string, selected: boolean) => {
    const map: Record<string, { card: string; icon: string; check: string }> = {
      teal:   { card: 'border-teal-300 bg-teal-50/80 text-teal-950',     icon: 'bg-teal-100 text-teal-700 ring-teal-200',     check: 'border-teal-700 bg-teal-700' },
      indigo: { card: 'border-indigo-300 bg-indigo-50/80 text-indigo-950', icon: 'bg-indigo-100 text-indigo-700 ring-indigo-200', check: 'border-indigo-700 bg-indigo-700' },
      violet: { card: 'border-violet-300 bg-violet-50/80 text-violet-950', icon: 'bg-violet-100 text-violet-700 ring-violet-200', check: 'border-violet-700 bg-violet-700' },
      orange:  { card: 'border-orange-300 bg-orange-50/80 text-orange-950',   icon: 'bg-orange-100 text-orange-700 ring-orange-200',   check: 'border-orange-700 bg-orange-700' },
      emerald: { card: 'border-emerald-300 bg-emerald-50/80 text-emerald-950', icon: 'bg-emerald-100 text-emerald-700 ring-emerald-200', check: 'border-emerald-700 bg-emerald-700' },
    }
    return selected ? map[accent] : { card: 'border-slate-200 bg-white text-slate-800', icon: 'bg-slate-50 text-slate-500 ring-slate-200', check: 'border-slate-300 bg-white text-transparent' }
  }

  return (
    <div className="w-full space-y-4">
      <div>
        <h2 className="text-base font-semibold text-slate-950">Select Attacks</h2>
        <p className="mt-1 text-xs text-slate-500">Choose one or more algorithms to compare.</p>
      </div>
      <div className="grid grid-cols-1 gap-2">
        {ATTACKS.map((attack) => {
          const selected = selectedAttacks.includes(attack.value)
          const colors = getColors(attack.accent, selected)
          const Icon = attack.icon

          return (
            <button
              key={attack.value}
              onClick={() => toggleAttack(attack.value)}
              className={`relative rounded-lg border p-3 text-left transition-all hover:-translate-y-0.5 hover:shadow-sm ${colors.card}`}
            >
              <div className="flex items-start gap-3">
                <span className={`flex size-9 shrink-0 items-center justify-center rounded-md ring-1 ${colors.icon}`}>
                  <Icon className="size-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold">{attack.label}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{attack.description}</p>
                </div>
                <span className={`flex size-5 shrink-0 items-center justify-center rounded border ${colors.check} text-white`}>
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