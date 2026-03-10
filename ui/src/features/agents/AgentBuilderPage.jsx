import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import PageHeader from '@/components/layout/PageHeader'
import Card from '@/components/layout/Card'
import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import { useServers } from '@/hooks/queries/useServers'
import { useToolset, useCreateToolset, useUpdateToolset } from '@/hooks/queries/useToolsets'
import styles from './AgentBuilderPage.module.scss'

export default function AgentBuilderPage() {
  const navigate = useNavigate()
  const { agent, id } = useParams()
  const isEdit = !!id && id !== 'new'
  const backPath = `/admin/agents/${encodeURIComponent(agent)}`

  const { data: servers = [] } = useServers()
  const { data: existingToolset } = useToolset(isEdit ? { name: decodeURIComponent(id) } : null)
  const createToolset = useCreateToolset()
  const updateToolset = useUpdateToolset()

  const [form, setForm] = useState({
    name: '',
    description: '',
  })
  const [selectedTools, setSelectedTools] = useState({})
  const [expandedServers, setExpandedServers] = useState({})

  useEffect(() => {
    if (existingToolset && isEdit) {
      setForm({
        name: existingToolset.name || '',
        description: existingToolset.description || '',
      })
      const toolMap = {}
      existingToolset.mcp_servers?.forEach((srv) => {
        toolMap[srv.name] = new Set(srv.tools || [])
      })
      setSelectedTools(toolMap)

      const expanded = {}
      existingToolset.mcp_servers?.forEach((srv) => {
        expanded[srv.name] = true
      })
      setExpandedServers(expanded)
    }
  }, [existingToolset, isEdit])

  const toggleServer = (serverName) => {
    setExpandedServers((prev) => ({ ...prev, [serverName]: !prev[serverName] }))
  }

  const toggleTool = (serverName, toolName) => {
    setSelectedTools((prev) => {
      const next = { ...prev }
      if (!next[serverName]) {
        next[serverName] = new Set()
      } else {
        next[serverName] = new Set(next[serverName])
      }
      if (next[serverName].has(toolName)) {
        next[serverName].delete(toolName)
        if (next[serverName].size === 0) delete next[serverName]
      } else {
        next[serverName].add(toolName)
      }
      return next
    })
  }

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  const mcpServersPayload = useMemo(() => {
    return Object.entries(selectedTools)
      .filter(([, tools]) => tools.size > 0)
      .map(([name, tools]) => ({ name, tools: Array.from(tools) }))
  }, [selectedTools])

  const totalTools = mcpServersPayload.reduce((sum, s) => sum + s.tools.length, 0)

  const handleSave = () => {
    if (!form.name.trim()) {
      toast.error('Name is required')
      return
    }
    if (mcpServersPayload.length === 0) {
      toast.error('Select at least one tool')
      return
    }

    const payload = {
      name: form.name.trim(),
      description: form.description.trim(),
      agent,
      mcp_servers: mcpServersPayload,
    }

    const mutation = isEdit ? updateToolset : createToolset
    mutation.mutate(payload, {
      onSuccess: () => {
        toast.success(isEdit ? 'Toolset updated' : 'Toolset created')
        navigate(backPath)
      },
      onError: () => toast.error(isEdit ? 'Failed to update' : 'Failed to create'),
    })
  }

  const isLoading = createToolset.isPending || updateToolset.isPending

  return (
    <div className={styles.page}>
      <PageHeader
        title={isEdit ? 'Edit Toolset' : 'New Toolset'}
        description={`Configure MCP tools for agent: ${agent}`}
        actions={
          <Button variant="secondary" size="sm" onClick={() => navigate(backPath)}>
            Back
          </Button>
        }
      />

      <div className={styles.columns}>
        {/* Left: Server & Tool picker */}
        <div className={styles.left}>
          <h3 className={styles.sectionTitle}>Servers & Tools</h3>
          <div className={styles.serverList}>
            {servers.length === 0 && (
              <p className={styles.emptyHint}>No servers available. Register a server first.</p>
            )}
            {servers.map((server) => {
              const isExpanded = expandedServers[server.name]
              const tools = server.tools || []
              const selected = selectedTools[server.name] || new Set()

              return (
                <div key={server.name} className={styles.serverGroup}>
                  <button
                    className={styles.serverToggle}
                    onClick={() => toggleServer(server.name)}
                  >
                    <span className={styles.chevron}>{isExpanded ? '\u25BE' : '\u25B8'}</span>
                    <span className={styles.serverLabel}>{server.name}</span>
                    {selected.size > 0 && (
                      <Badge variant="count">{selected.size}</Badge>
                    )}
                  </button>
                  {isExpanded && (
                    <div className={styles.toolList}>
                      {tools.length === 0 && (
                        <span className={styles.noTools}>No tools available</span>
                      )}
                      {tools.map((tool) => {
                        const toolName = typeof tool === 'string' ? tool : tool.name
                        const isChecked = selected.has(toolName)
                        return (
                          <label key={toolName} className={styles.toolItem}>
                            <input
                              type="checkbox"
                              checked={isChecked}
                              onChange={() => toggleTool(server.name, toolName)}
                            />
                            <span className={styles.toolName}>{toolName}</span>
                          </label>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Center: Toolset config */}
        <div className={styles.center}>
          <h3 className={styles.sectionTitle}>Toolset Configuration</h3>

          <label className={styles.field}>
            <span className={styles.label}>Name</span>
            <input
              type="text"
              className={styles.input}
              value={form.name}
              onChange={handleChange('name')}
              placeholder="analyzer-v2"
              disabled={isEdit}
            />
          </label>

          <label className={styles.field}>
            <span className={styles.label}>Description</span>
            <textarea
              className={styles.textarea}
              value={form.description}
              onChange={handleChange('description')}
              placeholder="Describe what this toolset does..."
              rows={4}
            />
          </label>

          <div className={styles.selectedSummary}>
            <h4 className={styles.summaryTitle}>
              Selected Tools <Badge variant="count">{totalTools}</Badge>
            </h4>
            {mcpServersPayload.length === 0 ? (
              <p className={styles.emptyHint}>No tools selected yet</p>
            ) : (
              mcpServersPayload.map((srv) => (
                <div key={srv.name} className={styles.summaryServer}>
                  <span className={styles.summaryServerName}>{srv.name}</span>
                  <div className={styles.summaryTools}>
                    {srv.tools.map((t) => (
                      <span key={t} className={styles.summaryTag}>{t}</span>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className={styles.formActions}>
            <Button variant="secondary" onClick={() => navigate(backPath)} disabled={isLoading}>
              Cancel
            </Button>
            <Button onClick={handleSave} loading={isLoading}>
              {isEdit ? 'Update Toolset' : 'Create Toolset'}
            </Button>
          </div>
        </div>

        {/* Right: Preview */}
        <div className={styles.right}>
          <h3 className={styles.sectionTitle}>Preview</h3>
          <Card className={styles.previewCard}>
            <div className={styles.previewHeader}>
              <span className={styles.previewName}>{form.name || 'Toolset Name'}</span>
              <Badge variant="draft">Draft</Badge>
            </div>
            <Badge variant="info">{agent}</Badge>
            {form.description && (
              <p className={styles.previewDesc}>{form.description}</p>
            )}
            {mcpServersPayload.length > 0 && (
              <div className={styles.previewServers}>
                <span className={styles.previewLabel}>Servers & Tools:</span>
                {mcpServersPayload.map((srv) => (
                  <div key={srv.name} className={styles.previewServerItem}>
                    <span className={styles.previewServerName}>{srv.name}:</span>
                    <div className={styles.previewTools}>
                      {srv.tools.map((t) => (
                        <span key={t} className={styles.previewToolTag}>{t}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
