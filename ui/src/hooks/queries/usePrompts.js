import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getPromptVersions,
  getPromptData,
  getDeployList,
  insertPrompt,
  deployPrompt,
  rollbackPrompt,
} from '@/api/agents'

export function useVersions(agent) {
  return useQuery({
    queryKey: ['promptVersions', agent],
    queryFn: () => getPromptVersions({ agent, kind: 'prompt' }).then((r) => r.data?.data || []),
    enabled: !!agent,
  })
}

export function usePromptData(agent, id) {
  return useQuery({
    queryKey: ['promptData', agent, id],
    queryFn: () => getPromptData({ agent, kind: 'prompt', id }).then((r) => r.data?.data || null),
    enabled: !!agent && !!id,
  })
}

export function useDeployList() {
  return useQuery({
    queryKey: ['deployList'],
    queryFn: () => getDeployList().then((r) => r.data?.data || []),
  })
}

export function useSavePrompt() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: insertPrompt,
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['promptVersions', vars.agent] })
    },
  })
}

export function useDeploy() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deployPrompt,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['deployList'] })
      qc.invalidateQueries({ queryKey: ['promptVersions'] })
    },
  })
}

export function useRollback() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: rollbackPrompt,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['deployList'] })
      qc.invalidateQueries({ queryKey: ['promptVersions'] })
    },
  })
}
