import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getAgents, createAgent, updateAgent, deleteAgent } from '@/api/agents'

export function useAgents() {
  return useQuery({
    queryKey: ['agents'],
    queryFn: () => getAgents().then((r) => r.data?.data || []),
    staleTime: 30_000,
  })
}

export function useCreateAgent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createAgent,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  })
}

export function useUpdateAgent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: updateAgent,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  })
}

export function useDeleteAgent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteAgent,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  })
}
