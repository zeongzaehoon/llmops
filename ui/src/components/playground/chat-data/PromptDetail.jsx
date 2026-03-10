import { useState, useRef, useEffect } from 'react'
import { getPrompt, getPromptList, insertPrompt } from '@/api/adminApi.js'
import { formatDate } from '@/utils/parse.js'
import BaseSelect from '@/components/playground/common/BaseSelect'
import BaseLoading from '@/components/playground/common/BaseLoading'
import PromptDetailModal from './PromptDetailModal'
import BaseButton from '@/components/playground/common/BaseButton'

import styles from './PromptDetail.module.scss'

import iconExpand from '@/assets/icon--expand.svg'
import iconClipboard from '@/assets/icon--clipboard.svg'
import iconChevronBottom from '@/assets/icon--chevronBottom.svg'

const initialPrompt = {
  memo: '',
  prompt: ''
}

const PromptDetail = ({ title, kind, size, agent, style }) => {
  const [versionList, setVersionList] = useState([])
  const [prompt, setPrompt] = useState(initialPrompt)
  const [latestPrompt, setLatestPrompt] = useState(initialPrompt)
  const [inputData, setInputData] = useState(initialPrompt)
  const [isEditMode, setIsEditMode] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [selectedVersion, setSelectedVersion] = useState(undefined)
  const [isLoading, setIsLoading] = useState(undefined)
  const scrollerRef = useRef(null)

  useEffect(() => {
    getPromptVersionList()
  }, [])

  function getPromptVersionList() {
    getPromptList({ agent, kind })
      .then(async (res) => {
        const list = res.data.data

        if (list.length > 0) {
          for (let i in list) {
            list[i]['title'] = (list[i].getResult ? '* ' : '- ') + formatDate(list[i].date, 'num')
          }

          setVersionList(list)

          await handleSelectVersionFn(list, list[0].title, true)
        } else {
          setVersionList(list)
        }
      })
      .catch((e) => console.log(e))
  }

  const handleSelectVersionFn = (list, selected, isInit = false) => {
    const foundVersion = (list || versionList).find((item) => item.title === selected)
    setSelectedVersion(foundVersion)
    setIsLoading(true)

    return getPrompt({ agent, kind, id: foundVersion.id })
      .then((res) => {
        const promptData = res.data.data
        setPrompt(promptData)
        setIsLoading(false)

        if (isInit) {
          setLatestPrompt({ prompt: promptData.prompt, id: promptData.id })
          setInputData({ prompt: promptData.prompt, memo: '' })
        }
      })
      .catch((e) => {
        console.log(e)
      })
      .finally(() => {
        setIsLoading(false)
      })
  }

  const handleSelectVersion = (selected) => {
    handleSelectVersionFn(null, selected, false)
  }

  const handleChangeEditMode = () => {
    if (isEditMode) {
      resetInputData()
    }
    setIsEditMode(!isEditMode)
  }

  const resetInputData = () => {
    setInputData({ prompt: latestPrompt.prompt, memo: '' })
  }

  const handleClickSave = () => {
    const confirmed = confirm('프롬프트를 저장하시겠습니까?')
    if (!confirmed) {
      return
    }
    saveNewPrompt()
    handleChangeEditMode()
  }

  const saveNewPrompt = () => {
    let data = {
      agent,
      kind,
      prompt: inputData.prompt,
      memo: inputData.memo
    }

    insertPrompt(data)
      .then((res) => {
        alert('프롬프트 저장 완료')
        console.log(res)
      })
      .catch((e) => {
        alert('프롬프트 저장에 실패했습니다.')
        console.log(e)
      })
      .finally(() => {
        getPromptVersionList()
      })
  }

  const handleExpandViewer = () => {
    setIsExpanded(!isExpanded)
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

  const getSize = () => {
    return 'full'
  }

  const wrapperClasses = [
    styles['prompt-wrapper'],
    isEditMode ? styles.edit : '',
    styles[getSize()]
  ].filter(Boolean).join(' ')

  return (
    <div className={wrapperClasses} style={style}>
      <div className={styles['prompt-viewer']}>
        <div className={styles['prompt-viewer-header']}>
          <p className={styles['prompt-viewer-header-title']}>{title}</p>
          {!isEditMode && (
            <button
              className={styles['prompt-viewer-header-expandBtn']}
              onClick={handleExpandViewer}
            >
              <img src={iconExpand} alt="expand button" />
            </button>
          )}
        </div>
        <div className={styles['prompt-viewer-controlbar']}>
          <div className={styles.version}>
            <p className={styles['version-label']}>Version:</p>
            {isEditMode ? (
              <p className={styles['version-edit']}>입력 중..</p>
            ) : (
              <BaseSelect
                list={versionList.map((item) => item.title)}
                memo={versionList.map((item) => item.memo || '')}
                selected={selectedVersion && selectedVersion.title}
                grayscale={selectedVersion && latestPrompt && latestPrompt.id !== selectedVersion.id}
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
        <div className={styles['prompt-viewer-body']} ref={scrollerRef}>
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
                    onChange={(e) => setInputData({ ...inputData, memo: e.target.value })}
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
                <div className={`${styles['section-body-textarea']} ${styles.long} ${styles[getSize()]}`}>
                  <textarea
                    cols="30"
                    rows="10"
                    value={inputData.prompt}
                    onChange={(e) => setInputData({ ...inputData, prompt: e.target.value })}
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
      <div className={styles.dim}></div>
      {isExpanded && (
        <PromptDetailModal
          title={title}
          versionList={versionList}
          selectedVersion={selectedVersion}
          prompt={prompt}
          inputData={inputData}
          isLoading={isLoading}
          onResetInput={resetInputData}
          onSave={saveNewPrompt}
          onSelect={handleSelectVersion}
          onClose={handleExpandViewer}
          onInputDataChange={setInputData}
        />
      )}
    </div>
  )
}

export default PromptDetail
