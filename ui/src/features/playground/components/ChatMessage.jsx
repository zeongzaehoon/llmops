import { useCallback, useState } from 'react'
import { updateRating } from '@/api/chat'
import styles from './ChatMessage.module.scss'

/**
 * Convert basic markdown to HTML.
 * Handles: headers, bold, italic, code blocks, inline code, lists, blockquotes.
 */
function markdownToHtml(text) {
  if (!text) return ''

  let html = text
    // Code blocks (``` ... ```)
    .replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code class="lang-$1">$2</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Headers
    .replace(/^##### (.+)$/gm, '<h5>$1</h5>')
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold and italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Blockquotes
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // Unordered lists
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    // Ordered lists
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Wrap consecutive <li> items in <ul>
    .replace(/((<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
    // Line breaks (but not inside pre/code blocks)
    .replace(/\n/g, '<br/>')
    // Clean up multiple <br/> from blocks
    .replace(/<br\/><br\/>/g, '<br/>')
    // Clean up br after block elements
    .replace(/(<\/(h[1-6]|pre|blockquote|ul|ol|li)>)<br\/>/g, '$1')
    .replace(/<br\/>(<(h[1-6]|pre|blockquote|ul|ol))/g, '$1')

  return html
}

export default function ChatMessage({
  message,
  isStreaming = false,
  agent,
}) {
  const { id, role, content, askCode, rating: initialRating, stopped } = message
  const [rating, setRating] = useState(initialRating || null)
  const [copied, setCopied] = useState(false)

  const isUser = role === 'user'
  const isAssistant = role === 'assistant'
  const showRating = isAssistant && !isStreaming && content

  const handleRate = useCallback(
    async (value) => {
      const newRating = rating === value ? null : value
      setRating(newRating)
      if (askCode && agent) {
        try {
          await updateRating(agent, {
            ask_code: askCode,
            rating: newRating,
          })
        } catch {
          // Silently fail
        }
      }
    },
    [rating, askCode, agent]
  )

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(content || '').then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }, [content])

  return (
    <div className={`${styles.messageRow} ${styles[role]}`}>
      <div className={styles.bubble}>
        {isUser ? (
          <div className={styles.content}>{content}</div>
        ) : (
          <div
            className={styles.content}
            dangerouslySetInnerHTML={{ __html: markdownToHtml(content) }}
          />
        )}
        {isStreaming && <span className={styles.cursor} />}
        {stopped && (
          <div className={styles.stopped}>[Generation stopped]</div>
        )}

        {(showRating || !isUser) && (
          <div className={`${styles.actions} ${showRating ? styles.visible : ''}`}>
            {isAssistant && (
              <>
                <button
                  className={`${styles.actionBtn} ${rating === 'good' ? styles.rated : ''}`}
                  onClick={() => handleRate('good')}
                  title="Good response"
                >
                  &#x1F44D;
                </button>
                <button
                  className={`${styles.actionBtn} ${rating === 'bad' ? styles.rated : ''}`}
                  onClick={() => handleRate('bad')}
                  title="Bad response"
                >
                  &#x1F44E;
                </button>
              </>
            )}
            <button
              className={styles.actionBtn}
              onClick={handleCopy}
              title="Copy"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
