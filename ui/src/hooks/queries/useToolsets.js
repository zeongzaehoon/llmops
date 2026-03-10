import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getAgents,
  createAgent,
  updateAgent,
  deleteAgent,
  getToolsets,
  getToolset,
  createToolset,
  updateToolset,
  deleteToolset,
  deployToolset,
} from '@/api/agents'

// ---- Agent hooks ----
export function useAgents() {
  return useQuery({
    queryKey: ['agents'],
    queryFn: () => getAgents().then((r) => r.data?.data || r.data?.res?.data || []),
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

// ---- Toolset hooks ----
export function useToolsets() {
  return useQuery({
    queryKey: ['toolsets'],
    queryFn: () => getToolsets().then((r) => r.data?.res?.data || []),
    staleTime: 30_000,
  })
}

export function useToolset(data) {
  return useQuery({
    queryKey: ['toolset', data?.name],
    queryFn: () => getToolset(data).then((r) => r.data?.res?.data || null),
    enabled: !!data?.name,
    staleTime: 30_000,
  })
}

export function useCreateToolset() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createToolset,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['toolsets'] }),
  })
}

export function useUpdateToolset() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: updateToolset,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['toolsets'] }),
  })
}

export function useDeleteToolset() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteToolset,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['toolsets'] }),
  })
}

export function useDeployToolset() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deployToolset,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['toolsets'] }),
  })
}
