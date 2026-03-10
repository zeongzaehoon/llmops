import { useRef, useEffect, useState, useCallback } from 'react'
import ChatMessage from './ChatMessage'
import styles from './ChatBody.module.scss'

export default function ChatBody({
  messages,
  isStreaming,
  showTyping,
  agent,
}) {
  const containerRef = useRef(null)
  const bottomRef = useRef(null)
  const [showScrollPill, setShowScrollPill] = useState(false)
  const userScrolledRef = useRef(false)

  const scrollToBottom = useCallback((behavior = 'smooth') => {
    bottomRef.current?.scrollIntoView({ behavior })
    userScrolledRef.current = false
    setShowScrollPill(false)
  }, [])

  // Detect user scroll
  const handleScroll = useCallback(() => {
    const el = containerRef.current
    if (!el) return
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    const isNearBottom = distanceFromBottom < 60

    if (isNearBottom) {
      userScrolledRef.current = false
      setShowScrollPill(false)
    } else {
      userScrolledRef.current = true
      setShowScrollPill(true)
    }
  }, [])

  // Auto-scroll on new content unless user scrolled up
  useEffect(() => {
    if (!userScrolledRef.current) {
      scrollToBottom('auto')
    }
  }, [messages, isStreaming, scrollToBottom])

  // Scroll to bottom on initial mount
  useEffect(() => {
    scrollToBottom('auto')
  }, [scrollToBottom])

  const isEmpty = messages.length === 0 && !isStreaming

  return (
    <div className={styles.body} ref={containerRef} onScroll={handleScroll}>
      {isEmpty ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyTitle}>Start a conversation</div>
          <div className={styles.emptyDescription}>
            Type a message below to begin chatting
          </div>
        </div>
      ) : (
        <div className={styles.messageList}>
          {messages.map((msg, idx) => (
            <ChatMessage
              key={msg.id}
              message={msg}
              isStreaming={
                isStreaming &&
                msg.role === 'assistant' &&
                idx === messages.length - 1
              }
              agent={agent}
            />
          ))}
          {showTyping && (
            <div className={styles.typingIndicator}>
              <span className={styles.dot} />
              <span className={styles.dot} />
              <span className={styles.dot} />
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}

      {showScrollPill && (
        <button className={styles.scrollPill} onClick={() => scrollToBottom()}>
          Scroll to bottom
        </button>
      )}
    </div>
  )
}
