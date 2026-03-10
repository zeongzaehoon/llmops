import toast, { Toaster } from 'react-hot-toast'

/**
 * Toast notification wrapper around react-hot-toast.
 * <SolToaster /> renders the toast container.
 * useToast() returns convenience methods.
 */
export function SolToaster() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: 'var(--sol-surface-elevated)',
          color: 'var(--sol-text-primary)',
          border: '1px solid var(--sol-border-primary)',
          fontSize: '13px',
        },
        success: {
          iconTheme: {
            primary: 'var(--sol-status-success)',
            secondary: 'var(--sol-surface-elevated)',
          },
        },
        error: {
          iconTheme: {
            primary: 'var(--sol-status-danger)',
            secondary: 'var(--sol-surface-elevated)',
          },
        },
      }}
    />
  )
}

export function useToast() {
  return {
    success: (msg) => toast.success(msg),
    error: (msg) => toast.error(msg),
    info: (msg) => toast(msg),
    loading: (msg) => toast.loading(msg),
    dismiss: (id) => toast.dismiss(id),
  }
}
