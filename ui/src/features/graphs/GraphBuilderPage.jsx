import { useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import Button from '@/components/inputs/Button'
import Badge from '@/components/data-display/Badge'
import { useGraph, useCreateGraph, useUpdateGraph } from '@/hooks/queries/useGraphs'
import GraphTypeSelector from './components/GraphTypeSelector'
import GraphCanvas from './components/GraphCanvas'
import DebateSettings from './components/DebateSettings'
import GraphTestPanel from './components/GraphTestPanel'
import styles from './GraphBuilderPage.module.scss'

const EMPTY_AGENT = { agent: '', role: '' }

const TYPE_BADGE_MAP = {
  linear: 'info',
  debate: 'danger',
  parallel: 'staging',
  router: 'production',
}

function defaultAgentsForType(type) {
  switch (type) {
    case 'linear':
      return [{ ...EMPTY_AGENT }, { ...EMPTY_AGENT }]
    case 'debate':
      return [{ ...EMPTY_AGENT }, { ...EMPTY_AGENT }]
    case 'parallel':
      return [{ ...EMPTY_AGENT }, { ...EMPTY_AGENT }, { ...EMPTY_AGENT }]
    case 'router':
      return [{ ...EMPTY_AGENT }, { ...EMPTY_AGENT }]
    default:
      return [{ ...EMPTY_AGENT }]
  }
}

export default function GraphBuilderPage() {
  const { id: graphId } = useParams()
  const navigate = useNavigate()
  const isEditing = Boolean(graphId)

  const { data: existingGraph, isLoading: isLoadingGraph } = useGraph(
    isEditing ? { name: graphId } : null
  )
  const createGraph = useCreateGraph()
  const updateGraph = useUpdateGraph()

  // Form state — initialize from existing data or defaults
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [type, setType] = useState('linear')
  const [agents, setAgents] = useState(defaultAgentsForType('linear'))
  const [maxIterations, setMaxIterations] = useState(3)
  const [moderator, setModerator] = useState('')
  const [initialized, setInitialized] = useState(false)
  const [savedGraphId, setSavedGraphId] = useState(graphId || null)

  // Populate form from existing graph once loaded
  if (isEditing && existingGraph && !initialized) {
    setName(existingGraph.name || '')
    setDescription(existingGraph.description || '')
    setType(existingGraph.type || 'linear')
    setAgents(
      existingGraph.agents?.length > 0
        ? existingGraph.agents
        : defaultAgentsForType(existingGraph.type || 'linear')
    )
    setMaxIterations(existingGraph.max_iterations ?? 3)
    setModerator(existingGraph.moderator || '')
    setInitialized(true)
  }

  const handleTypeChange = useCallback((newType) => {
    setType(newType)
    setAgents(defaultAgentsForType(newType))
    setModerator('')
  }, [])

  const handleChangeAgent = useCallback((index, updated) => {
    setAgents((prev) => prev.map((a, i) => (i === index ? updated : a)))
  }, [])

  const handleRemoveAgent = useCallback((index) => {
    setAgents((prev) => prev.filter((_, i) => i !== index))
  }, [])

  const handleAddAgent = useCallback(() => {
    setAgents((prev) => [...prev, { ...EMPTY_AGENT }])
  }, [])

  const handleSave = async () => {
    if (!name.trim()) {
      toast.error('Graph name is required.')
      return
    }

    if (agents.every((a) => !a.agent)) {
      toast.error('At least one agent must be selected.')
      return
    }

    const payload = {
      name: name.trim(),
      description: description.trim(),
      type,
      agents: agents.filter((a) => a.agent),
      max_iterations: type === 'debate' ? maxIterations : undefined,
      moderator: type === 'debate' ? moderator : undefined,
    }

    try {
      if (isEditing) {
        await updateGraph.mutateAsync({ ...payload, graph_id: graphId })
        toast.success('Graph updated successfully.')
      } else {
        const res = await createGraph.mutateAsync(payload)
        const newId = res?.data?.data?.graph_id
        if (newId) setSavedGraphId(newId)
        toast.success('Graph created successfully.')
      }
    } catch {
      toast.error('Failed to save graph.')
    }
  }

  const handleCancel = () => {
    navigate('/admin/graphs')
  }

  const isSaving = createGraph.isPending || updateGraph.isPending

  if (isEditing && isLoadingGraph) {
    return (
      <div className={styles.page}>
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <span>Loading graph...</span>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      {/* Top bar */}
      <div className={styles.topBar}>
        <div className={styles.topLeft}>
          <button type="button" className={styles.backBtn} onClick={handleCancel}>
            &larr; Back
          </button>
          <h1 className={styles.pageTitle}>
            {isEditing ? 'Edit Multi-Agent Graph' : 'New Multi-Agent Graph'}
          </h1>
          {type && <Badge variant={TYPE_BADGE_MAP[type]}>{type}</Badge>}
        </div>
        <div className={styles.topActions}>
          <Button variant="secondary" size="md" onClick={handleCancel}>
            Cancel
          </Button>
          <Button variant="primary" size="md" loading={isSaving} onClick={handleSave}>
            {isEditing ? 'Update' : 'Save'}
          </Button>
        </div>
      </div>

      {/* Form fields */}
      <div className={styles.formSection}>
        <div className={styles.formRow}>
          <div className={styles.formField}>
            <label className={styles.label}>Name</label>
            <input
              type="text"
              className={styles.input}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Give your graph a name"
              maxLength={100}
            />
          </div>
          <div className={styles.formField}>
            <label className={styles.label}>Description</label>
            <input
              type="text"
              className={styles.input}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
              maxLength={300}
            />
          </div>
        </div>
      </div>

      {/* Type selector */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Graph Type</h2>
        <GraphTypeSelector value={type} onChange={handleTypeChange} />
      </div>

      {/* Debate settings (conditionally shown) */}
      {type === 'debate' && (
        <div className={styles.section}>
          <DebateSettings
            maxIterations={maxIterations}
            onMaxIterationsChange={setMaxIterations}
            moderator={moderator}
            onModeratorChange={setModerator}
            agents={agents}
          />
        </div>
      )}

      {/* Graph canvas */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>
          Graph Canvas
          <span className={styles.agentCount}>{agents.length} agent{agents.length !== 1 ? 's' : ''}</span>
        </h2>
        <GraphCanvas
          type={type}
          agents={agents}
          onChangeAgent={handleChangeAgent}
          onRemoveAgent={handleRemoveAgent}
          onAddAgent={handleAddAgent}
          moderator={moderator}
        />
      </div>

      {/* Test panel */}
      <div className={styles.section}>
        <GraphTestPanel
          graphId={savedGraphId}
          graphName={name}
          agents={agents}
        />
      </div>
    </div>
  )
}
