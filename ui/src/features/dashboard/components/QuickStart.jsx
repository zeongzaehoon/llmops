import { useNavigate } from 'react-router-dom'
import Button from '@/components/inputs/Button'
import styles from './QuickStart.module.scss'

const STEPS = [
  {
    id: 'server',
    label: 'Register an MCP Server',
    path: '/admin/servers',
  },
  {
    id: 'toolset',
    label: 'Create an Agent',
    path: '/admin/agents',
  },
  {
    id: 'playground',
    label: 'Test in Playground',
    path: '/admin/playground',
  },
]

/**
 * Onboarding checklist for new users.
 * @param {boolean} hasServers - Whether MCP servers exist
 * @param {boolean} hasToolsets - Whether agent toolsets exist
 * @param {boolean} hasPlayground - Whether playground has been used (always false for now)
 */
export default function QuickStart({ hasServers = false, hasToolsets = false, hasPlayground = false }) {
  const navigate = useNavigate()

  const completed = [hasServers, hasToolsets, hasPlayground]
  const completedCount = completed.filter(Boolean).length
  const allDone = completedCount === STEPS.length
  const progress = (completedCount / STEPS.length) * 100

  if (allDone) return null

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3 className={styles.title}>Welcome to Solomon</h3>
        <p className={styles.subtitle}>Set up your first agent in 3 steps</p>
      </div>

      <div className={styles.progressWrap}>
        <div className={styles.progressBar}>
          <div className={styles.progressFill} style={{ width: `${progress}%` }} />
        </div>
        <span className={styles.progressText}>{completedCount}/{STEPS.length}</span>
      </div>

      <div className={styles.steps}>
        {STEPS.map((step, i) => {
          const done = completed[i]
          return (
            <div key={step.id} className={`${styles.step} ${done ? styles.stepDone : ''}`}>
              <span className={styles.stepCheck}>
                {done ? '\u2713' : i + 1}
              </span>
              <span className={`${styles.stepLabel} ${done ? styles.strikethrough : ''}`}>
                {step.label}
              </span>
              {!done && (
                <Button
                  variant="ghost"
                  size="sm"
                  className={styles.stepAction}
                  onClick={() => navigate(step.path)}
                >
                  Start &rarr;
                </Button>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
