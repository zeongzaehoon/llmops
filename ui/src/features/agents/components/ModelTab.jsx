import { useState, useMemo } from 'react'
import toast from 'react-hot-toast'
import Button from '@/components/inputs/Button'
import EmptyState from '@/components/feedback/EmptyState'
import VendorSelector from '@/features/models/components/VendorSelector'
import ModelList from '@/features/models/components/ModelList'
import { useModels, useCurrentModel, useSetModel } from '@/hooks/queries/useModels'
import styles from '../AgentDetailPage.module.scss'

export default function ModelTab({ agent }) {
  const { data: allModels = [], isLoading: modelsLoading } = useModels()
  const { data: currentModel, isLoading: currentModelLoading } = useCurrentModel(agent)
  const setModelMutation = useSetModel()
  const [selectedVendor, setSelectedVendor] = useState(null)
  const [selectedModel, setSelectedModel] = useState(null)

  const vendors = useMemo(() => {
    const s = new Set()
    allModels.forEach((m) => {
      if (m.vendor) s.add(m.vendor)
    })
    return [...s]
  }, [allModels])

  const modelCounts = useMemo(() => {
    const c = {}
    allModels.forEach((m) => {
      if (m.vendor) c[m.vendor] = (c[m.vendor] || 0) + 1
    })
    return c
  }, [allModels])

  const filteredModels = useMemo(() => {
    if (!selectedVendor) return []
    return allModels.filter((m) => m.vendor === selectedVendor)
  }, [allModels, selectedVendor])

  const handleVendorSelect = (v) => {
    setSelectedVendor(v)
    setSelectedModel(null)
  }

  const handleModelSave = () => {
    if (!selectedVendor || !selectedModel) {
      toast.error('Please select a vendor and model')
      return
    }
    setModelMutation.mutate(
      { agent, company: selectedVendor, model: selectedModel },
      {
        onSuccess: () => toast.success('Model updated'),
        onError: () => toast.error('Failed to update model')
      }
    )
  }

  return (
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
  )
}
