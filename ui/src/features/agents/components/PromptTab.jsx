import { useState, useMemo, useCallback } from 'react'
import toast from 'react-hot-toast'
import Card from '@/components/layout/Card'
import EmptyState from '@/components/feedback/EmptyState'
import {
  useVersions,
  usePromptData,
  useDeployList,
  useSavePrompt,
  useDeploy,
  useRollback
} from '@/hooks/queries/usePrompts'
import VersionTimeline from '@/features/prompts/components/VersionTimeline'
import PromptEditor from '@/features/prompts/components/PromptEditor'
import DeployPanel from '@/features/prompts/components/DeployPanel'
import DeployModal from '@/features/prompts/components/DeployModal'
import DiffViewer from '@/features/prompts/components/DiffViewer'
import styles from '../AgentDetailPage.module.scss'

export default function PromptTab({ agent }) {
  const { data: deployList = [] } = useDeployList()
  const { data: versions = [], isLoading: versionsLoading } = useVersions(agent)
  const sortedVersions = useMemo(
    () => [...versions].sort((a, b) => new Date(b.date) - new Date(a.date)),
    [versions]
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
        onSuccess: () => {
          toast.success('Prompt saved as new version')
          setSelectedId(null)
        },
        onError: () => toast.error('Failed to save prompt')
      })
    },
    [saveMutation]
  )

  const handleShowDiff = useCallback(
    async (oldVer, newVer) => {
      try {
        const [oldRes, newRes] = await Promise.all([
          import('@/api/agents').then((m) =>
            m.getPromptData({ agent, kind: 'prompt', id: oldVer })
          ),
          import('@/api/agents').then((m) => m.getPromptData({ agent, kind: 'prompt', id: newVer }))
        ])
        setDiffTexts({
          old: oldRes.data?.data?.prompt || '',
          new: newRes.data?.data?.prompt || ''
        })
        setDiffState({ old: oldVer, new: newVer })
      } catch {
        toast.error('Failed to load versions for diff')
      }
    },
    [agent]
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
        onError: () => toast.error(`Failed to ${modalType}`)
      }
    )
  }

  const deployInfo = useMemo(
    () => deployList.find((d) => d.agent === agent) || {},
    [deployList, agent]
  )

  return (
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
  )
}
