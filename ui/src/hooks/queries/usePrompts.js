import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as promptsApi from '@/api/prompts'

export function useVersions(agent) {
  return useQuery({
    queryKey: ['promptVersions', agent],
    queryFn: () => promptsApi.getVersion({ agent, kind: 'prompt' }).then((r) => r.data?.res?.data || []),
    enabled: !!agent,
  })
}

export function usePromptData(agent, version) {
  return useQuery({
    queryKey: ['promptData', agent, version],
    queryFn: () => promptsApi.getData({ agent, kind: 'prompt', id: version }).then((r) => r.data?.res?.data || null),
    enabled: !!agent,
  })
}

export function useDeployList() {
  return useQuery({
    queryKey: ['deployList'],
    queryFn: () => promptsApi.getDeployList().then((r) => r.data?.res?.data || []),
  })
}

export function useSavePrompt() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: promptsApi.insertPrompt,
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['promptVersions', vars.agent] })
    },
  })
}

export function useDeploy() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: promptsApi.deploy,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['deployList'] })
      qc.invalidateQueries({ queryKey: ['promptVersions'] })
    },
  })
}

export function useRollback() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: promptsApi.rollback,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['deployList'] })
      qc.invalidateQueries({ queryKey: ['promptVersions'] })
    },
  })
}
