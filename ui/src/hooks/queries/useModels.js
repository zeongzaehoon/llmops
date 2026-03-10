import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as modelsApi from '@/api/models'

export function useModels() {
  return useQuery({
    queryKey: ['models'],
    queryFn: () => modelsApi.getModels().then((r) => r.data?.res?.data || []),
    staleTime: 60_000 * 5,
  })
}

export function useCurrentModel(agent) {
  return useQuery({
    queryKey: ['currentModel', agent],
    queryFn: () => modelsApi.getCurrentModel(agent).then((r) => r.data?.res?.data || null),
    enabled: !!agent,
  })
}

export function useSetModel() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: modelsApi.setVendorAndModel,
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['currentModel', vars.agent] })
    },
  })
}
