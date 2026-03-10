import { useState, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import styles from './AskContainer.module.scss'

export default function AskContainer({ isLoading, isAnswering, onSubmitQuestion }) {
  const { t } = useTranslation()
  const [question, setQuestion] = useState('')
  const textareaRef = useRef(null)

  const handleSubmit = () => {
    if (checkIsEmpty()) return

    onSubmitQuestion({ prompt: question })
    setQuestion('')
  }

  const handleResizeTextArea = () => {
    const textarea = textareaRef.current
    if (textarea.scrollHeight > 180) return
    textarea.style.height = 'auto'
    textarea.style.height = textarea.scrollHeight + 'px'
  }

  const handlePress = (e) => {
    if (e.keyCode !== 13) return
    if (e.shiftKey) return

    textareaRef.current.style.height = 'auto'
    e.preventDefault()
    handleSubmit()
  }

  const checkIsEmpty = () => {
    return question.length === 0
  }

  const handleChange = (e) => {
    setQuestion(e.target.value)
    handleResizeTextArea()
  }

  return (
    <div className={styles.askWrapper}>
      <div className={styles.textareaWrapper}>
        <textarea
          ref={textareaRef}
          rows="1"
          value={question}
          placeholder={t('askPlaceHolder')}
          onInput={handleResizeTextArea}
          onChange={handleChange}
          onKeyPress={handlePress}
        />
      </div>
      <div className={styles.buttonWrapper}>
        <button
          className={`${styles.sendButton} ${checkIsEmpty() ? styles.empty : ''} ${isAnswering ? styles.answering : ''}`}
          onClick={handleSubmit}
        >
          <div className={styles.sendButtonIcon} />
        </button>
      </div>
    </div>
  )
}
