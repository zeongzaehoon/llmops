import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Bot,
  Server,
  GitFork,
  MessageSquare,
  BookOpen,
  Settings,
} from 'lucide-react'
import styles from './AdminLayout.module.scss'

const NAV_ITEMS = [
  { path: '/admin', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { path: '/admin/agents', label: 'Agents', icon: Bot },
  { path: '/admin/servers', label: 'Servers', icon: Server },
  { path: '/admin/graphs', label: 'Graphs', icon: GitFork },
  { path: '/admin/playground', label: 'Playground', icon: MessageSquare },
  { path: '/admin/knowledge', label: 'Knowledge', icon: BookOpen },
]

const BOTTOM_ITEMS = [
  { path: '/admin/settings', label: 'Settings', icon: Settings },
]

export default function AdminLayout() {
  const location = useLocation()

  const breadcrumbSegments = location.pathname
    .replace(/^\/admin\/?/, '')
    .split('/')
    .filter(Boolean)

  const pageTitle = breadcrumbSegments[0]
    ? breadcrumbSegments[0].charAt(0).toUpperCase() + breadcrumbSegments[0].slice(1)
    : 'Home'

  return (
    <div className={styles.layout}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarLogo}>
          <div className={styles.logoMark}>S</div>
          <span className={styles.logoText}>Solomon</span>
        </div>

        <nav className={styles.sidebarNav}>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.end}
                className={({ isActive }) =>
                  `${styles.navItem} ${isActive ? styles.active : ''}`
                }
              >
                <span className={styles.navIcon}>
                  <Icon size={18} strokeWidth={1.8} />
                </span>
                <span className={styles.navLabel}>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>

        <div className={styles.sidebarBottom}>
          {BOTTOM_ITEMS.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `${styles.navItem} ${isActive ? styles.active : ''}`
                }
              >
                <span className={styles.navIcon}>
                  <Icon size={18} strokeWidth={1.8} />
                </span>
                <span className={styles.navLabel}>{item.label}</span>
              </NavLink>
            )
          })}
        </div>
      </aside>

      {/* Main content area */}
      <div className={styles.main}>
        {/* TopBar */}
        <header className={styles.topbar}>
          <h1 className={styles.pageTitle}>{pageTitle}</h1>
        </header>

        {/* Page content */}
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
