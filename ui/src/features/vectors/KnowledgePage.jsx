import { useState } from 'react'
import toast from 'react-hot-toast'
import PageHeader from '@/components/layout/PageHeader'
import Button from '@/components/inputs/Button'
import { useVectorSearch, useVectorUpsert, useVectorDeleteById } from '@/hooks/queries/useVectors'
import SearchPanel from './components/SearchPanel'
import ResultList from './components/ResultList'
import UpsertModal from './components/UpsertModal'
import styles from './KnowledgePage.module.scss'

export default function KnowledgePage() {
  const [upsertOpen, setUpsertOpen] = useState(false)
  const [results, setResults] = useState([])
  const [lastAgent, setLastAgent] = useState('main')

  const searchMutation = useVectorSearch()
  const upsertMutation = useVectorUpsert()
  const deleteMutation = useVectorDeleteById()

  const handleSearch = (params) => {
    setLastAgent(params.agent)
    searchMutation.mutate(params, {
      onSuccess: (res) => {
        const data = res.data?.res?.data || []
        setResults(data)
        if (data.length === 0) {
          toast('No matching vectors found')
        }
      },
      onError: () => {
        toast.error('Search failed')
      },
    })
  }

  const handleUpsert = (data) => {
    upsertMutation.mutate(data, {
      onSuccess: () => {
        toast.success('Vectors upserted successfully')
        setUpsertOpen(false)
      },
      onError: () => {
        toast.error('Upsert failed')
      },
    })
  }

  const handleDelete = (id) => {
    deleteMutation.mutate(
      { ids: [id], agent: lastAgent },
      {
        onSuccess: () => {
          setResults((prev) => prev.filter((r) => (r.id || r._id) !== id))
          toast.success('Vector deleted')
        },
        onError: () => {
          toast.error('Delete failed')
        },
      },
    )
  }

  return (
    <div className={styles.page}>
      <PageHeader
        title="Knowledge Base"
        description="Vector DB data management and semantic search"
        actions={
          <Button size="sm" onClick={() => setUpsertOpen(true)}>
            + Upsert
          </Button>
        }
      />

      <SearchPanel onSearch={handleSearch} isLoading={searchMutation.isPending} />

      <div className={styles.results}>
        {searchMutation.isPending ? (
          <div className={styles.loading}>Searching vectors...</div>
        ) : (
          <ResultList
            results={results}
            onDelete={handleDelete}
            isDeleting={deleteMutation.isPending}
          />
        )}
      </div>

      <UpsertModal
        open={upsertOpen}
        onClose={() => setUpsertOpen(false)}
        onUpsert={handleUpsert}
        isLoading={upsertMutation.isPending}
      />
    </div>
  )
}
