import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import Modal from '@/components/overlay/Modal'
import Button from '@/components/inputs/Button'
import { useCreateServer, useUpdateServer } from '@/hooks/queries/useServers'
import styles from './ServerFormModal.module.scss'

export default function ServerFormModal({ open, onClose, server = null }) {
  const isEdit = !!server
  const createServer = useCreateServer()
  const updateServer = useUpdateServer()

  const [form, setForm] = useState({ name: '', uri: '', token: '', description: '' })

  useEffect(() => {
    if (server) {
      setForm({
        name: server.name || '',
        uri: server.uri || '',
        token: '',
        description: server.description || '',
      })
    } else {
      setForm({ name: '', uri: '', token: '', description: '' })
    }
  }, [server, open])

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!form.name.trim() || !form.uri.trim()) {
      toast.error('Name and URI are required')
      return
    }

    const mutation = isEdit ? updateServer : createServer
    const payload = isEdit
      ? {
          id: server.id,
          name: form.name.trim(),
          uri: form.uri.trim(),
          description: form.description.trim(),
        }
      : {
          name: form.name.trim(),
          uri: form.uri.trim(),
          token: form.token.trim(),
          description: form.description.trim(),
        }

    mutation.mutate(payload, {
      onSuccess: () => {
        toast.success(isEdit ? 'Server updated' : 'Server registered')
        onClose()
      },
      onError: () => toast.error(isEdit ? 'Failed to update server' : 'Failed to register server'),
    })
  }

  const isLoading = createServer.isPending || updateServer.isPending

  return (
    <Modal open={open} onClose={onClose} size="md">
      <form className={styles.form} onSubmit={handleSubmit}>
        <h2 className={styles.title}>{isEdit ? 'Edit Server' : 'Register Server'}</h2>

        <label className={styles.field}>
          <span className={styles.label}>Name</span>
          <input
            type="text"
            className={styles.input}
            value={form.name}
            onChange={handleChange('name')}
            placeholder="mcp-filesystem"
            disabled={isEdit}
          />
        </label>

        <label className={styles.field}>
          <span className={styles.label}>URI</span>
          <input
            type="text"
            className={styles.input}
            value={form.uri}
            onChange={handleChange('uri')}
            placeholder="stdio:// or sse://"
          />
        </label>

        <label className={styles.field}>
          <span className={styles.label}>Token</span>
          <input
            type="password"
            className={styles.input}
            value={form.token}
            onChange={handleChange('token')}
            placeholder={isEdit ? 'Leave blank to keep current token' : 'MCP server auth token'}
          />
        </label>

        <label className={styles.field}>
          <span className={styles.label}>Description</span>
          <textarea
            className={styles.textarea}
            value={form.description}
            onChange={handleChange('description')}
            placeholder="Describe what this server does..."
            rows={3}
          />
        </label>

        <div className={styles.actions}>
          <Button type="button" variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" loading={isLoading}>
            {isEdit ? 'Update' : 'Register'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
