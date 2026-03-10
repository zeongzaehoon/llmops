import Badge from '@/components/data-display/Badge'
import styles from './GraphTypeSelector.module.scss'

const GRAPH_TYPES = [
  {
    value: 'linear',
    label: 'Linear',
    badge: 'info',
    description: 'Sequential pipeline where each agent passes output to the next.',
    diagram: '[A] \u2192 [B] \u2192 [C]',
  },
  {
    value: 'debate',
    label: 'Debate',
    badge: 'danger',
    description: 'Agents discuss and a moderator synthesizes the result.',
    diagram: '[A] \u21C4 [B] \u2192 [M]',
  },
  {
    value: 'parallel',
    label: 'Parallel',
    badge: 'staging',
    description: 'Agents run simultaneously and results are aggregated.',
    diagram: '[A],[B],[C] \u2192 [Agg]',
  },
  {
    value: 'router',
    label: 'Router',
    badge: 'production',
    description: 'A router agent dispatches to the best-fit agent.',
    diagram: '[R] \u2192? [A] or [B]',
  },
]

export default function GraphTypeSelector({ value, onChange }) {
  return (
    <div className={styles.grid}>
      {GRAPH_TYPES.map((type) => (
        <button
          key={type.value}
          type="button"
          className={`${styles.card} ${value === type.value ? styles.selected : ''}`}
          onClick={() => onChange(type.value)}
        >
          <div className={styles.cardTop}>
            <span className={styles.label}>{type.label}</span>
            <Badge variant={type.badge}>{type.value}</Badge>
          </div>
          <div className={styles.diagram}>{type.diagram}</div>
          <p className={styles.description}>{type.description}</p>
        </button>
      ))}
    </div>
  )
}
