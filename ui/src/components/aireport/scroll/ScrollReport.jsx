import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function ScrollReport() {
  const { id } = useParams()
  const { t } = useTranslation()

  return (
    <div className="scroll-report">
      <h2>Scroll Report</h2>
      <p>Report ID: {id}</p>
      {/* Scroll report content will be implemented here */}
    </div>
  )
}
