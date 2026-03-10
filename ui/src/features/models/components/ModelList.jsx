import styles from './ModelList.module.scss'

export default function ModelList({ models = [], selected, onSelect }) {
  if (models.length === 0) {
    return (
      <div className={styles.empty}>
        No models available for this vendor
      </div>
    )
  }

  return (
    <div className={styles.list}>
      {models.map((model) => {
        const modelId = typeof model === 'string' ? model : model.model || model.id
        const description = typeof model === 'string' ? null : model.description
        const isSelected = modelId === selected

        return (
          <label
            key={modelId}
            className={`${styles.item} ${isSelected ? styles.selected : ''}`}
          >
            <input
              type="radio"
              name="model"
              className={styles.radio}
              checked={isSelected}
              onChange={() => onSelect(modelId)}
            />
            <div className={styles.info}>
              <span className={styles.modelName}>{modelId}</span>
              {description && (
                <span className={styles.description}>{description}</span>
              )}
            </div>
          </label>
        )
      })}
    </div>
  )
}
