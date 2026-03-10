import Card from '@/components/layout/Card'
import styles from './StatCard.module.scss'

/**
 * Dashboard stat card with icon, value, and detail text.
 * @param {string} icon - Emoji or Unicode character
 * @param {string} title - Card title
 * @param {string|number} value - Main display value
 * @param {string} subtitle - Detail text below value
 * @param {string} color - CSS variable for accent color
 * @param {boolean} pulse - Show pulse animation
 * @param {boolean} loading - Show shimmer state
 * @param {function} onClick - Click handler
 */
export default function StatCard({ icon, title, value, subtitle, color, pulse = false, loading = false, onClick }) {
  return (
    <Card hoverable className={styles.statCard} onClick={onClick}>
      <div className={styles.top}>
        <div className={styles.iconWrap} style={{ '--stat-color': color }}>
          {pulse && <span className={styles.pulse} />}
          <span className={styles.icon}>{icon}</span>
        </div>
        <span className={styles.title}>{title}</span>
      </div>

      {loading ? (
        <div className={styles.shimmer}>
          <div className={styles.shimmerLine} />
          <div className={styles.shimmerLineSm} />
        </div>
      ) : (
        <div className={styles.body}>
          <span className={styles.value}>{value}</span>
          {subtitle && <span className={styles.subtitle}>{subtitle}</span>}
        </div>
      )}
    </Card>
  )
}
