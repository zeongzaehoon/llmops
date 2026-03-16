import { useMemo } from 'react'
import { useAgents } from '@/hooks/queries/useAgents'
import styles from './AgentNode.module.scss'

export default function AgentNode({ agent, index, onChange, onRemove, removable = true }) {
  const { data: registeredAgents = [] } = useAgents()

  const selectedInfo = useMemo(
    () => registeredAgents.find((a) => a.agent === agent.agent),
    [registeredAgents, agent.agent],
  )

  const handleChange = (field, value) => {
    onChange(index, { ...agent, [field]: value })
  }

  return (
    <div className={styles.node}>
      {removable && (
        <button
          type="button"
          className={styles.removeBtn}
          onClick={() => onRemove(index)}
          title="Remove agent"
        >
          &times;
        </button>
      )}

      <div className={styles.stepLabel}>Step {index + 1}</div>

      <div className={styles.field}>
        <label className={styles.fieldLabel}>Agent</label>
        <select
          className={styles.select}
          value={agent.agent || ''}
          onChange={(e) => handleChange('agent', e.target.value)}
        >
          <option value="">Select agent...</option>
          {registeredAgents.map((a) => (
            <option key={a.id || a.agent} value={a.agent}>
              {a.agent}
            </option>
          ))}
        </select>
        {selectedInfo?.description && (
          <span className={styles.agentDesc}>{selectedInfo.description}</span>
        )}
      </div>

      <div className={styles.field}>
        <label className={styles.fieldLabel}>Role</label>
        <input
          type="text"
          className={styles.input}
          value={agent.role || ''}
          onChange={(e) => handleChange('role', e.target.value)}
          placeholder="e.g. Researcher"
          maxLength={100}
        />
      </div>
    </div>
  )
}
