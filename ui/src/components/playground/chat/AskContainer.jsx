import { useState, useRef, useCallback, useEffect } from 'react'
import { getModelList } from '@/api/adminApi'
import iconSend from '@/assets/icon--send.svg'
import styles from './AskContainer.module.scss'

export default function AskContainer({
  agent,
  chatOptions,
  isLoading,
  isAnswering,
  disabled,
  stop,
  onChangeOptions,
  onSubmit
}) {
  const [question, setQuestion] = useState('')

  const textareaRef = useRef(null)
  const modelListFetchedRef = useRef(false)

  useEffect(() => {
    if (modelListFetchedRef.current) return
    modelListFetchedRef.current = true

    getModelList()
      .then((res) => {
        onChangeOptions?.({ model: res.data.data.baseModel })
        const modelArr = res.data.data.modelList || []
        // modelList stored for potential future use
      })
      .catch((e) => {
        console.log(e)
      })
  }, [onChangeOptions])

  const checkIsEmpty = useCallback(() => {
    return question.length === 0
  }, [question])

  const handleSubmit = useCallback(() => {
    if (checkIsEmpty()) return

    let data = {
      prompt: question,
      agent: agent
    }

    onSubmit?.(data)

    setQuestion('')
  }, [checkIsEmpty, question, agent, onSubmit])

  const handleResizeTextArea = useCallback(() => {
    const textarea = textareaRef.current
    if (!textarea) return
    if (textarea.scrollHeight > 180) return
    textarea.style.height = 'auto'
    textarea.style.height = textarea.scrollHeight + 'px'
  }, [])

  const handlePress = useCallback(
    (e) => {
      if (e.keyCode !== 13) return
      if (e.shiftKey) return

      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
      e.preventDefault()
      handleSubmit()
    },
    [handleSubmit]
  )

  const handleClickStop = useCallback(() => {
    stop?.()
  }, [stop])

  return (
    <div className={`${styles['ask-container-wrapper']} ${disabled ? styles['disabled'] : ''}`}>
      <div className={styles['ask-container']}>
        <div className={styles['ask-container-header']}>
          <div></div>
          {(isLoading || isAnswering) ? (
            <div className={styles['pause']} onClick={handleClickStop}>
              <div className={styles['pause-icon']}>
                <div></div>
                <div></div>
              </div>
              <p>{'\uC0DD\uC131 \uBA48\uCD94\uAE30'}</p>
            </div>
          ) : null}
        </div>
        <div className={styles['ask-wrapper']}>
          <div className={styles['textarea-wrapper']}>
            <textarea
              ref={textareaRef}
              rows="1"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask anything..."
              disabled={disabled}
              onInput={handleResizeTextArea}
              onKeyPress={handlePress}
            />
          </div>
          <div className={styles['button-wrapper']}>
            <button
              className={`${checkIsEmpty() ? styles['empty'] : ''} ${isAnswering ? styles['answering'] : ''}`}
              onClick={handleSubmit}
            >
              <img alt="send" src={iconSend} />
              <div className={styles['droplet_spinner']}>
                <div className={styles['droplet']}></div>
                <div className={styles['droplet']}></div>
                <div className={styles['droplet']}></div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
