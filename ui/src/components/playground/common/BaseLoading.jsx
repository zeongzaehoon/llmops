import loadingIcon from '@/assets/icon--loading-animated.svg'
import styles from './BaseLoading.module.scss'

const BaseLoading = () => {
  return (
    <div className={styles.loading}>
      <img src={loadingIcon} alt="loading" />
    </div>
  )
}

export default BaseLoading
