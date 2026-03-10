import { useMutation } from '@tanstack/react-query'
import * as vectorsApi from '@/api/vectors'

export function useVectorUpsert() {
  return useMutation({ mutationFn: vectorsApi.upsert })
}

export function useVectorSearch() {
  return useMutation({ mutationFn: vectorsApi.search })
}

export function useVectorDeleteById() {
  return useMutation({ mutationFn: vectorsApi.deleteById })
}

export function useVectorDeleteByFilter() {
  return useMutation({ mutationFn: vectorsApi.deleteByFilter })
}
