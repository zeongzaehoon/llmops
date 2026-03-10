import { Suspense } from 'react'
import { useParams } from 'react-router-dom'
import HistoryContainer from '@/components/playground/history/HistoryContainer'
import BaseLoading from '@/components/playground/common/BaseLoading'
import styles from './HistoryWrapper.module.scss'

export default function HistoryWrapper() {
  const { agent } = useParams()

  return (
    <div className={styles['history-wrapper']}>
      <Suspense fallback={<BaseLoading />}>
        <HistoryContainer agent={agent} />
      </Suspense>
    </div>
  )
}
