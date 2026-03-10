import { useState, useRef, useMemo, useCallback } from 'react'
import { DEFAULT_TYPE } from '@/utils/constants'
import styles from './BaseSelect.module.scss'

const BaseSelect = ({
  list = [],
  memo,
  selected,
  grayscale = false,
  ordering = false,
  markList,
  markText,
  padding,
  maxContent = false,
  onSelect
}) => {
  const selectRef = useRef(null)
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const optionsPosition = useMemo(() => {
    if (!selectRef.current) return 'auto'
    const rect = selectRef.current.getBoundingClientRect()
    const windowHeight = window.innerHeight
    return windowHeight - rect.bottom < 100 ? '100%' : 'auto'
  }, [dropdownOpen])

  const toggleDropdown = useCallback(() => {
    setDropdownOpen((prev) => !prev)
  }, [])

  const selectOption = useCallback(
    (option) => {
      onSelect?.(option)
      setDropdownOpen(false)
    },
    [onSelect]
  )

  const inputClassName = `${styles['select-input']} ${grayscale ? styles.grayscale : ''}`

  return (
    <div className={styles.select} ref={selectRef}>
      <div
        className={inputClassName}
        onClick={toggleDropdown}
        style={padding ? { padding } : undefined}
      >
        {selected && ordering && selected !== DEFAULT_TYPE && (
          <span className={styles.index}>{list.indexOf(selected)} </span>
        )}
        {selected ? selected : 'Select an option'}
        {markText && markList && markList.indexOf(selected) !== -1 && (
          <span className={styles.mark}>{markText}</span>
        )}
      </div>

      {dropdownOpen && (
        <div className={styles['select-background']} onClick={toggleDropdown} />
      )}

      {!memo ? (
        <div
          className={styles['select-options']}
          style={{
            display: dropdownOpen ? undefined : 'none',
            bottom: optionsPosition,
            width: maxContent ? 'max-content' : '100%'
          }}
        >
          {list.map((option, index) => (
            <div className={styles['select-options-wrapper']} key={typeof option === 'object' ? option.group : option}>
              {typeof option === 'object' ? (
                <div className={styles['select-options-group']}>
                  <p className={styles['select-options-group-title']}>{option.group}</p>
                  {option.list.map((groupOption) => (
                    <div
                      key={groupOption.name}
                      className={`${styles['select-options-item']} ${styles.group} ${
                        groupOption.disabled ? styles.disabled : ''
                      } ${groupOption.name === selected ? styles.selected : ''}`}
                      onClick={() =>
                        !groupOption.disabled && selectOption(groupOption.name)
                      }
                    >
                      {groupOption.name}
                    </div>
                  ))}
                </div>
              ) : (
                <div
                  className={`${styles['select-options-item']} ${
                    option === selected ? styles.selected : ''
                  }`}
                  onClick={() => selectOption(option)}
                >
                  {ordering && option !== DEFAULT_TYPE && (
                    <span className={styles.index}>{index} </span>
                  )}
                  {option}
                  {markText && markList && markList.indexOf(option) !== -1 && (
                    <span className={styles.mark}>{markText}</span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div
          className={styles['select-options']}
          style={{ display: dropdownOpen ? undefined : 'none' }}
        >
          {list.map((option, idx) => (
            <div
              key={option}
              className={`${styles['select-options-item']} ${
                option === selected ? styles.selected : ''
              }`}
              title={memo[idx] ? memo[idx].slice(0, 50) : ''}
              onClick={() => selectOption(option)}
            >
              {option}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default BaseSelect
