import styles from './CategorySelector.module.scss'

export default function CategorySelector({ categories = [], active, onSelect }) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.scroll}>
        {categories.map((cat) => (
          <button
            key={cat}
            className={`${styles.chip} ${cat === active ? styles.active : ''}`}
            onClick={() => onSelect(cat)}
          >
            {cat}
          </button>
        ))}
      </div>
    </div>
  )
}
