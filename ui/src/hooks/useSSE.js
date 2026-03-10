import { useState, useRef, useCallback } from 'react'
import { askStream } from '@/api/chat'

/**
 * SSE streaming hook.
 * Returns { content, askCode, isStreaming, error, ask, abort }
 */
export function useSSE() {
  const [content, setContent] = useState('')
  const [askCode, setAskCode] = useState(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState(null)
  const aborterRef = useRef(null)

  const abort = useCallback(() => {
    aborterRef.current?.abort()
    setIsStreaming(false)
  }, [])

  const ask = useCallback((agent, payload) => {
    // Abort any in-flight request
    aborterRef.current?.abort()

    setContent('')
    setAskCode(null)
    setError(null)
    setIsStreaming(true)

    const aborter = askStream(agent, payload, {
      onStart: (code) => {
        setAskCode(code)
      },
      onData: (chunk) => {
        setContent((prev) => prev + chunk)
      },
      onEnd: () => {
        setIsStreaming(false)
      },
      onError: (err) => {
        setError(typeof err === 'string' ? err : err?.message || '오류가 발생했습니다.')
        setIsStreaming(false)
      },
    })

    aborterRef.current = aborter
  }, [])

  return { content, askCode, isStreaming, error, ask, abort }
}
