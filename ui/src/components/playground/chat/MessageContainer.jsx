import { useMemo, useCallback } from 'react'
import { convertMarkdownToHtml } from '@/utils/parse'
import { AGENT } from '@/utils/constants'
import iconUser from '@/assets/icon--user.svg'
import iconSolomon from '@/assets/icon--solomon.svg'
import iconAiSolomon from '@/assets/icon--aisolomon.svg'
import iconClipboard from '@/assets/icon--clipboard.svg'
import styles from './MessageContainer.module.scss'

export default function MessageContainer({
  agent,
  message,
  isLoadingItem,
  chatOptions = {},
  onSubmit
}) {

  const isSolomon = message.role === 'ai'

  const author = useMemo(() => {
    if (isSolomon) {
      return agent === AGENT.CS ? '\uC194\uB85C\uBAAC' : 'UX GPT'
    } else {
      return '\uB098'
    }
  }, [isSolomon, agent])

  const copy = useCallback(() => {
    navigator.clipboard.writeText(message.message).then(() => alert('\uBA54\uC2DC\uC9C0\uB97C \uBCF5\uC0AC\uD588\uC2B5\uB2C8\uB2E4.'))
  }, [message.message])

  const profileIcon = !isSolomon
    ? iconUser
    : agent === AGENT.CS
      ? iconSolomon
      : iconAiSolomon

  return (
    <div className={styles['message-container']}>
      <div
        className={`${styles['message-wrapper']} ${isSolomon ? styles['isSolomon'] : ''}`}
      >
        <div className={styles['message-profile']}>
          <img alt="profile" src={profileIcon} />
        </div>
        <div className={styles['message-content']}>
          <p className={styles['message-content-author']}>{author}</p>
          <div className={styles['message-content-text']}>
            {isSolomon ? (
              <div
                className={`${styles['message-content-text-body']} ${styles['reset-font-size']} ${isLoadingItem ? styles['loading'] : ''}`}
                dangerouslySetInnerHTML={{ __html: convertMarkdownToHtml(message.message) }}
              />
            ) : (
              <p
                className={`${styles['message-content-text-body']} ${isLoadingItem ? styles['loading'] : ''}`}
              >
                {message.message}
              </p>
            )}
            {!isLoadingItem && isSolomon && (
              <div className={styles['message-content-text-footer']}>
                <div></div>
                <div className={styles['buttons']}>
                  <button className={`${styles['icon-button']} ${styles['copy']}`}>
                    <img src={iconClipboard} alt={'\uBCF5\uC0AC \uBC84\uD2BC'} onClick={copy} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
