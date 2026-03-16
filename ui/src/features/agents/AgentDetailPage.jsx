import { useState, useMemo, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import PageHeader from '@/components/layout/PageHeader'
import Tabs from '@/components/navigation/Tabs'
import Card from '@/components/layout/Card'
import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import EmptyState from '@/components/feedback/EmptyState'
import ConfirmDialog from '@/components/feedback/ConfirmDialog'

// Model components
import VendorSelector from '@/features/models/components/VendorSelector'
import ModelList from '@/features/models/components/ModelList'
import { useModels, useCurrentModel, useSetModel } from '@/hooks/queries/useModels'

// Prompt components
import {
  useVersions,
  usePromptData,
  useDeployList,
  useSavePrompt,
  useDeploy,
  useRollback,
} from '@/hooks/queries/usePrompts'
import VersionTimeline from '@/features/prompts/components/VersionTimeline'
import PromptEditor from '@/features/prompts/components/PromptEditor'
import DeployPanel from '@/features/prompts/components/DeployPanel'
import DeployModal from '@/features/prompts/components/DeployModal'
import DiffViewer from '@/features/prompts/components/DiffViewer'

// Toolset components
import { useToolsetsByAgent, useDeleteToolset, useDeployToolset } from '@/hooks/queries/useToolsets'
import ToolsetCard from './components/ToolsetCard'

import styles from './AgentDetailPage.module.scss'

const TAB_KEYS = { MODEL: 'model', PROMPT: 'prompt', TOOLSET: 'toolset' }

export default function AgentDetailPage() {
  const { agent } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(TAB_KEYS.MODEL)

  // ---- Model state ----
  const { data: allModels = [], isLoading: modelsLoading } = useModels()
  const { data: currentModel, isLoading: currentModelLoading } = useCurrentModel(agent)
  const setModelMutation = useSetModel()
  const [selectedVendor, setSelectedVendor] = useState(null)
  const [selectedModel, setSelectedModel] = useState(null)

  const vendors = useMemo(() => {
    const s = new Set()
    allModels.forEach((m) => { if (m.vendor) s.add(m.vendor) })
    return [...s]
  }, [allModels])

  const modelCounts = useMemo(() => {
    const c = {}
    allModels.forEach((m) => { if (m.vendor) c[m.vendor] = (c[m.vendor] || 0) + 1 })
    return c
  }, [allModels])

  const filteredModels = useMemo(() => {
    if (!selectedVendor) return []
    return allModels.filter((m) => m.vendor === selectedVendor)
  }, [allModels, selectedVendor])

  const handleVendorSelect = (v) => { setSelectedVendor(v); setSelectedModel(null) }

  const handleModelSave = () => {
    if (!selectedVendor || !selectedModel) {
      toast.error('Please select a vendor and model')
      return
    }
    setModelMutation.mutate(
      { agent, company: selectedVendor, model: selectedModel },
      {
        onSuccess: () => toast.success('Model updated'),
        onError: () => toast.error('Failed to update model'),
      },
    )
  }

  // ---- Prompt state ----
  const { data: deployList = [] } = useDeployList()
  const { data: versions = [], isLoading: versionsLoading } = useVersions(agent)
  const sortedVersions = useMemo(
    () => [...versions].sort((a, b) => new Date(b.date) - new Date(a.date)),
    [versions],
  )
  const latestId = sortedVersions[0]?.id ?? null
  const [selectedId, setSelectedId] = useState(null)
  const currentId = selectedId ?? latestId
  const { data: promptData } = usePromptData(agent, currentId)

  const saveMutation = useSavePrompt()
  const deployMutation = useDeploy()
  const rollbackMutation = useRollback()
  const [modalType, setModalType] = useState(null)
  const [diffState, setDiffState] = useState(null)
  const [diffTexts, setDiffTexts] = useState({ old: '', new: '' })

  const handlePromptSave = useCallback(
    (data) => {
      saveMutation.mutate(data, {
        onSuccess: () => { toast.success('Prompt saved as new version'); setSelectedId(null) },
        onError: () => toast.error('Failed to save prompt'),
      })
    },
    [saveMutation],
  )

  const handleShowDiff = useCallback(
    async (oldVer, newVer) => {
      try {
        const [oldRes, newRes] = await Promise.all([
          import('@/api/agents').then((m) => m.getPromptData({ agent, kind: 'prompt', id: oldVer })),
          import('@/api/agents').then((m) => m.getPromptData({ agent, kind: 'prompt', id: newVer })),
        ])
        setDiffTexts({
          old: oldRes.data?.data?.prompt || '',
          new: newRes.data?.data?.prompt || '',
        })
        setDiffState({ old: oldVer, new: newVer })
      } catch {
        toast.error('Failed to load versions for diff')
      }
    },
    [agent],
  )

  const handleDeployConfirm = (password, onAnimationDone) => {
    const mutation = modalType === 'deploy' ? deployMutation : rollbackMutation
    mutation.mutate(
      { agent, password },
      {
        onSuccess: () => {
          toast.success(modalType === 'deploy' ? 'Deployed successfully' : 'Rollback completed')
          onAnimationDone?.()
          setTimeout(() => setModalType(null), 700)
        },
        onError: () => toast.error(`Failed to ${modalType}`),
      },
    )
  }

  const deployInfo = useMemo(() => deployList.find((d) => d.agent === agent) || {}, [deployList, agent])

  // ---- Toolset state ----
  const { data: agentToolsets = [] } = useToolsetsByAgent(agent)
  const deleteToolset = useDeleteToolset()
  const deployToolsetMutation = useDeployToolset()
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deployTarget, setDeployTarget] = useState(null)

  const liveToolset = useMemo(() => agentToolsets.find((t) => t.isService), [agentToolsets])

  const handleDeployToolset = () => {
    if (!deployTarget) return
    deployToolsetMutation.mutate(
      { id: deployTarget.id, agent: deployTarget.agent },
      {
        onSuccess: () => { toast.success('Toolset deployed'); setDeployTarget(null) },
        onError: () => toast.error('Failed to deploy'),
      },
    )
  }

  const handleDeleteToolset = () => {
    if (!deleteTarget) return
    deleteToolset.mutate(
      { id: deleteTarget.id },
      {
        onSuccess: () => { toast.success('Toolset deleted'); setDeleteTarget(null) },
        onError: () => toast.error('Failed to delete'),
      },
    )
  }

  const tabItems = useMemo(() => [
    { key: TAB_KEYS.MODEL, label: 'Model' },
    { key: TAB_KEYS.PROMPT, label: 'Prompt' },
    { key: TAB_KEYS.TOOLSET, label: 'Toolset', count: agentToolsets.length },
  ], [agentToolsets.length])

  return (
    <div className={styles.page}>
      <PageHeader
        title={agent}
        description="Model, prompt, and toolset configuration"
        actions={
          <Button variant="secondary" size="sm" onClick={() => navigate('/admin/agents')}>
            Back
          </Button>
        }
      />

      <div className={styles.tabBar}>
        <Tabs items={tabItems} activeKey={activeTab} onChange={setActiveTab} />
      </div>

      <div className={styles.content}>
        {/* ===== MODEL TAB ===== */}
        {activeTab === TAB_KEYS.MODEL && (
          <div className={styles.modelTab}>
            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Current Model</h3>
              <div className={styles.currentModel}>
                {currentModelLoading ? (
                  <span className={styles.muted}>Loading...</span>
                ) : currentModel ? (
                  <>
                    <span className={styles.vendorName}>{currentModel.company}</span>
                    <span className={styles.separator}>/</span>
                    <span className={styles.modelName}>{currentModel.model}</span>
                  </>
                ) : (
                  <span className={styles.muted}>No model configured</span>
                )}
              </div>
            </section>

            {modelsLoading ? (
              <div className={styles.loading}>Loading models...</div>
            ) : vendors.length === 0 ? (
              <EmptyState title="No models available" description="No LLM models have been registered" />
            ) : (
              <>
                <section className={styles.section}>
                  <h3 className={styles.sectionTitle}>Vendor</h3>
                  <VendorSelector
                    vendors={vendors}
                    selected={selectedVendor}
                    onSelect={handleVendorSelect}
                    modelCounts={modelCounts}
                  />
                </section>

                {selectedVendor && (
                  <section className={styles.section}>
                    <h3 className={styles.sectionTitle}>Model</h3>
                    <ModelList
                      models={filteredModels}
                      selected={selectedModel}
                      onSelect={setSelectedModel}
                    />
                  </section>
                )}

                <div className={styles.footer}>
                  <Button
                    onClick={handleModelSave}
                    loading={setModelMutation.isPending}
                    disabled={!selectedVendor || !selectedModel}
                  >
                    Save Model
                  </Button>
                </div>
              </>
            )}
          </div>
        )}

        {/* ===== PROMPT TAB ===== */}
        {activeTab === TAB_KEYS.PROMPT && (
          <div className={styles.promptTab}>
            <div className={styles.panels}>
              <Card className={styles.timelinePanel}>
                {versionsLoading ? (
                  <div className={styles.loading}>Loading versions...</div>
                ) : sortedVersions.length === 0 ? (
                  <EmptyState
                    title="No versions"
                    description="Save a prompt to create the first version"
                  />
                ) : (
                  <VersionTimeline
                    versions={sortedVersions}
                    activeVersion={currentId}
                    onSelectVersion={setSelectedId}
                    onShowDiff={handleShowDiff}
                  />
                )}
              </Card>

              <Card className={styles.editorPanel}>
                <PromptEditor
                  promptData={promptData}
                  agent={agent}
                  isLatest={currentId === latestId}
                  onSave={handlePromptSave}
                  isSaving={saveMutation.isPending}
                />
              </Card>
            </div>

            <Card className={styles.deployCard}>
              <DeployPanel
                deployInfo={deployInfo}
                onDeploy={() => setModalType('deploy')}
                onRollback={() => setModalType('rollback')}
              />
            </Card>

            <DeployModal
              open={!!modalType}
              onClose={() => setModalType(null)}
              onConfirm={handleDeployConfirm}
              type={modalType || 'deploy'}
              loading={deployMutation.isPending || rollbackMutation.isPending}
            />

            {diffState && (
              <DiffViewer
                open={!!diffState}
                onClose={() => setDiffState(null)}
                oldVersion={diffState.old}
                newVersion={diffState.new}
                oldText={diffTexts.old}
                newText={diffTexts.new}
              />
            )}
          </div>
        )}

        {/* ===== TOOLSET TAB ===== */}
        {activeTab === TAB_KEYS.TOOLSET && (
          <div className={styles.toolsetTab}>
            <div className={styles.toolsetHeader}>
              <Button size="sm" onClick={() => navigate(`/admin/agents/${encodeURIComponent(agent)}/toolset/new`)}>
                + New Toolset
              </Button>
            </div>

            {/* Live toolset summary */}
            {liveToolset && (
              <Card className={styles.liveToolsetCard}>
                <div className={styles.liveToolsetHeader}>
                  <Badge variant="live">LIVE</Badge>
                  <span className={styles.liveToolsetName}>{liveToolset.name}</span>
                </div>
                {liveToolset.mcpInfo?.length > 0 && (
                  <div className={styles.liveToolsetMeta}>
                    {liveToolset.mcpInfo.map((info, idx) => (
                      <span key={idx} className={styles.liveToolsetServer}>
                        {info.serverName || info.serverId}: {info.tools?.length || 0} tools
                      </span>
                    ))}
                  </div>
                )}
              </Card>
            )}

            {agentToolsets.length === 0 ? (
              <EmptyState
                title="No toolsets"
                description="Create a toolset to connect MCP tools to this agent"
                action={{
                  label: '+ New Toolset',
                  onClick: () => navigate(`/admin/agents/${encodeURIComponent(agent)}/toolset/new`),
                }}
              />
            ) : (
              <div className={styles.toolsetGrid}>
                {agentToolsets.map((toolset) => (
                  <ToolsetCard
                    key={toolset.id}
                    toolset={toolset}
                    onDeploy={setDeployTarget}
                    onEdit={(t) => navigate(`/admin/agents/${encodeURIComponent(agent)}/toolset/${encodeURIComponent(t.id)}`)}
                    onDelete={setDeleteTarget}
                  />
                ))}
              </div>
            )}

            <ConfirmDialog
              open={!!deployTarget}
              title="Deploy Toolset"
              description={
                liveToolset
                  ? `Replace live toolset "${liveToolset.name}" with "${deployTarget?.name}"?`
                  : `Deploy "${deployTarget?.name}" to production?`
              }
              confirmLabel="Deploy"
              variant="primary"
              onConfirm={handleDeployToolset}
              onCancel={() => setDeployTarget(null)}
            />

            <ConfirmDialog
              open={!!deleteTarget}
              title="Delete Toolset"
              description={`Delete "${deleteTarget?.name}"? This cannot be undone.`}
              confirmLabel="Delete"
              variant="danger"
              onConfirm={handleDeleteToolset}
              onCancel={() => setDeleteTarget(null)}
            />
          </div>
        )}
      </div>
    </div>
  )
}
