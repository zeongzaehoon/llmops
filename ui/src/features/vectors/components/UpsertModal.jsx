import { useState, useRef } from 'react'
import Modal from '@/components/overlay/Modal'
import Button from '@/components/inputs/Button'
import styles from './UpsertModal.module.scss'

const INITIAL_STATE = {
  agent: 'main',
  textsRaw: '',
  metaPairs: [{ key: '', value: '' }],
}

export default function UpsertModal({ open, onClose, onUpsert, isLoading = false }) {
  const [form, setForm] = useState(INITIAL_STATE)
  const fileRef = useRef(null)

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleMetaChange = (index, field, value) => {
    setForm((prev) => {
      const pairs = [...prev.metaPairs]
      pairs[index] = { ...pairs[index], [field]: value }
      return { ...prev, metaPairs: pairs }
    })
  }

  const addMetaPair = () => {
    setForm((prev) => ({
      ...prev,
      metaPairs: [...prev.metaPairs, { key: '', value: '' }],
    }))
  }

  const removeMetaPair = (index) => {
    setForm((prev) => ({
      ...prev,
      metaPairs: prev.metaPairs.filter((_, i) => i !== index),
    }))
  }

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (ev) => {
      const content = ev.target.result
      setForm((prev) => ({
        ...prev,
        textsRaw: prev.textsRaw ? `${prev.textsRaw}\n${content}` : content,
      }))
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  const handleSubmit = () => {
    const rawText = form.textsRaw.trim()
    if (!rawText) return

    let texts
    try {
      const parsed = JSON.parse(rawText)
      texts = Array.isArray(parsed) ? parsed : [rawText]
    } catch {
      texts = rawText.split('\n').filter((line) => line.trim())
    }

    const metadata = {}
    form.metaPairs.forEach(({ key, value }) => {
      if (key.trim()) {
        metadata[key.trim()] = value
      }
    })

    onUpsert({
      texts,
      agent: form.agent || 'main',
      metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
    })
  }

  const handleClose = () => {
    setForm(INITIAL_STATE)
    onClose?.()
  }

  return (
    <Modal open={open} onClose={handleClose} size="lg">
      <div className={styles.modal}>
        <h2 className={styles.title}>Upsert Vectors</h2>

        <div className={styles.field}>
          <label className={styles.label}>Agent</label>
          <input
            type="text"
            className={styles.input}
            value={form.agent}
            onChange={(e) => handleChange('agent', e.target.value)}
            placeholder="main"
          />
        </div>

        <div className={styles.field}>
          <div className={styles.labelRow}>
            <label className={styles.label}>Texts</label>
            <button
              type="button"
              className={styles.fileBtn}
              onClick={() => fileRef.current?.click()}
            >
              Upload File
            </button>
            <input
              ref={fileRef}
              type="file"
              accept=".txt,.csv,.json"
              className={styles.fileInput}
              onChange={handleFileUpload}
            />
          </div>
          <textarea
            className={styles.textarea}
            value={form.textsRaw}
            onChange={(e) => handleChange('textsRaw', e.target.value)}
            placeholder="Enter texts (one per line) or a JSON array..."
            rows={6}
          />
          <span className={styles.hint}>
            One text per line, or paste a JSON array of strings
          </span>
        </div>

        <div className={styles.field}>
          <div className={styles.labelRow}>
            <label className={styles.label}>Metadata</label>
            <button type="button" className={styles.addBtn} onClick={addMetaPair}>
              + Add Field
            </button>
          </div>
          <div className={styles.metaList}>
            {form.metaPairs.map((pair, idx) => (
              <div key={idx} className={styles.metaRow}>
                <input
                  type="text"
                  className={styles.input}
                  value={pair.key}
                  onChange={(e) => handleMetaChange(idx, 'key', e.target.value)}
                  placeholder="Key"
                />
                <input
                  type="text"
                  className={styles.input}
                  value={pair.value}
                  onChange={(e) => handleMetaChange(idx, 'value', e.target.value)}
                  placeholder="Value"
                />
                <button
                  type="button"
                  className={styles.removeBtn}
                  onClick={() => removeMetaPair(idx)}
                  disabled={form.metaPairs.length === 1}
                >
                  x
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.actions}>
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            loading={isLoading}
            disabled={!form.textsRaw.trim()}
          >
            Upsert
          </Button>
        </div>
      </div>
    </Modal>
  )
}
