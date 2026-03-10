import { useRef } from 'react'
import { useTranslation } from 'react-i18next'
import MessageContainer from './MessageContainer'
import AskContainer from './AskContainer'
import chatImgAll from '@/assets/image--chat-img-all.svg'
import chatImgAllM from '@/assets/image--chat-img-all-m.svg'
import styles from './ChatBody.module.scss'

export default function ChatBody({ messages, isLoading, isAnswering, onSubmitQuestion, onStop }) {
  const { t } = useTranslation()
  const scrollerRef = useRef(null)

  const recommend = t('recommend', { returnObjects: true })

  const checkLoadingComponents = (index) => {
    if (!isLoading) return false
    return index === 0
  }

  const handleClickQuestion = (question, idx) => {
    scrollToBottom()
    const questionData = {
      prompt: question,
      fixedAnswer: idx
    }
    onSubmitQuestion(questionData)
  }

  const scrollToBottom = () => {
    scrollerRef.current.scrollTo({
      top: 0
    })
  }

  return (
    <div className={styles.chatBody}>
      <div ref={scrollerRef} className={styles.chatBodyWrapper}>
        {messages.map((message, index) => (
          <div key={index}>
            <MessageContainer
              role={message.role}
              content={message.message}
              isLoadingItem={checkLoadingComponents(index)}
            />
          </div>
        ))}
        <MessageContainer role="ai" content={t('welcomeMessage')} />
        <div className={styles.recommendQuestionList}>
          {Array.isArray(recommend) &&
            recommend.map((question, idx) => (
              <div
                className={styles.recommendedQuestionItem}
                key={idx}
                onClick={() => handleClickQuestion(question, idx + 1)}
              >
                {question}
              </div>
            ))}
        </div>
        <div className={styles.chatBodyHeader}>
          <img className={`${styles.headerImg} ${styles.pc}`} src={chatImgAll} alt="" />
          <img className={`${styles.headerImg} ${styles.mobile}`} src={chatImgAllM} alt="" />
        </div>
      </div>
      <AskContainer
        isLoading={isLoading}
        isAnswering={isAnswering}
        onSubmitQuestion={onSubmitQuestion}
      />
    </div>
  )
}
