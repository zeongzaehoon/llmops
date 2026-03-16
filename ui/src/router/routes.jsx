import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'

// Layout
const AdminLayout = lazy(() => import('@/layouts/AdminLayout'))

// Feature pages
const DashboardPage = lazy(() => import('@/features/dashboard/DashboardPage'))
const AgentHubPage = lazy(() => import('@/features/agents/AgentHubPage'))
const AgentDetailPage = lazy(() => import('@/features/agents/AgentDetailPage'))
const AgentBuilderPage = lazy(() => import('@/features/agents/AgentBuilderPage'))
const ServersPage = lazy(() => import('@/features/servers/ServersPage'))
const GraphHubPage = lazy(() => import('@/features/graphs/GraphHubPage'))
const GraphBuilderPage = lazy(() => import('@/features/graphs/GraphBuilderPage'))
const PlaygroundPage = lazy(() => import('@/features/playground/PlaygroundPage'))
const ChatPage = lazy(() => import('@/features/playground/ChatPage'))
const KnowledgePage = lazy(() => import('@/features/vectors/KnowledgePage'))
const HistoryPage = lazy(() => import('@/features/history/HistoryPage'))

// Existing pages (lazy)
const ReportLayout = lazy(() => import('@/components/aireport/common/ReportLayout'))
const ScrollReport = lazy(() => import('@/components/aireport/scroll/ScrollReport'))
const BeusChatContainer = lazy(() => import('@/components/contactus/ChatContainer'))

function SuspenseWrapper({ children }) {
  return <Suspense fallback={<div />}>{children}</Suspense>
}

function LazyPage({ Component }) {
  return (
    <SuspenseWrapper>
      <Component />
    </SuspenseWrapper>
  )
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/admin" replace />,
  },
  {
    path: '/admin',
    element: (
      <SuspenseWrapper>
        <AdminLayout />
      </SuspenseWrapper>
    ),
    children: [
      { index: true, element: <LazyPage Component={DashboardPage} /> },
      { path: 'agents', element: <LazyPage Component={AgentHubPage} /> },
      { path: 'agents/:agent', element: <LazyPage Component={AgentDetailPage} /> },
      { path: 'agents/:agent/toolset/new', element: <LazyPage Component={AgentBuilderPage} /> },
      { path: 'agents/:agent/toolset/:id', element: <LazyPage Component={AgentBuilderPage} /> },
      { path: 'servers', element: <LazyPage Component={ServersPage} /> },
      { path: 'graphs', element: <LazyPage Component={GraphHubPage} /> },
      { path: 'graphs/new', element: <LazyPage Component={GraphBuilderPage} /> },
      { path: 'graphs/:id', element: <LazyPage Component={GraphBuilderPage} /> },
      { path: 'playground', element: <LazyPage Component={PlaygroundPage} /> },
      { path: 'playground/:agent', element: <LazyPage Component={ChatPage} /> },
      { path: 'knowledge', element: <LazyPage Component={KnowledgePage} /> },
      { path: 'history/:agent', element: <LazyPage Component={HistoryPage} /> },
    ],
  },
  // Existing report/chat routes
  {
    path: '/heatmap/:id',
    element: <LazyPage Component={ReportLayout} />,
  },
  {
    path: '/scroll/:id',
    element: <LazyPage Component={ScrollReport} />,
  },
  {
    path: '/schemaTag/:id',
    element: <LazyPage Component={ReportLayout} />,
  },
  {
    path: '/whitePaper/:id',
    element: <LazyPage Component={ReportLayout} />,
  },
  {
    path: '/cxTrends/:id',
    element: <LazyPage Component={ReportLayout} />,
  },
  {
    path: '/beusChat',
    element: <LazyPage Component={BeusChatContainer} />,
  },
  {
    path: '/schemaChat',
    element: <LazyPage Component={BeusChatContainer} />,
  },
])
