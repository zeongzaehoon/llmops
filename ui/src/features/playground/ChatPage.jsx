import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useSSE } from '@/hooks/useSSE'
import { useHistory } from '@/hooks/queries/useHistory'
import { useAppStore } from '@/store/useAppStore'
import ChatHeader from './components/ChatHeader'
import ChatBody from './components/ChatBody'
import ChatInput from './components/ChatInput'
import HistorySidebar from './components/HistorySidebar'
import styles from './ChatPage.module.scss'

let msgIdCounter = 0
function nextId() {
  return `msg-${Date.now()}-${++msgIdCounter}`
}

export default function ChatPage() {
  const { agent } = useParams()
  const { isConnected, isLoading: isConnecting, error: authError, connect } = useAuth()
  const { content, askCode, isStreaming, error: streamError, ask, abort } = useSSE()
  const { data: history = [] } = useHistory(agent)
  const { chatOptions } = useAppStore()

  const [messages, setMessages] = useState([])
  const [showTyping, setShowTyping] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [activeHistoryId, setActiveHistoryId] = useState(null)
  const [errorBanner, setErrorBanner] = useState(null)

  // Track the current streaming assistant message id
  const streamingMsgIdRef = useRef(null)
  const prevContentRef = useRef('')

  // Connect on mount
  useEffect(() => {
    if (!isConnected && !isConnecting) {
      connect(agent)
    }
  }, [agent, isConnected, isConnecting, connect])

  // Show stream errors
  useEffect(() => {
    if (streamError) {
      setErrorBanner(streamError)
    }
  }, [streamError])

  // Handle streaming content updates
  useEffect(() => {
    if (!isStreaming && !content) return

    // When streaming starts and we have no assistant message yet, create one
    if (isStreaming && content && !streamingMsgIdRef.current) {
      setShowTyping(false)
      const id = nextId()
      streamingMsgIdRef.current = id
      setMessages((prev) => [
        ...prev,
        { id, role: 'assistant', content, askCode, rating: null, timestamp: new Date() },
      ])
      prevContentRef.current = content
      return
    }

    // Update existing assistant message with new content
    if (streamingMsgIdRef.current && content !== prevContentRef.current) {
      const msgId = streamingMsgIdRef.current
      setMessages((prev) =>
        prev.map((m) =>
          m.id === msgId ? { ...m, content, askCode: askCode || m.askCode } : m
        )
      )
      prevContentRef.current = content
    }

    // Streaming ended
    if (!isStreaming && streamingMsgIdRef.current) {
      streamingMsgIdRef.current = null
      prevContentRef.current = ''
    }
  }, [content, isStreaming, askCode])

  const handleSend = useCallback(
    (question) => {
      if (!question.trim()) return

      // Add user message
      const userMsg = {
        id: nextId(),
        role: 'user',
        content: question,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, userMsg])
      setShowTyping(true)
      streamingMsgIdRef.current = null
      prevContentRef.current = ''

      // Build payload
      const payload = {
        question,
        company: chatOptions.company || '',
        agent,
        model: chatOptions.model?.model || '',
        lang: chatOptions.lang || '한국어',
        test: chatOptions.test || false,
        session_key: agent,
        graph_id: '',
      }

      ask(agent, payload)
    },
    [agent, chatOptions, ask]
  )

  const handleStop = useCallback(() => {
    abort()
    setShowTyping(false)
    // Mark the current streaming message as stopped
    if (streamingMsgIdRef.current) {
      const msgId = streamingMsgIdRef.current
      setMessages((prev) =>
        prev.map((m) => (m.id === msgId ? { ...m, stopped: true } : m))
      )
      streamingMsgIdRef.current = null
      prevContentRef.current = ''
    }
  }, [abort])

  const handleNewChat = useCallback(() => {
    setMessages([])
    setActiveHistoryId(null)
    streamingMsgIdRef.current = null
    prevContentRef.current = ''
  }, [])

  const handleSelectHistory = useCallback((item) => {
    const id = item._id || item.ask_id
    setActiveHistoryId(id)

    // Convert history item to messages
    const msgs = []
    if (item.question || item.ask) {
      msgs.push({
        id: nextId(),
        role: 'user',
        content: item.question || item.ask,
        timestamp: new Date(item.regDate || 0),
      })
    }
    if (item.answer || item.content) {
      msgs.push({
        id: nextId(),
        role: 'assistant',
        content: item.answer || item.content,
        askCode: item.ask_id,
        rating: item.rating || null,
        timestamp: new Date(item.regDate || 0),
      })
    }
    setMessages(msgs)
  }, [])

  if (isConnecting) {
    return (
      <div className={styles.page}>
        <div className={styles.connectingOverlay}>
          <div className={styles.spinner} />
          <span>Connecting to {agent}...</span>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <HistorySidebar
        history={history}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed((v) => !v)}
        activeId={activeHistoryId}
        onSelect={handleSelectHistory}
      />

      <div className={styles.main}>
        <ChatHeader agent={agent} onNewChat={handleNewChat} />

        {(errorBanner || authError) && (
          <div className={styles.errorBanner}>
            <span>{errorBanner || authError}</span>
            <button
              className={styles.dismissBtn}
              onClick={() => setErrorBanner(null)}
            >
              &#x2715;
            </button>
          </div>
        )}

        <ChatBody
          messages={messages}
          isStreaming={isStreaming}
          showTyping={showTyping && !content}
          agent={agent}
        />

        <ChatInput
          onSend={handleSend}
          onStop={handleStop}
          isStreaming={isStreaming}
          disabled={!isConnected}
        />
      </div>
    </div>
  )
}
