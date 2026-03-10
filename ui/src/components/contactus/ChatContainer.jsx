import { useState, useEffect, useRef, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { askQuestion, abortRendering } from '@/api/chatApi'
import { connect } from '@/api/connectApi'
import { askAgent } from '@/utils/constants'
import ChatHeader from './ChatHeader'
import ChatBody from './ChatBody'
import LoadingContainer from './LoadingContainer'
import styles from './ChatContainer.module.scss'

export default function ChatContainer() {
  const { i18n } = useTranslation()
  const agent = 'contactUs'

  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isAnswering, setIsAnswering] = useState(false)
  const [gptVersion, setGptVersion] = useState('')
  const [initialLoading, setInitialLoading] = useState(true)

  const userInfoRef = useRef(null)
  const messagesRef = useRef([])

  const setConnection = useCallback((version) => {
    setIsConnected(true)
    if (version) setGptVersion(version)
  }, [])

  const startConnecting = useCallback(() => {
    try {
      connect(agent, setConnection)
    } catch (e) {
      console.log('Connect Error', e)
    }
  }, [setConnection])

  const startAnswering = useCallback(() => {
    setIsLoading(false)
    setIsAnswering(true)
  }, [])

  const onAnswering = useCallback((chunk) => {
    messagesRef.current = [...messagesRef.current]
    messagesRef.current[0] = {
      ...messagesRef.current[0],
      message: messagesRef.current[0].message + chunk
    }
    setMessages([...messagesRef.current])
  }, [])

  const endAnswering = useCallback(() => {
    setIsLoading(false)
    setIsAnswering(false)
  }, [])

  const handleSubmitQuestion = useCallback(
    (question) => {
      const newMessages = [
        { role: 'ai', message: '' },
        { role: 'human', message: question.prompt },
        ...messagesRef.current
      ]
      messagesRef.current = newMessages
      setMessages([...newMessages])
      setIsLoading(true)

      const questionData = JSON.stringify({
        ...question,
        agent: agent,
        info: userInfoRef.current
      })

      askQuestion(agent, questionData, startAnswering, onAnswering, endAnswering)
    },
    [startAnswering, onAnswering, endAnswering]
  )

  const initChatting = useCallback(
    (initialMessage) => {
      userInfoRef.current = initialMessage.info
      const lang = initialMessage.info.lang

      if (i18n.languages && i18n.languages.indexOf(lang) !== -1) {
        i18n.changeLanguage(lang)
        document.documentElement.setAttribute('lang', lang)
      }

      if (initialMessage.info['askCategory'] in askAgent) {
        initialMessage.info['askCategory'] = askAgent[initialMessage.info['askCategory']]
      }

      const currentWidth = window.innerWidth
      const questionIncluded = initialMessage.content && initialMessage.content.length > 0

      if (currentWidth >= 996) {
        setTimeout(() => {
          setInitialLoading(false)
          setTimeout(() => {
            if (questionIncluded) handleSubmitQuestion({ prompt: initialMessage.content })
          }, 500)
        }, 1500)
      } else {
        setInitialLoading(false)
        setTimeout(() => {
          if (questionIncluded) handleSubmitQuestion({ prompt: initialMessage.content })
        }, 1000)
      }
    },
    [i18n, handleSubmitQuestion]
  )

  useEffect(() => {
    startConnecting()

    const handleMessage = (e) => {
      if (e.data.event === 'sendQuestion' && e.data.msg) {
        initChatting(e.data.msg)
      }
    }

    window.addEventListener('message', handleMessage)
    return () => {
      window.removeEventListener('message', handleMessage)
    }
  }, [startConnecting, initChatting])

  const stopAnswering = () => {
    setIsAnswering(false)
    abortRendering()
  }

  const resetHistoryMessages = () => {
    messagesRef.current = []
    setMessages([])
    localStorage.removeItem('contactUs_accessToken')
    localStorage.removeItem('contactUs_refreshToken')
  }

  return (
    <div className={styles.chatContainer}>
      {initialLoading ? (
        <LoadingContainer />
      ) : (
        <div className={styles.chatContainerWrapper}>
          <ChatHeader
            agent={agent}
            isConnected={isConnected}
            gptVersion={gptVersion}
            reset={resetHistoryMessages}
          />
          <ChatBody
            messages={messages}
            isLoading={isLoading}
            isAnswering={isAnswering}
            onSubmitQuestion={handleSubmitQuestion}
            onStop={stopAnswering}
          />
        </div>
      )}
    </div>
  )
}
