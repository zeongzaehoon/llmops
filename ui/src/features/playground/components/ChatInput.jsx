import { useState, useRef, useCallback, useEffect } from 'react'
import Button from '@/components/inputs/Button'
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
    // Reset height
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

  return (
    <div className={styles.inputArea}>
      <div className={styles.textareaWrap}>
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
      </div>
      <div className={styles.buttons}>
        {isStreaming ? (
          <Button variant="danger" size="sm" onClick={onStop}>
            Stop
          </Button>
        ) : (
          <Button
            variant="primary"
            size="sm"
            onClick={handleSend}
            disabled={!value.trim() || disabled}
          >
            Send
          </Button>
        )}
      </div>
    </div>
  )
}
