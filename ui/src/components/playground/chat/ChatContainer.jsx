import { useState, useCallback, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { AGENT } from '@/utils/constants'
import { getHistory, askQuestion, abortRendering } from '@/api/chatApi'
import { getReference } from '@/api/adminApi'
import { connect, refresh } from '@/api/connectApi'
import { useStore } from '@/store'
import ChatSetting from '../setting/ChatSetting'
import ChatHeader from './ChatHeader'
import ChatBody from './ChatBody'
import ReferenceContainer from '../chat-data/ReferenceContainer'
import PromptContainer from '../chat-data/PromptContainer'
import styles from './ChatContainer.module.scss'

export default function ChatContainer() {
  const { agent } = useParams()
  const insertReferenceItem = useStore((state) => state.insertReferenceItem)

  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isAnswering, setIsAnswering] = useState(false)
  const [showSetting, setShowSetting] = useState(false)
  const [gptVersion, setGptVersion] = useState('')
  const [askDisabled, setAskDisabled] = useState(false)

  const lastAiIndexRef = useRef(undefined)
  const messagesRef = useRef([])
  const startedRef = useRef(false)

  const handleChangeAskDisablity = useCallback((disabled) => {
    setAskDisabled(disabled)
  }, [])

  const setConnection = useCallback((version) => {
    setIsConnected(true)
    if (version) setGptVersion(version)
  }, [])

  const insertMessage = useCallback((role, message) => {
    if (role === 'ai') {
      lastAiIndexRef.current = 0
    } else {
      lastAiIndexRef.current = (lastAiIndexRef.current ?? -1) + 1
    }
    messagesRef.current = [{ role, message }, ...messagesRef.current]
    setMessages([...messagesRef.current])
  }, [])

  const setReferenceItem = useCallback(
    (cat, questionData) => {
      const data = { agent: questionData.agent, prompt: questionData.prompt }

      getReference(cat, data)
        .then((res) => {
          const reference = {
            question: questionData.alternativePrompt || questionData.prompt,
            reference: res.data.data.refer,
            answer: '...',
            created: new Date()
          }
          insertReferenceItem({ agent: cat, reference })
        })
        .catch((e) => console.log(e))
    },
    [insertReferenceItem]
  )

  const startAnswering = useCallback(() => {
    setIsLoading(false)
    setIsAnswering(true)
  }, [])

  const onAnswering = useCallback((chunk) => {
    const idx = lastAiIndexRef.current
    messagesRef.current = messagesRef.current.map((msg, i) =>
      i === idx ? { ...msg, message: msg.message + chunk } : msg
    )
    setMessages([...messagesRef.current])
  }, [])

  const endAnswering = useCallback(() => {
    setIsLoading(false)
    setIsAnswering(false)
  }, [])

  const stopAnswering = useCallback(() => {
    setIsAnswering(false)
    abortRendering()
  }, [])

  const setHistoryMessages = useCallback((prevMessages) => {
    const reversedMessages = [...prevMessages].reverse()
    messagesRef.current = [...messagesRef.current, ...reversedMessages]
    setMessages([...messagesRef.current])
  }, [])

  const handleSubmitQuestion = useCallback(
    async (questionData) => {
      let questionMessage = questionData.alternativePrompt || questionData.prompt

      insertMessage('human', questionMessage)
      setReferenceItem(agent, questionData)
      insertMessage('ai', '')

      setIsLoading(true)

      askQuestion(agent, questionData, startAnswering, onAnswering, endAnswering)
    },
    [agent, insertMessage, setReferenceItem, startAnswering, onAnswering, endAnswering]
  )

  const handleShowSetting = useCallback(() => {
    setShowSetting((prev) => !prev)
  }, [])

  // Start connecting on mount
  const startConnecting = useCallback(async () => {
    try {
      await connect(agent, setConnection)

      getHistory(agent)
        .then((res) => {
          const msgs = res.data.data
          if (msgs.length > 0) {
            setHistoryMessages(msgs)
          }
        })
        .catch((e) => {
          if (e.response?.status === 401) {
            refresh(agent)
          }
          console.log(e)
        })
    } catch (e) {
      console.log('Connect Error', e)
    }
  }, [agent, setConnection, setHistoryMessages])

  if (!startedRef.current) {
    startedRef.current = true
    startConnecting()
  }

  return (
    <div className={styles['chat-container']}>
      {showSetting && <ChatSetting onClose={handleShowSetting} />}
      <ChatHeader
        agent={agent}
        title={agent === AGENT.CS ? '\uC194\uB85C\uBAAC' : 'UX GPT'}
        info={isConnected ? '\uC811\uC18D \uC911' : '\uC811\uC18D \uC548\uB428'}
        onOpenSetting={handleShowSetting}
      />
      <div className={styles['chat-section-layout']}>
        <ReferenceContainer agent={agent} />
        <ChatBody
          agent={agent}
          messages={messages}
          isLoading={isLoading}
          isAnswering={isAnswering}
          disabled={askDisabled}
          onSubmitQuestion={handleSubmitQuestion}
          stop={stopAnswering}
        />
        <PromptContainer agent={agent} onDisable={handleChangeAskDisablity} />
      </div>
    </div>
  )
}
