import { useState, useCallback, useRef } from 'react'

export function useModal() {
  const [isVisible, setIsVisible] = useState(false)
  const [result, setResult] = useState(null)
  const resolveRef = useRef(null)

  const openModal = useCallback(() => {
    setIsVisible(true)
    setResult(null)
  }, [])

  const closeModal = useCallback((value) => {
    setIsVisible(false)
    setResult(value)
    if (resolveRef.current) {
      resolveRef.current(value)
      resolveRef.current = null
    }
  }, [])

  const getResult = useCallback(() => {
    return new Promise((resolve) => {
      resolveRef.current = resolve
    })
  }, [])

  const showModal = useCallback(async () => {
    openModal()
    return await getResult()
  }, [openModal, getResult])

  return {
    isVisible,
    openModal,
    closeModal,
    getResult,
    showModal
  }
}
