import { useState } from 'react'
import BaseButton from '@/components/playground/common/BaseButton'

import styles from './PromptModuleCreateModal.module.scss'

const PromptModuleCreateModal = ({ list, onClose, onSave }) => {
  const [inputText, setInputText] = useState('')

  const handleClickClose = () => {
    onClose()
  }

  const handleClickSave = () => {
    const isAvailable = checkAvailable()
    if (!isAvailable) return

    onSave(inputText.trim())
    alert(`'${inputText.trim()}' 프롬프트 모듈이 생성되었습니다. 신규 프롬프트를 생성해주세요.`)
    onClose()
  }

  const checkAvailable = () => {
    if (list.indexOf(inputText) !== -1) {
      alert('동일한 이름의 프롬프트 모듈이 존재합니다.')
      setInputText('')
      return false
    } else if (inputText === 'PING-PONG SET') {
      alert('해당 이름으로 프롬프트 모듈을 생성할 수 없습니다.')
      setInputText('')
      return false
    } else {
      return true
    }
  }

  return (
    <div className={styles['modal-wrapper']}>
      <div className={styles['modal-viewer']}>
        <div className={styles['modal-viewer-header']}>
          <h1 className={styles['modal-viewer-header-title']}>프롬프트 모듈 생성</h1>
          <button className={styles['modal-viewer-header-closeBtn']} onClick={handleClickClose}>
            &times;
          </button>
        </div>
        <div className={styles['modal-viewer-body']}>
          <p className={styles['modal-viewer-body-desc']}>
            ※ 저장 후 프롬프트를 생성해야 정상적으로 모듈이 생성됩니다.
          </p>
          <div className={styles['modal-viewer-body-section']}>
            <input
              className={styles['modal-viewer-body-section-input']}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="New prompt module"
            />
            <BaseButton size="medium" onClick={handleClickSave}>저장</BaseButton>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PromptModuleCreateModal
