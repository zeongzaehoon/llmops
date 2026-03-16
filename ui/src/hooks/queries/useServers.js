import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getMcpServers, enrollMcpServer, updateMcpServer, deleteMcpServer } from '@/api/agents'

export function useServers() {
  return useQuery({
    queryKey: ['servers'],
    queryFn: () => getMcpServers().then((r) => r.data?.data || []),
    staleTime: 30_000,
  })
}

export function useCreateServer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: enrollMcpServer,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['servers'] }),
  })
}

export function useUpdateServer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: updateMcpServer,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['servers'] }),
  })
}

export function useDeleteServer() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteMcpServer,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['servers'] }),
  })
}
