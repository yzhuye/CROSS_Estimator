import { AttackType } from '../lib/types'
import { Check, GitBranch, Network, FlaskConical, Layers, Zap } from 'lucide-react'

interface AttackSelectorProps {
  selectedAttacks: AttackType[]
  onAttackChange: (attacks: AttackType[]) => void
}

type AttackDef = {
  value: AttackType
  label: string
  description: string
  icon: typeof Network
  accent: string
}

const ATTACKS_RSDP: AttackDef[] = [
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
]

const ATTACKS_RSDPG: AttackDef[] = [
  {
    value: 'stern_g',
    label: 'Stern R-SDP(G)',
    description: 'Generic ISD on R-SDP(G) — ignores subgroup G structure',
    icon: Layers,
    accent: 'orange',
  },
  {
    value: 'collision_search',
    label: 'Submatrix Stern/Dumer',
    description: 'Exploits subgroup G structure (Theorem 15)',
    icon: Zap,
    accent: 'emerald',
  },
]

const RSDP_VALUES   = new Set<AttackType>(ATTACKS_RSDP.map((a)   => a.value))
const RSDPG_VALUES  = new Set<AttackType>(ATTACKS_RSDPG.map((a)  => a.value))

function groupOf(a: AttackType): 'rsdp' | 'rsdpg' {
  return RSDPG_VALUES.has(a) ? 'rsdpg' : 'rsdp'
}

export function AttackSelector({ selectedAttacks, onAttackChange }: AttackSelectorProps) {
  const toggleAttack = (attack: AttackType) => {
    const clickedGroup = groupOf(attack)
    const otherGroup   = clickedGroup === 'rsdp' ? RSDPG_VALUES : RSDP_VALUES

    // Remove every attack from the opposite group (enforce mutual exclusivity)
    const sameGroupSelected = selectedAttacks.filter((a) => !otherGroup.has(a))

    if (sameGroupSelected.includes(attack)) {
      onAttackChange(sameGroupSelected.filter((a) => a !== attack))
    } else {
      onAttackChange([...sameGroupSelected, attack])
    }
  }

  const getColors = (accent: string, selected: boolean) => {
    const map: Record<string, { card: string; icon: string; check: string }> = {
      teal:    { card: 'border-teal-300 bg-teal-50/80 text-teal-950',       icon: 'bg-teal-100 text-teal-700 ring-teal-200',       check: 'border-teal-700 bg-teal-700' },
      indigo:  { card: 'border-indigo-300 bg-indigo-50/80 text-indigo-950', icon: 'bg-indigo-100 text-indigo-700 ring-indigo-200', check: 'border-indigo-700 bg-indigo-700' },
      violet:  { card: 'border-violet-300 bg-violet-50/80 text-violet-950', icon: 'bg-violet-100 text-violet-700 ring-violet-200', check: 'border-violet-700 bg-violet-700' },
      orange:  { card: 'border-orange-300 bg-orange-50/80 text-orange-950', icon: 'bg-orange-100 text-orange-700 ring-orange-200', check: 'border-orange-700 bg-orange-700' },
      emerald: { card: 'border-emerald-300 bg-emerald-50/80 text-emerald-950', icon: 'bg-emerald-100 text-emerald-700 ring-emerald-200', check: 'border-emerald-700 bg-emerald-700' },
    }
    return selected
      ? map[accent]
      : { card: 'border-slate-200 bg-white text-slate-800', icon: 'bg-slate-50 text-slate-500 ring-slate-200', check: 'border-slate-300 bg-white text-transparent' }
  }

  const renderGroup = (title: string, badge: string, badgeClass: string, attacks: AttackDef[]) => (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-[0.13em] text-slate-500">{title}</span>
        <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${badgeClass}`}>{badge}</span>
      </div>
      <div className="grid grid-cols-1 gap-2">
        {attacks.map((attack) => {
          const selected = selectedAttacks.includes(attack.value)
          const colors   = getColors(attack.accent, selected)
          const Icon     = attack.icon
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
    </div>
  )

  return (
    <div className="w-full space-y-5">
      <div>
        <h2 className="text-base font-semibold text-slate-950">Select Attacks</h2>
        <p className="mt-1 text-xs text-slate-500">
          Choose one or more algorithms. R-SDP and R-SDP(G) attacks use different parameters — they cannot be mixed.
        </p>
      </div>

      {renderGroup('R-SDP Attacks', 'z = 7', 'bg-teal-50 text-teal-700 ring-1 ring-teal-200', ATTACKS_RSDP)}

      <div className="border-t border-dashed border-slate-200" />

      {renderGroup('R-SDP(G) Attacks', 'z = 127, m < n', 'bg-orange-50 text-orange-700 ring-1 ring-orange-200', ATTACKS_RSDPG)}

      {selectedAttacks.length === 0 && (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          Please select at least one attack
        </p>
      )}
    </div>
  )
}