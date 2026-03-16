import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getToolsets,
  getToolset,
  createToolset,
  updateToolset,
  deleteToolset,
  deployToolset,
} from '@/api/agents'

export function useToolsets() {
  return useQuery({
    queryKey: ['toolsets'],
    queryFn: () => getToolsets().then((r) => r.data?.data || []),
    staleTime: 30_000,
  })
}

export function useToolsetsByAgent(agent) {
  return useQuery({
    queryKey: ['toolsets', { agent }],
    queryFn: () => getToolset({ agent }).then((r) => r.data?.data || []),
    enabled: !!agent,
    staleTime: 30_000,
  })
}

export function useCreateToolset() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createToolset,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['toolsets'] })
    },
  })
}

export function useUpdateToolset() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: updateToolset,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['toolsets'] })
    },
  })
}

export function useDeleteToolset() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteToolset,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['toolsets'] })
    },
  })
}

export function useDeployToolset() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deployToolset,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['toolsets'] })
      qc.invalidateQueries({ queryKey: ['agents'] })
    },
  })
}
