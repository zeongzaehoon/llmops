import styles from './PageHeader.module.scss'

/**
 * Page header with title, description, and optional action area.
 * @param {string} title
 * @param {string} description
 * @param {React.ReactNode} actions
 */
export default function PageHeader({ title, description, actions }) {
  return (
    <div className={styles.header}>
      <div className={styles.top}>
        <div className={styles.info}>
          <h1 className={styles.title}>{title}</h1>
          {description && <p className={styles.description}>{description}</p>}
        </div>
        {actions && <div className={styles.actions}>{actions}</div>}
      </div>
    </div>
  )
}
