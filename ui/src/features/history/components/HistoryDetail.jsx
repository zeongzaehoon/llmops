import { useState } from 'react'
import toast from 'react-hot-toast'
import Button from '@/components/inputs/Button'
import EmptyState from '@/components/feedback/EmptyState'
import { updateMemo, downloadQuestion } from '@/api/prompts'
import styles from './HistoryDetail.module.scss'

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function HistoryDetail({ conversation }) {
  const [memo, setMemo] = useState(conversation?.memo || '')
  const [saving, setSaving] = useState(false)
  const [downloading, setDownloading] = useState(false)

  if (!conversation) {
    return (
      <div className={styles.empty}>
        <EmptyState
          title="Select a conversation"
          description="Choose a conversation from the list to view details"
        />
      </div>
    )
  }

  const handleSaveMemo = async () => {
    setSaving(true)
    try {
      await updateMemo({
        ask_id: conversation._id || conversation.ask_id,
        memo,
      })
      toast.success('Memo saved')
    } catch {
      toast.error('Failed to save memo')
    } finally {
      setSaving(false)
    }
  }

  const handleDownload = async () => {
    setDownloading(true)
    try {
      const res = await downloadQuestion({
        ask_id: conversation._id || conversation.ask_id,
      })
      const blob = new Blob([res.data], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `conversation-${conversation._id || 'export'}.txt`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error('Failed to download')
    } finally {
      setDownloading(false)
    }
  }

  const messages = conversation.messages || conversation.history || []
  const question = conversation.question || conversation.ask
  const answer = conversation.answer

  const displayMessages =
    messages.length > 0
      ? messages
      : [
          ...(question ? [{ role: 'user', content: question }] : []),
          ...(answer ? [{ role: 'assistant', content: answer }] : []),
        ]

  return (
    <div className={styles.detail}>
      <div className={styles.toolbar}>
        <div className={styles.memoField}>
          <input
            type="text"
            className={styles.memoInput}
            value={memo}
            onChange={(e) => setMemo(e.target.value)}
            placeholder="Add a memo..."
          />
          <Button size="sm" variant="secondary" onClick={handleSaveMemo} loading={saving}>
            Save
          </Button>
        </div>
        <Button size="sm" variant="ghost" onClick={handleDownload} loading={downloading}>
          Download
        </Button>
      </div>

      {conversation.rating != null && (
        <div className={styles.ratingBar}>
          <span className={styles.ratingLabel}>Rating:</span>
          <span className={styles.ratingValue}>
            {conversation.rating > 0 ? '+' : ''}{conversation.rating}
          </span>
        </div>
      )}

      <div className={styles.metaBar}>
        {conversation.model && (
          <span className={styles.metaItem}>Model: {conversation.model}</span>
        )}
        {conversation.tokenCount != null && (
          <span className={styles.metaItem}>Tokens: {conversation.tokenCount}</span>
        )}
        {(conversation.regDate || conversation.createdAt) && (
          <span className={styles.metaItem}>
            {formatDate(conversation.regDate || conversation.createdAt)}
          </span>
        )}
      </div>

      <div className={styles.messages}>
        {displayMessages.map((msg, idx) => (
          <div
            key={idx}
            className={`${styles.bubble} ${
              msg.role === 'user' ? styles.user : styles.assistant
            }`}
          >
            <span className={styles.role}>{msg.role === 'user' ? 'You' : 'AI'}</span>
            <div className={styles.content}>{msg.content}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
