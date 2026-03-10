import { convertMarkdownToHtml } from '@/utils/parse'
import iconPerson from '@/assets/icon--person.svg'
import styles from './MessageContainer.module.scss'

export default function MessageContainer({ content, role, isLoadingItem }) {
  return (
    <div className={`${styles.messageContainer} ${role === 'ai' ? styles.isSolomon : ''}`}>
      {role === 'ai' ? (
        <div className={styles.messageProfileSolomon}></div>
      ) : (
        <div className={styles.messageProfileHuman}>
          <img src={iconPerson} alt="" />
        </div>
      )}
      <div className={styles.messageTextContainer}>
        {isLoadingItem ? (
          <div className={`${styles.messageText} ${styles.loading}`}>loading .</div>
        ) : (
          <div
            className={styles.messageText}
            dangerouslySetInnerHTML={{ __html: convertMarkdownToHtml(content) }}
          ></div>
        )}
      </div>
    </div>
  )
}
