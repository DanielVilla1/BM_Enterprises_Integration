// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: AppShell =====
// Purpose: The frame around every screen: sidebar, top bar, phone dock, theme toggle
// Inputs: pages, active page, user details, a user-menu slot and content (props only)
// Returns: responsive layout markup
// Flow:
// 1. Large screens: permanent sidebar grouped by section
// 2. Phones: top bar with a slide-in menu plus a bottom dock for the first five pages
// 3. Selecting a page closes the slide-in menu

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useRef } from 'react'
import { groupNavigation } from '../utils/navigation'
import { initialsOf } from '../utils/formatting'
import { Icon } from './Icon'

const DOCK_LIMIT = 5

/**
 * @function BrandMark
 * @description The product logo block.
 * @returns {import('react').ReactElement}
 */
function BrandMark() {
  return (
    <div className="flex items-center gap-3">
      <span className="flex h-10 w-10 items-center justify-center rounded-box bg-primary text-primary-content shadow">
        <Icon name="truck" className="h-6 w-6" />
      </span>
      <div className="leading-tight">
        <p className="text-base font-extrabold tracking-tight">BM Enterprises</p>
        <p className="text-xs text-base-content/60">Hauling operations</p>
      </div>
    </div>
  )
}

/**
 * @function AppShell
 * @description Pure UI application frame.
 * @param {Object} componentProps Props: pages, activePage, onSelect, userName, roleLabel, userSlot, theme, onToggleTheme, children
 * @returns {import('react').ReactElement}
 */
export function AppShell({
  pages,
  activePage,
  onSelect,
  userName,
  roleLabel,
  userSlot,
  theme,
  onToggleTheme,
  children,
}) {
  const drawerToggleReference = useRef(null)
  const activeLabel = pages.find((page) => page.key === activePage)?.label ?? ''

  const choosePage = (pageKey) => {
    if (drawerToggleReference.current) drawerToggleReference.current.checked = false
    onSelect(pageKey)
  }

  return (
    <div className="drawer lg:drawer-open">
      <input
        id="app-drawer"
        ref={drawerToggleReference}
        type="checkbox"
        className="drawer-toggle"
      />
      <div className="drawer-content flex min-h-screen flex-col bg-base-200">
        <header className="navbar sticky top-0 z-30 border-b border-base-300 bg-base-100/90 backdrop-blur">
          <div className="flex-none lg:hidden">
            <label htmlFor="app-drawer" className="btn btn-ghost btn-square" aria-label="Open menu">
              <Icon name="menu" />
            </label>
          </div>
          <div className="min-w-0 flex-1 px-2 text-lg font-semibold">
            <span className="truncate">{activeLabel}</span>
          </div>
          <div className="flex flex-none items-center gap-1">
            <button
              type="button"
              className="btn btn-ghost btn-circle"
              onClick={onToggleTheme}
              aria-label={theme === 'bm-light' ? 'Switch to dark theme' : 'Switch to light theme'}
            >
              <Icon name={theme === 'bm-light' ? 'moon' : 'sun'} />
            </button>
            <div className="ml-1 hidden items-center gap-2 sm:flex">
              <div className="text-right leading-tight">
                <p className="text-sm font-semibold">{userName}</p>
                <p className="text-xs text-base-content/60">{roleLabel}</p>
              </div>
            </div>
            <div className="ml-1 flex h-10 items-center">{userSlot}</div>
          </div>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 space-y-6 p-4 pb-28 lg:p-8 lg:pb-8">
          {children}
        </main>

        <nav
          className="dock dock-sm z-30 border-t border-base-300 bg-base-100 lg:hidden"
          aria-label="Quick navigation"
        >
          {pages.slice(0, DOCK_LIMIT).map((page) => (
            <button
              key={page.key}
              type="button"
              className={page.key === activePage ? 'dock-active text-primary' : ''}
              onClick={() => choosePage(page.key)}
              aria-current={page.key === activePage ? 'page' : undefined}
            >
              <Icon name={page.icon} />
              <span className="dock-label capitalize">{page.label.split(' ').slice(-1)[0]}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="drawer-side z-40">
        <label htmlFor="app-drawer" aria-label="Close menu" className="drawer-overlay" />
        <aside className="flex min-h-full w-72 flex-col border-r border-base-300 bg-base-100">
          <div className="border-b border-base-300 p-5">
            <BrandMark />
          </div>
          <nav className="flex-1 overflow-y-auto p-3" aria-label="Main">
            {groupNavigation(pages).map((section) => (
              <ul key={section.group} className="menu w-full gap-1 p-0">
                <li className="menu-title mt-3 text-xs uppercase tracking-wider">
                  {section.group}
                </li>
                {section.items.map((page) => (
                  <li key={page.key}>
                    <button
                      type="button"
                      className={page.key === activePage ? 'menu-active font-semibold' : ''}
                      onClick={() => choosePage(page.key)}
                      aria-current={page.key === activePage ? 'page' : undefined}
                    >
                      <Icon name={page.icon} className="h-5 w-5" />
                      <span className="flex-1 text-left">{page.label}</span>
                      {page.preview ? (
                        <span className="badge badge-xs badge-warning badge-soft">Soon</span>
                      ) : null}
                    </button>
                  </li>
                ))}
              </ul>
            ))}
          </nav>
          <div className="flex items-center gap-3 border-t border-base-300 p-4">
            <div className="avatar avatar-placeholder">
              <div className="w-10 rounded-full bg-primary text-primary-content">
                <span className="text-sm font-bold">{initialsOf(userName)}</span>
              </div>
            </div>
            <div className="min-w-0 leading-tight">
              <p className="truncate text-sm font-semibold">{userName}</p>
              <p className="truncate text-xs text-base-content/60">{roleLabel}</p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
