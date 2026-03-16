import { useCallback } from 'react'
import Button from '@/components/inputs/Button'
import { useAppStore } from '@/store/useAppStore'
import { useModels, useCurrentModel } from '@/hooks/queries/useModels'
import { setVendorAndModel } from '@/api/agents'
import styles from './ChatHeader.module.scss'

const LANGUAGES = [
  { value: '한국어', label: 'ko' },
  { value: 'English', label: 'en' },
  { value: '日本語', label: 'ja' },
]

export default function ChatHeader({ agent, onNewChat }) {
  const { data: models = [] } = useModels()
  const { data: currentModel } = useCurrentModel(agent)
  const { chatOptions, setChatOptions } = useAppStore()

  const handleModelChange = useCallback(
    (e) => {
      const selected = models.find((m) => m._id === e.target.value)
      if (selected) {
        setChatOptions({ model: selected })
        setVendorAndModel({
          agent,
          vendor: selected.vendor,
          model: selected.model,
        })
      }
    },
    [models, agent, setChatOptions]
  )

  const handleLangChange = useCallback(
    (e) => {
      setChatOptions({ lang: e.target.value })
    },
    [setChatOptions]
  )

  const handleTestToggle = useCallback(() => {
    setChatOptions({ test: !chatOptions.test })
  }, [chatOptions.test, setChatOptions])

  const activeModelId = chatOptions.model?._id || currentModel?._id || ''

  return (
    <div className={styles.header}>
      <div className={styles.left}>
        <span className={styles.agentName}>{agent}</span>
      </div>

      <div className={styles.controls}>
        <div className={styles.selectGroup}>
          <span className={styles.selectLabel}>Model</span>
          <select
            className={styles.select}
            value={activeModelId}
            onChange={handleModelChange}
          >
            {!activeModelId && <option value="">Select model</option>}
            {models.map((m) => (
              <option key={m._id} value={m._id}>
                {m.vendor}/{m.model}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.selectGroup}>
          <span className={styles.selectLabel}>Lang</span>
          <select
            className={styles.select}
            value={chatOptions.lang}
            onChange={handleLangChange}
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.toggleGroup}>
          <span className={styles.toggleLabel}>Test</span>
          <button
            className={`${styles.toggle} ${chatOptions.test ? styles.active : ''}`}
            onClick={handleTestToggle}
            type="button"
          >
            <span className={styles.toggleKnob} />
          </button>
        </div>

        <Button variant="ghost" size="sm" onClick={onNewChat}>
          + New Chat
        </Button>
      </div>
    </div>
  )
}
