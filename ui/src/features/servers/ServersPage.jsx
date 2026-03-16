import { useState } from 'react'
import PageHeader from '@/components/layout/PageHeader'
import Button from '@/components/inputs/Button'
import ServerPanel from '@/features/agents/components/ServerPanel'
import ServerFormModal from '@/features/agents/components/ServerFormModal'

export default function ServersPage() {
  const [modalOpen, setModalOpen] = useState(false)

  return (
    <div>
      <PageHeader
        title="MCP Servers"
        description="Register and manage MCP servers shared across all agents"
        actions={
          <Button size="sm" onClick={() => setModalOpen(true)}>
            + Register Server
          </Button>
        }
      />

      <ServerPanel onRegister={() => setModalOpen(true)} />

      <ServerFormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  )
}
