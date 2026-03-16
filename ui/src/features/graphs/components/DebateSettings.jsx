import styles from './DebateSettings.module.scss'

export default function DebateSettings({
  maxIterations,
  onMaxIterationsChange,
  moderator,
  onModeratorChange,
  agents,
}) {
  return (
    <div className={styles.container}>
      <h4 className={styles.title}>Debate Settings</h4>

      <div className={styles.row}>
        <div className={styles.field}>
          <label className={styles.label}>Max Iterations</label>
          <div className={styles.sliderGroup}>
            <input
              type="range"
              min={1}
              max={10}
              step={1}
              value={maxIterations}
              onChange={(e) => onMaxIterationsChange(Number(e.target.value))}
              className={styles.slider}
            />
            <span className={styles.sliderValue}>{maxIterations}</span>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Moderator Agent</label>
          <select
            className={styles.select}
            value={moderator}
            onChange={(e) => onModeratorChange(e.target.value)}
          >
            <option value="">Select moderator...</option>
            {agents
              .filter((a) => a.agent)
              .map((a, i) => (
                <option key={i} value={a.agent}>
                  {a.agent}{a.role ? ` (${a.role})` : ''}
                </option>
              ))}
          </select>
        </div>
      </div>
    </div>
  )
}
