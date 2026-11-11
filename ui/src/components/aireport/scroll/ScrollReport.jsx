import { useParams } from 'react-router-dom'

export default function ScrollReport() {
  const { id } = useParams()

  return (
    <div className="scroll-report">
      <h2>Scroll Report</h2>
      <p>Report ID: {id}</p>
      {/* Scroll report content will be implemented here */}
    </div>
  )
}
