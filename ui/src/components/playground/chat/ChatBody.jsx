import { useState, useRef, useEffect, useCallback } from 'react'
import AskContainer from './AskContainer'
import MessageContainer from './MessageContainer'
import RecommendationContainer from './RecommendationContainer'
import { LANGS, WELCOME_MESSAGE } from '@/utils/constants'
import iconChevronBottom from '@/assets/icon--chevronBottom.svg'
import styles from './ChatBody.module.scss'

export default function ChatBody({
  agent,
  messages,
  isLoading,
  isAnswering,
  disabled,
  onSubmitQuestion,
  stop
}) {
  const [chatOptions, setChatOptions] = useState({
    model: null,
    lang: Object.keys(LANGS)[0],
    testMode: false
  })
  const [isAutoScrollBtnVisible, setIsAutoScrollBtnVisible] = useState(false)

  const scrollerRef = useRef(null)
  const scrollHandlerRef = useRef(null)

  const getWelcomeMessage = () => {
    return { role: 'ai', message: WELCOME_MESSAGE[agent] || WELCOME_MESSAGE['main'] }
  }

  const checkLoadingComponents = (index) => {
    if (!isLoading) return false
    return index === 0
  }

  const scrollToBottom = useCallback(() => {
    if (!scrollerRef.current) return
    scrollerRef.current.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }, [])

  const checkShowRecommendation = () => {
    return messages.length === 0
  }

  const changeChatOptions = useCallback((options) => {
    setChatOptions((prev) => ({ ...prev, ...options }))
  }, [])

  const submit = useCallback(
    (data) => {
      const scroller = scrollerRef.current
      if (scroller && scroller.scrollTop !== 0) {
        scrollToBottom()
        const handler = () => {
          if (scroller.scrollTop === 0) {
            setTimeout(() => {
              onSubmitQuestion(data)
              scroller.removeEventListener('scroll', handler)
            }, 300)
          }
        }
        scrollHandlerRef.current = handler
        scroller.addEventListener('scroll', handler)
      } else {
        onSubmitQuestion(data)
      }
    },
    [onSubmitQuestion, scrollToBottom]
  )

  const handleScrollBtn = useCallback(() => {
    if (scrollerRef.current) {
      setIsAutoScrollBtnVisible(scrollerRef.current.scrollTop !== 0)
    }
  }, [])

  useEffect(() => {
    const chatScroller = document.querySelector('#chat-scroller')
    if (chatScroller) {
      scrollerRef.current = chatScroller
      chatScroller.addEventListener('scroll', handleScrollBtn)
    }

    return () => {
      if (scrollerRef.current) {
        scrollerRef.current.removeEventListener('scroll', handleScrollBtn)
      }
    }
  }, [handleScrollBtn])

  return (
    <div className={styles['chat-body']}>
      <div id="chat-scroller" className={styles['chat-body-wrapper']}>
        {messages.map((item, index) => (
          <div key={index}>
            <MessageContainer
              agent={agent}
              message={item}
              isLoadingItem={checkLoadingComponents(index)}
              chatOptions={chatOptions}
              onSubmit={submit}
            />
          </div>
        ))}
        <MessageContainer agent={agent} message={getWelcomeMessage()} />
      </div>
      <div>
        <RecommendationContainer
          agent={agent}
          onSubmit={submit}
          style={{ display: checkShowRecommendation() ? '' : 'none' }}
        />
        <AskContainer
          agent={agent}
          chatOptions={chatOptions}
          isLoading={isLoading}
          isAnswering={isAnswering}
          disabled={disabled}
          stop={stop}
          onChangeOptions={changeChatOptions}
          onSubmit={submit}
        />
      </div>
      <div
        className={styles['auto-scroll-button']}
        style={{ display: isAutoScrollBtnVisible ? '' : 'none' }}
        onClick={scrollToBottom}
      >
        <img src={iconChevronBottom} alt={'\uC544\uB798\uB85C \uC2A4\uD06C\uB864 \uBC84\uD2BC'} />
      </div>
    </div>
  )
}
