import { useState, useMemo } from 'react'
import toast from 'react-hot-toast'
import PageHeader from '@/components/layout/PageHeader'
import Button from '@/components/inputs/Button'
import EmptyState from '@/components/feedback/EmptyState'
import CategorySelector from '@/features/prompts/components/CategorySelector'
import { useModels, useCurrentModel, useSetModel } from '@/hooks/queries/useModels'
import VendorSelector from './components/VendorSelector'
import ModelList from './components/ModelList'
import styles from './ModelSettingsPage.module.scss'

const DEFAULT_CATEGORIES = ['main', 'cs', 'journeymapMCP', 'ranking', 'trend', 'weekly']

export default function ModelSettingsPage() {
  const [agent, setAgent] = useState('main')
  const [selectedVendor, setSelectedVendor] = useState(null)
  const [selectedModel, setSelectedModel] = useState(null)

  const { data: allModels = [], isLoading: modelsLoading } = useModels()
  const { data: currentModel, isLoading: currentLoading } = useCurrentModel(agent)
  const setModelMutation = useSetModel()

  const vendors = useMemo(() => {
    const vendorSet = new Set()
    allModels.forEach((m) => {
      if (m.vendor) vendorSet.add(m.vendor)
    })
    return [...vendorSet]
  }, [allModels])

  const modelCounts = useMemo(() => {
    const counts = {}
    allModels.forEach((m) => {
      if (m.vendor) {
        counts[m.vendor] = (counts[m.vendor] || 0) + 1
      }
    })
    return counts
  }, [allModels])

  const filteredModels = useMemo(() => {
    if (!selectedVendor) return []
    return allModels.filter((m) => m.vendor === selectedVendor)
  }, [allModels, selectedVendor])

  const handleVendorSelect = (vendor) => {
    setSelectedVendor(vendor)
    setSelectedModel(null)
  }

  const handleSave = () => {
    if (!selectedVendor || !selectedModel) {
      toast.error('Please select a vendor and model')
      return
    }

    setModelMutation.mutate(
      { agent, vendor: selectedVendor, model: selectedModel },
      {
        onSuccess: () => {
          toast.success(`Model updated for ${agent}`)
        },
        onError: () => {
          toast.error('Failed to update model')
        },
      },
    )
  }

  return (
    <div className={styles.page}>
      <PageHeader
        title="Model Settings"
        description="Configure LLM vendor and model per agent"
      />

      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Agent</h3>
        <CategorySelector
          categories={DEFAULT_CATEGORIES}
          active={agent}
          onSelect={setAgent}
        />
      </section>

      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Current Model</h3>
        <div className={styles.currentModel}>
          {currentLoading ? (
            <span className={styles.loadingText}>Loading...</span>
          ) : currentModel ? (
            <>
              <span className={styles.currentVendor}>{currentModel.vendor}</span>
              <span className={styles.currentSep}>/</span>
              <span className={styles.currentName}>{currentModel.model}</span>
            </>
          ) : (
            <span className={styles.noModel}>No model configured</span>
          )}
        </div>
      </section>

      {modelsLoading ? (
        <div className={styles.loading}>Loading models...</div>
      ) : vendors.length === 0 ? (
        <EmptyState
          title="No models available"
          description="No LLM models have been registered"
        />
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
              onClick={handleSave}
              loading={setModelMutation.isPending}
              disabled={!selectedVendor || !selectedModel}
            >
              Save Selection
            </Button>
          </div>
        </>
      )}
    </div>
  )
}
