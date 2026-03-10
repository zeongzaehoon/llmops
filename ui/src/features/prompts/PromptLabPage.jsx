import { useState, useMemo, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import PageHeader from '@/components/layout/PageHeader'
import Card from '@/components/layout/Card'
import EmptyState from '@/components/feedback/EmptyState'
import {
  useVersions,
  usePromptData,
  useDeployList,
  useSavePrompt,
  useDeploy,
  useRollback,
} from '@/hooks/queries/usePrompts'
import CategorySelector from './components/CategorySelector'
import VersionTimeline from './components/VersionTimeline'
import PromptEditor from './components/PromptEditor'
import DeployPanel from './components/DeployPanel'
import DeployModal from './components/DeployModal'
import DiffViewer from './components/DiffViewer'
import styles from './PromptLabPage.module.scss'

export default function PromptLabPage() {
  const { agent: paramAgent } = useParams()
  const navigate = useNavigate()

  const { data: deployList = [] } = useDeployList()

  const categories = useMemo(() => {
    const cats = deployList.map((d) => d.agent).filter(Boolean)
    return [...new Set(cats)]
  }, [deployList])

  const activeCategory = paramAgent || categories[0] || ''

  const { data: versions = [], isLoading: versionsLoading } = useVersions(activeCategory)
  const sortedVersions = useMemo(
    () => [...versions].sort((a, b) => (b.version ?? 0) - (a.version ?? 0)),
    [versions]
  )
  const latestVersion = sortedVersions[0]?.version ?? null

  const [selectedVersion, setSelectedVersion] = useState(null)
  const currentVersion = selectedVersion ?? latestVersion

  const { data: promptData } = usePromptData(activeCategory, currentVersion)

  const saveMutation = useSavePrompt()
  const deployMutation = useDeploy()
  const rollbackMutation = useRollback()

  const [modalType, setModalType] = useState(null)
  const [diffState, setDiffState] = useState(null)
  const [diffTexts, setDiffTexts] = useState({ old: '', new: '' })

  const handleCategorySelect = (cat) => {
    setSelectedVersion(null)
    navigate(`/admin/prompts/${encodeURIComponent(cat)}`)
  }

  const handleVersionSelect = (ver) => {
    setSelectedVersion(ver)
  }

  const handleSave = useCallback(
    (data) => {
      saveMutation.mutate(data, {
        onSuccess: () => {
          toast.success('Prompt saved as new version')
          setSelectedVersion(null)
        },
        onError: () => toast.error('Failed to save prompt'),
      })
    },
    [saveMutation]
  )

  const handleShowDiff = useCallback(
    async (oldVer, newVer) => {
      try {
        const [oldRes, newRes] = await Promise.all([
          import('@/api/prompts').then((m) =>
            m.getData({ agent: activeCategory, kind: 'prompt', id: oldVer })
          ),
          import('@/api/prompts').then((m) =>
            m.getData({ agent: activeCategory, kind: 'prompt', id: newVer })
          ),
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
    [activeCategory]
  )

  const handleDeployConfirm = (password, onAnimationDone) => {
    const mutation = modalType === 'deploy' ? deployMutation : rollbackMutation
    const action = modalType === 'deploy' ? 'deploy' : 'rollback'

    mutation.mutate(
      { agent: activeCategory, password },
      {
        onSuccess: () => {
          toast.success(
            action === 'deploy'
              ? 'Deployed to production successfully'
              : 'Rollback completed successfully'
          )
          onAnimationDone?.()
          setTimeout(() => setModalType(null), 700)
        },
        onError: () => {
          toast.error(`Failed to ${action}`)
        },
      }
    )
  }

  const deployInfo = useMemo(() => {
    const entry = deployList.find((d) => d.agent === activeCategory)
    return entry || {}
  }, [deployList, activeCategory])

  return (
    <div className={styles.page}>
      <PageHeader
        title="Prompt Lab"
        description="Prompt version management and Blue-Green deployment"
      />

      {categories.length > 0 && (
        <CategorySelector
          categories={categories}
          active={activeCategory}
          onSelect={handleCategorySelect}
        />
      )}

      {!activeCategory ? (
        <EmptyState
          title="No agent selected"
          description="Select an agent above or configure deploy targets first"
        />
      ) : (
        <>
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
                  onSelectVersion={handleVersionSelect}
                  onShowDiff={handleShowDiff}
                />
              )}
            </Card>

            <Card className={styles.editorPanel}>
              <PromptEditor
                promptData={promptData}
                agent={activeCategory}
                isLatest={currentVersion === latestVersion}
                onSave={handleSave}
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
        </>
      )}

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
  )
}
