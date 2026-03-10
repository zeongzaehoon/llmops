import { useState, useRef } from 'react'
import { DEFAULT_TYPE } from '@/utils/constants.js'
import BaseSelect from '@/components/playground/common/BaseSelect'
import BaseLoading from '@/components/playground/common/BaseLoading'
import BaseButton from '@/components/playground/common/BaseButton'

import styles from './PromptModuleDetailModal.module.scss'

import iconClipboard from '@/assets/icon--clipboard.svg'
import iconChevronBottom from '@/assets/icon--chevronBottom.svg'

const PromptModuleDetailModal = ({
  title,
  agent,
  typeList,
  roleNameList,
  updatedRoleNameList,
  versionList,
  selectedType,
  selectedRoleName,
  selectedVersion,
  entirePrompt,
  prompt,
  viewAllMode,
  isLoading,
  isAllModeLoading,
  inputData,
  onResetInput,
  onSelectVersion,
  onClose,
  onSave,
  onSelectType,
  onSelectRolename,
  onShowModal,
  onInputDataChange
}) => {
  const [isEditMode, setIsEditMode] = useState(false)
  const scrollerRef = useRef(null)

  const handleChangeEditMode = () => {
    if (isEditMode) {
      onResetInput()
    } else if (!selectedRoleName) {
      alert('프롬프트 모듈을 선택해주세요.')
      return
    }
    setIsEditMode(!isEditMode)
  }

  const handleClickSave = () => {
    const confirmed = confirm('프롬프트를 저장하시겠습니까?')
    if (!confirmed) {
      return
    }
    onSave()
    handleChangeEditMode()
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
          <div className={styles['expanded-prompt-viewer-header-cont']}>
            <h1 className={styles['expanded-prompt-viewer-header-cont-title']}>{title}</h1>
          </div>
          <button className={styles['expanded-prompt-viewer-header-closeBtn']} onClick={onClose}>
            &times;
          </button>
        </div>
        <div className={styles['expanded-prompt-viewer-controlbar']}>
          <div className={styles['expanded-prompt-viewer-controlbar-item']}>
            <div className={styles.version}>
              <p className={styles['version-label']}>Type:</p>
              <BaseSelect
                list={typeList}
                selected={selectedType}
                onSelect={(option) => onSelectType(option)}
              />
            </div>
          </div>
          <div className={styles['expanded-prompt-viewer-controlbar-item']}>
            <div className={styles.version}>
              <p className={styles['version-label']}>Module:</p>
              {isEditMode ? (
                <p className={styles['version-edit']}>{selectedRoleName}</p>
              ) : (
                <BaseSelect
                  list={roleNameList}
                  selected={selectedRoleName}
                  ordering={selectedType !== DEFAULT_TYPE}
                  markList={updatedRoleNameList}
                  markText="changed"
                  onSelect={(option) => onSelectRolename(option)}
                />
              )}
            </div>
            <div className={styles.buttons}>
              <BaseButton onClick={onShowModal}>신규</BaseButton>
            </div>
          </div>
          {selectedRoleName !== DEFAULT_TYPE && (
            <div className={styles['expanded-prompt-viewer-controlbar-item']}>
              <div className={styles.version}>
                <p className={styles['version-label']}>Version:</p>
                {isEditMode ? (
                  <p className={styles['version-edit']}>입력 중..</p>
                ) : (
                  <BaseSelect
                    list={versionList.map((item) => item.title)}
                    memo={versionList.map((item) => item.memo || '')}
                    selected={selectedVersion && selectedVersion.title}
                    onSelect={(option) => onSelectVersion(option)}
                  />
                )}
              </div>
              <div className={styles.buttons}>
                <BaseButton
                  color={isEditMode ? 'light' : 'primary'}
                  disabled={!selectedRoleName}
                  onClick={handleChangeEditMode}
                >
                  {isEditMode ? '취소' : '신규'}
                </BaseButton>
                {isEditMode && (
                  <BaseButton onClick={handleClickSave}>저장</BaseButton>
                )}
              </div>
            </div>
          )}
        </div>
        {viewAllMode ? (
          <div className={styles['expanded-prompt-viewer-body']} ref={scrollerRef}>
            {!isAllModeLoading ? (
              <div className={`${styles['entire-version']} ${styles['section-body']}`}>
                {entirePrompt ? (
                  entirePrompt.map((value, idx) => (
                    <p key={idx} title={value.roleName.trim()}>
                      {value.prompt}
                    </p>
                  ))
                ) : (
                  <p>저장된 프롬프트 모듈 조합이 없습니다.</p>
                )}
              </div>
            ) : (
              <BaseLoading />
            )}
            <div className={styles['auto-scroll-button']} onClick={scrollToTop}>
              <img src={iconChevronBottom} alt="scroll button" />
            </div>
          </div>
        ) : (
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
        )}
      </div>
    </div>
  )
}

export default PromptModuleDetailModal
