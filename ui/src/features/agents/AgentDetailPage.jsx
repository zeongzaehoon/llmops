import { useState, useMemo, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import PageHeader from '@/components/layout/PageHeader'
import Tabs from '@/components/navigation/Tabs'
import Card from '@/components/layout/Card'
import Badge from '@/components/data-display/Badge'
import Button from '@/components/inputs/Button'
import EmptyState from '@/components/feedback/EmptyState'

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
import { useToolsets, useDeleteToolset, useDeployToolset } from '@/hooks/queries/useToolsets'
import { useServers } from '@/hooks/queries/useServers'
import ToolsetCard from './components/ToolsetCard'
import ServerPanel from './components/ServerPanel'
import ServerFormModal from './components/ServerFormModal'

import styles from './AgentDetailPage.module.scss'

const TAB_KEYS = { MODEL: 'model', PROMPT: 'prompt', TOOLSET: 'toolset', SERVERS: 'servers' }

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
      { agent, vendor: selectedVendor, model: selectedModel },
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
    () => [...versions].sort((a, b) => (b.version ?? 0) - (a.version ?? 0)),
    [versions],
  )
  const latestVersion = sortedVersions[0]?.version ?? null
  const [selectedVersion, setSelectedVersion] = useState(null)
  const currentVersion = selectedVersion ?? latestVersion
  const { data: promptData } = usePromptData(agent, currentVersion)

  const saveMutation = useSavePrompt()
  const deployMutation = useDeploy()
  const rollbackMutation = useRollback()
  const [modalType, setModalType] = useState(null)
  const [diffState, setDiffState] = useState(null)
  const [diffTexts, setDiffTexts] = useState({ old: '', new: '' })

  const handlePromptSave = useCallback(
    (data) => {
      saveMutation.mutate(data, {
        onSuccess: () => { toast.success('Prompt saved as new version'); setSelectedVersion(null) },
        onError: () => toast.error('Failed to save prompt'),
      })
    },
    [saveMutation],
  )

  const handleShowDiff = useCallback(
    async (oldVer, newVer) => {
      try {
        const [oldRes, newRes] = await Promise.all([
          import('@/api/prompts').then((m) => m.getData({ agent, kind: 'prompt', id: oldVer })),
          import('@/api/prompts').then((m) => m.getData({ agent, kind: 'prompt', id: newVer })),
        ])
        setDiffTexts({
          old: oldRes.data?.res?.data?.prompt || '',
          new: newRes.data?.res?.data?.prompt || '',
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
  const { data: toolsets = [] } = useToolsets()
  const agentToolsets = useMemo(() => toolsets.filter((t) => t.agent === agent), [toolsets, agent])
  const deleteToolset = useDeleteToolset()
  const deployToolset = useDeployToolset()
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deployTarget, setDeployTarget] = useState(null)

  // ---- Server state ----
  const [serverModalOpen, setServerModalOpen] = useState(false)

  const tabItems = useMemo(() => [
    { key: TAB_KEYS.MODEL, label: 'Model' },
    { key: TAB_KEYS.PROMPT, label: 'Prompt' },
    { key: TAB_KEYS.TOOLSET, label: 'Toolset', count: agentToolsets.length },
    { key: TAB_KEYS.SERVERS, label: 'Servers' },
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
                    <span className={styles.vendorName}>{currentModel.vendor}</span>
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
                    activeVersion={currentVersion}
                    onSelectVersion={setSelectedVersion}
                    onShowDiff={handleShowDiff}
                  />
                )}
              </Card>

              <Card className={styles.editorPanel}>
                <PromptEditor
                  promptData={promptData}
                  agent={agent}
                  isLatest={currentVersion === latestVersion}
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
                    key={toolset.name}
                    toolset={toolset}
                    onDeploy={setDeployTarget}
                    onEdit={(t) => navigate(`/admin/agents/${encodeURIComponent(agent)}/toolset/${encodeURIComponent(t.name)}`)}
                    onDelete={setDeleteTarget}
                  />
                ))}
              </div>
            )}

            {deployTarget && (
              <ConfirmAction
                title="Deploy Toolset"
                description={`Deploy "${deployTarget.name}" to production?`}
                onConfirm={() => {
                  deployToolset.mutate(
                    { name: deployTarget.name, agent: deployTarget.agent },
                    {
                      onSuccess: () => { toast.success('Toolset deployed'); setDeployTarget(null) },
                      onError: () => toast.error('Failed to deploy'),
                    },
                  )
                }}
                onCancel={() => setDeployTarget(null)}
              />
            )}

            {deleteTarget && (
              <ConfirmAction
                title="Delete Toolset"
                description={`Delete "${deleteTarget.name}"? This cannot be undone.`}
                variant="danger"
                onConfirm={() => {
                  deleteToolset.mutate(
                    { name: deleteTarget.name, agent: deleteTarget.agent },
                    {
                      onSuccess: () => { toast.success('Toolset deleted'); setDeleteTarget(null) },
                      onError: () => toast.error('Failed to delete'),
                    },
                  )
                }}
                onCancel={() => setDeleteTarget(null)}
              />
            )}
          </div>
        )}

        {/* ===== SERVERS TAB ===== */}
        {activeTab === TAB_KEYS.SERVERS && (
          <div className={styles.serversTab}>
            <div className={styles.toolsetHeader}>
              <Button size="sm" onClick={() => setServerModalOpen(true)}>
                + Register Server
              </Button>
            </div>
            <ServerPanel onRegister={() => setServerModalOpen(true)} />
            <ServerFormModal
              open={serverModalOpen}
              onClose={() => setServerModalOpen(false)}
            />
          </div>
        )}
      </div>
    </div>
  )
}

// Inline confirm dialog to avoid importing ConfirmDialog with complex logic
function ConfirmAction({ title, description, variant = 'primary', onConfirm, onCancel }) {
  return (
    <div className={styles.confirmOverlay} onClick={onCancel}>
      <div className={styles.confirmBox} onClick={(e) => e.stopPropagation()}>
        <h4 className={styles.confirmTitle}>{title}</h4>
        <p className={styles.confirmDesc}>{description}</p>
        <div className={styles.confirmActions}>
          <Button variant="secondary" size="sm" onClick={onCancel}>Cancel</Button>
          <Button variant={variant} size="sm" onClick={onConfirm}>Confirm</Button>
        </div>
      </div>
    </div>
  )
}
