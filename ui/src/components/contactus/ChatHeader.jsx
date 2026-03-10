import { useState } from 'react'
import iconClose from '@/assets/icon--close.svg'
import SurveyModalContainer from './SurveyModalContainer'
import styles from './ChatHeader.module.scss'

export default function ChatHeader({ agent, isConnected, gptVersion, reset }) {
  const [showSurvey, setShowSurvey] = useState(false)

  const handleShowSurvey = () => {
    setShowSurvey((prev) => !prev)
  }

  return (
    <>
      <div className={styles.chatHeader}>
        <div className={styles.solomonProfile}>
          <div className={styles.solomonProfileImg}></div>
          <div className={`${styles.status} ${!isConnected ? styles.disabled : ''}`}></div>
        </div>
        <div className={styles.solomonDetail}>
          <div className={styles.solomonName}>BEUSABLE SOLOMON</div>
          <div className={styles.gptVersion}>UX GPT</div>
        </div>
        <button className={styles.exitButtonContainer} onClick={handleShowSurvey}>
          <div className={styles.exitButtonWrapper}>
            <img src={iconClose} alt="exit image" />
          </div>
        </button>
      </div>
      {showSurvey && (
        <SurveyModalContainer
          agent={agent}
          reset={reset}
          onClose={handleShowSurvey}
        />
      )}
    </>
  )
}
