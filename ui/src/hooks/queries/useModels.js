import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getModels, getCurrentModel, setVendorAndModel } from '@/api/agents'

export function useModels() {
  return useQuery({
    queryKey: ['models'],
    queryFn: () =>
      getModels().then((r) => {
        const groups = r.data?.data?.modelList || []
        return groups.flatMap((g) =>
          (g.models || [])
            .filter((m) => !m.disabled)
            .map((m) => ({ vendor: g.company, model: m.name })),
        )
      }),
    staleTime: 60_000 * 5,
  })
}

export function useCurrentModel(agent) {
  return useQuery({
    queryKey: ['currentModel', agent],
    queryFn: () => getCurrentModel(agent).then((r) => r.data?.data || null),
    enabled: !!agent,
  })
}

export function useSetModel() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: setVendorAndModel,
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['currentModel', vars.agent] })
    },
  })
}
