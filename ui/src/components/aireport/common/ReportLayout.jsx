import { useParams, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useMemo } from 'react'
import { REPORT_META } from '@/utils/constants'

export default function ReportLayout() {
  const { id } = useParams()
  const location = useLocation()
  const { t } = useTranslation()

  const reportType = useMemo(() => {
    const path = location.pathname.split('/')[1]
    return path
  }, [location.pathname])

  const meta = REPORT_META[reportType] || {}

  return (
    <div className="report-layout">
      <h2>{meta.logoText || 'AI Report'}</h2>
      <p>Report ID: {id}</p>
      {/* Report content will be implemented here */}
    </div>
  )
}
