import { useState, useCallback } from 'react'
import { connect as connectApi } from '@/api/auth'
import { saveTokensFromResponse } from '@/utils/storage'

/**
 * Auth hook: connect(agent) to create session + JWT.
 * Returns { isConnected, isLoading, error, connect }
 */
export function useAuth() {
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const connect = useCallback(async (agent) => {
    setIsLoading(true)
    setError(null)

    try {
      const res = await connectApi(agent)
      saveTokensFromResponse(agent, res.data)
      setIsConnected(true)
    } catch (err) {
      setError(err?.message || '연결에 실패했습니다.')
      setIsConnected(false)
    } finally {
      setIsLoading(false)
    }
  }, [])

  return { isConnected, isLoading, error, connect }
}
