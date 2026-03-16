import { useState, useRef, useCallback, useEffect } from 'react'
import styles from './ChatInput.module.scss'

export default function ChatInput({ onSend, onStop, isStreaming, disabled }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  // Auto-resize textarea
  const adjustHeight = useCallback(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [])

  useEffect(() => {
    adjustHeight()
  }, [value, adjustHeight])

  const handleSend = useCallback(() => {
    const trimmed = value.trim()
    if (!trimmed || isStreaming) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }, [value, isStreaming, onSend])

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend]
  )

  // Focus textarea when streaming stops
  useEffect(() => {
    if (!isStreaming) {
      textareaRef.current?.focus()
    }
  }, [isStreaming])

  const canSend = value.trim() && !disabled

  return (
    <div className={styles.inputArea}>
      <div className={styles.inputBox}>
        <textarea
          ref={textareaRef}
          className={styles.textarea}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your question..."
          rows={1}
          disabled={disabled || isStreaming}
        />
        <div className={styles.actions}>
          {isStreaming ? (
            <button
              type="button"
              className={styles.stopBtn}
              onClick={onStop}
              aria-label="Stop"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <rect x="3" y="3" width="10" height="10" rx="2" />
              </svg>
            </button>
          ) : (
            <button
              type="button"
              className={`${styles.sendBtn} ${canSend ? styles.active : ''}`}
              onClick={handleSend}
              disabled={!canSend}
              aria-label="Send"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M2.5 1.75a.75.75 0 0 1 1.06-.02L8 6.06l4.44-4.33a.75.75 0 1 1 1.05 1.07L8.53 7.7a.75.75 0 0 1-1.06 0L2.52 2.82a.75.75 0 0 1-.02-1.07Z" transform="rotate(-90 8 8)" />
              </svg>
            </button>
          )}
        </div>
      </div>
      <p className={styles.hint}>
        <kbd>Enter</kbd> to send, <kbd>Shift + Enter</kbd> for new line
      </p>
    </div>
  )
}
