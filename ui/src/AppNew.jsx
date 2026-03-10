import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import { SolToaster } from '@/components/feedback/Toast'
import { router } from '@/router/routes'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export default function AppNew() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <SolToaster />
    </QueryClientProvider>
  )
}
