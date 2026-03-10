import { useState, useEffect, useRef } from 'react'
import styles from './SearchInput.module.scss'

/**
 * Search input with built-in debounce.
 * @param {string} value - controlled value
 * @param {function} onChange - called with debounced value
 * @param {string} placeholder
 * @param {number} debounce - ms (default 300)
 */
export default function SearchInput({
  value: controlledValue,
  onChange,
  placeholder = '검색...',
  debounce = 300,
  className = '',
}) {
  const [localValue, setLocalValue] = useState(controlledValue ?? '')
  const timerRef = useRef(null)

  useEffect(() => {
    if (controlledValue !== undefined) {
      setLocalValue(controlledValue)
    }
  }, [controlledValue])

  const handleChange = (e) => {
    const val = e.target.value
    setLocalValue(val)

    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      onChange?.(val)
    }, debounce)
  }

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [])

  return (
    <div className={`${styles.wrapper} ${className}`}>
      <span className={styles.icon}>{'\u2315'}</span>
      <input
        type="text"
        className={styles.input}
        value={localValue}
        onChange={handleChange}
        placeholder={placeholder}
      />
    </div>
  )
}
