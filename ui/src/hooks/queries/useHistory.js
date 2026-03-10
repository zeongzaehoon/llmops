import { useQuery } from '@tanstack/react-query'
import { getHistory } from '@/api/chat'

export function useHistory(agent) {
  return useQuery({
    queryKey: ['history', agent],
    queryFn: () => getHistory(agent).then((r) => r.data?.res?.data || []),
    enabled: !!agent,
    staleTime: 30_000,
  })
}
