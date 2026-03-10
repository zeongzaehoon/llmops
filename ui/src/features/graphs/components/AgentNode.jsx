import { useToolsets } from '@/hooks/queries/useToolsets'
import styles from './AgentNode.module.scss'

export default function AgentNode({ agent, index, onChange, onRemove, removable = true }) {
  const { data: toolsets = [] } = useToolsets()

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
        <label className={styles.fieldLabel}>Name</label>
        <input
          type="text"
          className={styles.input}
          value={agent.name || ''}
          onChange={(e) => handleChange('name', e.target.value)}
          placeholder="Agent name"
          maxLength={50}
        />
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

      <div className={styles.field}>
        <label className={styles.fieldLabel}>Toolset</label>
        <select
          className={styles.select}
          value={agent.toolset_name || ''}
          onChange={(e) => handleChange('toolset_name', e.target.value)}
        >
          <option value="">None</option>
          {toolsets.map((ts) => (
            <option key={ts._id || ts.name} value={ts.name}>
              {ts.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}
