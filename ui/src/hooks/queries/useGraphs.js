import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getGraphs, getGraph, createGraph, updateGraph, deleteGraph } from '@/api/graphs'

export function useGraphs() {
  return useQuery({
    queryKey: ['graphs'],
    queryFn: () => getGraphs().then((r) => r.data?.res?.data || []),
    staleTime: 30_000,
  })
}

export function useGraph(data) {
  const id = data?.graph_id || data?.name
  return useQuery({
    queryKey: ['graph', id],
    queryFn: () => getGraph(data).then((r) => r.data?.res?.data || null),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useCreateGraph() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createGraph,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['graphs'] }),
  })
}

export function useUpdateGraph() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: updateGraph,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['graphs'] }),
  })
}

export function useDeleteGraph() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteGraph,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['graphs'] }),
  })
}
