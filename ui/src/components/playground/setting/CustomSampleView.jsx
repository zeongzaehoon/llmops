import solomonIcon from '@/assets/icon--solomon.svg'
import crownIcon from '@/assets/icon--crown.svg'
import clipboardIcon from '@/assets/icon--clipboard.svg'
import userIcon from '@/assets/icon--user.svg'
import styles from './CustomSampleView.module.scss'

const CustomSampleView = ({ color }) => {
  return (
    <div
      className={styles.sampleBackground}
      style={{ background: color.background, color: color.textColor }}
    >
      <div className={styles.chatHeader}>
        <div className={styles.chatHeaderWrapper}>
          <div className={styles.solomonProfile}>
            <img alt="solomon logo" src={solomonIcon} />
          </div>
          <div className={styles.solomonDetail}>
            <div className={styles.solomonName}>
              <p>
                <span className={`${styles.connectedLight} ${styles.connected}`} />
                UX GPT
              </p>
              <img alt="crown" src={crownIcon} />
            </div>
            <p className={styles.status} style={{ color: color.subTextColor }}>
              gpt-4-1106-preview
            </p>
          </div>
          <button className={styles.settingButton}>
            <div />
            <div />
            <div />
          </button>
        </div>
      </div>
      <div className={styles.messageContainer}>
        <div className={`${styles.messageWrapper} ${styles.isSolomon}`}>
          <div className={styles.messageProfile}>
            <img alt="solomon logo" src={solomonIcon} />
          </div>
          <div className={styles.messageDetail}>
            <p className={styles.messageAuthor} style={{ color: color.subTextColor }}>
              UX GPT
            </p>
            <div className={styles.messageText}>
              <p>UX GPT의 메시지</p>
              <div className={styles.copyButtonContainer}>
                <button>
                  <img src={clipboardIcon} alt="복사 버튼" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className={styles.messageContainer}>
        <div className={styles.messageWrapper}>
          <div className={styles.messageProfile}>
            <img alt="user logo" src={userIcon} />
          </div>
          <div className={styles.messageDetail}>
            <p className={styles.messageAuthor} style={{ color: color.subTextColor }}>
              나
            </p>
            <div
              className={styles.messageText}
              style={{
                background: color.themeColor,
                color: color.themeColor
              }}
            >
              <p style={{ color: color.invertedTextColor }}>나의 메시지</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CustomSampleView
