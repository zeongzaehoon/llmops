import { useState, useRef } from 'react'
import BaseSelect from '@/components/playground/common/BaseSelect'
import BaseLoading from '@/components/playground/common/BaseLoading'
import BaseButton from '@/components/playground/common/BaseButton'

import styles from './PromptDetailModal.module.scss'

import iconClipboard from '@/assets/icon--clipboard.svg'
import iconChevronBottom from '@/assets/icon--chevronBottom.svg'

const PromptDetailModal = ({
  title,
  versionList,
  selectedVersion,
  prompt,
  inputData,
  isLoading,
  onResetInput,
  onSelect,
  onClose,
  onSave,
  onInputDataChange
}) => {
  const [isEditMode, setIsEditMode] = useState(false)
  const scrollerRef = useRef(null)

  const handleSelectVersion = (selected) => {
    onSelect(selected)
  }

  const handleChangeEditMode = () => {
    if (isEditMode) {
      onResetInput()
    }
    setIsEditMode(!isEditMode)
  }

  const handleClickSave = () => {
    const confirmed = confirm('프롬프트를 수정하시겠습니까?')
    if (!confirmed) {
      return
    }
    onSave()
    handleChangeEditMode()
  }

  const handleClickClose = () => {
    onClose()
  }

  const copy = () => {
    navigator.clipboard.writeText(prompt.prompt).then(() => alert('텍스트를 복사했습니다.'))
  }

  const scrollToTop = () => {
    scrollerRef.current.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }

  const wrapperClasses = [
    styles['expanded-prompt-wrapper'],
    isEditMode ? styles.edit : ''
  ].filter(Boolean).join(' ')

  return (
    <div className={wrapperClasses}>
      <div className={styles['expanded-prompt-viewer']}>
        <div className={styles['expanded-prompt-viewer-header']}>
          <h1 className={styles['expanded-prompt-viewer-header-title']}>{title}</h1>
          <button className={styles['expanded-prompt-viewer-header-closeBtn']} onClick={handleClickClose}>
            &times;
          </button>
        </div>
        <div className={styles['expanded-prompt-viewer-controlbar']}>
          <div className={styles.version}>
            <p className={styles['version-label']}>Version:</p>
            {isEditMode ? (
              <p className={styles['version-edit']}>입력 중..</p>
            ) : (
              <BaseSelect
                list={versionList.map((item) => item.title)}
                memo={versionList.map((item) => item.memo || '')}
                selected={selectedVersion && selectedVersion.title}
                onSelect={handleSelectVersion}
              />
            )}
          </div>
          <div className={styles.buttons}>
            <BaseButton color={isEditMode ? 'light' : 'primary'} onClick={handleChangeEditMode}>
              {isEditMode ? '취소' : '신규'}
            </BaseButton>
            {isEditMode && (
              <BaseButton onClick={handleClickSave}>저장</BaseButton>
            )}
          </div>
        </div>
        <div className={styles['expanded-prompt-viewer-body']} ref={scrollerRef}>
          <div className={styles.section}>
            <div className={styles['section-header']}>
              <p className={styles['section-header-title']}>Comment</p>
            </div>
            <div className={styles['section-body']}>
              {isEditMode ? (
                <div className={`${styles['section-body-textarea']} ${styles.short}`}>
                  <textarea
                    cols="30"
                    rows="10"
                    value={inputData.memo}
                    onChange={(e) => onInputDataChange({ ...inputData, memo: e.target.value })}
                  />
                </div>
              ) : !isLoading ? (
                <p>{prompt && prompt.memo}</p>
              ) : (
                <BaseLoading />
              )}
            </div>
          </div>
          <div className={styles.section}>
            <div className={`${styles['section-header']} ${styles.flex}`}>
              <p className={styles['section-header-title']}>Prompt</p>
              <button className={styles['section-header-copyBtn']} onClick={copy}>
                <img src={iconClipboard} alt="복사 버튼" />
              </button>
            </div>
            <div className={styles['section-body']}>
              {isEditMode ? (
                <div className={`${styles['section-body-textarea']} ${styles.long}`}>
                  <textarea
                    cols="30"
                    rows="10"
                    value={inputData.prompt}
                    onChange={(e) => onInputDataChange({ ...inputData, prompt: e.target.value })}
                  />
                </div>
              ) : !isLoading ? (
                <p>{prompt && prompt.prompt}</p>
              ) : (
                <BaseLoading />
              )}
            </div>
          </div>
          <div className={styles['auto-scroll-button']} onClick={scrollToTop}>
            <img src={iconChevronBottom} alt="scroll button" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default PromptDetailModal
