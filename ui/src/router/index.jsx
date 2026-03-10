import { lazy, Suspense, useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

const MainPage = lazy(() => import('@/components/playground/MainPage'))
const ChatContainer = lazy(() => import('@/components/playground/chat/ChatContainer'))
const HistoryWrapper = lazy(() => import('@/components/playground/history/HistoryWrapper'))
const BeusChatContainer = lazy(() => import('@/components/contactus/ChatContainer'))
const ReportLayout = lazy(() => import('@/components/aireport/common/ReportLayout'))
const ScrollReport = lazy(() => import('@/components/aireport/scroll/ScrollReport'))
const AgentHub = lazy(() => import('@/components/agent/AgentHub'))
const AgentBuilder = lazy(() => import('@/components/agent/AgentBuilder'))
const ServerRegistry = lazy(() => import('@/components/server/ServerRegistry'))

function PageTitleUpdater() {
  const location = useLocation()
  const { t } = useTranslation()

  useEffect(() => {
    const routeTitles = {
      '/schemaTag': 'route.schemaTag'
    }

    let title = 'Solomon'
    for (const [path, titleKey] of Object.entries(routeTitles)) {
      if (location.pathname.startsWith(path)) {
        title = t(titleKey)
        break
      }
    }
    document.title = title
  }, [location.pathname, t])

  return null
}

export default function AppRoutes() {
  return (
    <>
      <PageTitleUpdater />
      <Suspense fallback={<div />}>
        <Routes>
          <Route path="/" element={<Navigate to="/admin" replace />} />
          <Route path="/admin" element={<MainPage />} />
          <Route path="/admin/chat/:agent" element={<ChatContainer />} />
          <Route path="/admin/history/:agent" element={<HistoryWrapper />} />
          <Route path="/admin/agents" element={<AgentHub />} />
          <Route path="/admin/agents/new" element={<AgentBuilder />} />
          <Route path="/admin/agents/:id" element={<AgentBuilder />} />
          <Route path="/admin/servers" element={<ServerRegistry />} />
          <Route path="/heatmap/:id" element={<ReportLayout />} />
          <Route path="/scroll/:id" element={<ScrollReport />} />
          <Route path="/schemaTag/:id" element={<ReportLayout />} />
          <Route path="/whitePaper/:id" element={<ReportLayout />} />
          <Route path="/cxTrends/:id" element={<ReportLayout />} />
          <Route path="/beusChat" element={<BeusChatContainer />} />
          <Route path="/schemaChat" element={<BeusChatContainer />} />
        </Routes>
      </Suspense>
    </>
  )
}
