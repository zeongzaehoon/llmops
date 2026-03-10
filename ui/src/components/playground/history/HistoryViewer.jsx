import { useState, useCallback } from 'react'
import { convertMarkdownToHtml } from '@/utils/parse'
import { formatDate } from '@/utils/parse'
import { HISTORY_TAB } from '@/utils/constants'
import { updateMemo, downloadQuestion } from '@/api/adminApi'
import BaseButton from '@/components/playground/common/BaseButton'
import clipboardIcon from '@/assets/icon--clipboard.svg'
import loadingIcon from '@/assets/icon--loading-animated.svg'
import styles from './HistoryViewer.module.scss'

export default function HistoryViewer({
  tab,
  agent,
  selectedItem,
  isComparison,
  onNavigate,
  onReload
}) {
  const [isEditMode, setIsEditMode] = useState(false)
  const [newMemo, setNewMemo] = useState('')

  const handleChangeEditMode = useCallback(() => {
    if (isEditMode) {
      setNewMemo('')
    } else {
      setNewMemo(selectedItem?.memo || '')
    }
    setIsEditMode((prev) => !prev)
  }, [isEditMode, selectedItem])

  const handleClickSaveMemo = useCallback(() => {
    const data = {
      id: selectedItem.id,
      kind: tab,
      memo: newMemo,
      agent
    }

    updateMemo(data)
      .then((res) => {
        console.log(res)
        onReload?.(tab, selectedItem.id, isComparison)
        alert('메모 업데이트 완료')
      })
      .catch((e) => {
        console.log(e)
        alert('메모 업데이트에 실패했습니다.')
      })
      .finally(() => {
        handleChangeEditMode()
      })
  }, [selectedItem, tab, newMemo, agent, isComparison, onReload, handleChangeEditMode])

  const getMainContent = useCallback(
    (markdown = false) => {
      let content = ''
      if (tab === 'result') {
        content = selectedItem?.message || ''
      } else {
        content = selectedItem?.prompt || ''
      }

      if (markdown && tab !== 'refer') {
        return convertMarkdownToHtml(content.toString().trim())
      } else {
        return content
      }
    },
    [tab, selectedItem]
  )

  const navigate = useCallback(
    (navTab, id, type = null) => {
      onNavigate?.(navTab, id, type)
    },
    [onNavigate]
  )

  const copy = useCallback(() => {
    navigator.clipboard
      .writeText(getMainContent())
      .then(() => alert('텍스트를 복사했습니다.'))
  }, [getMainContent])

  const handleClickDownloadQuestion = useCallback((chatId) => {
    downloadQuestion({ id: chatId, responseType: 'blob' })
      .then((res) => {
        let filename = 'default-filename.json'
        const contentDisposition = res.headers['content-disposition']

        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(
            /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
          )
          if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1].replace(/['"]/g, '')
            filename = decodeURIComponent(escape(filename))
          }
        }

        const url = window.URL.createObjectURL(
          new Blob([res.data], {
            type: res.headers['content-type']
          })
        )
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
      })
      .catch((e) => console.log(e))
  }, [])

  if (!selectedItem) return null

  return (
    <div className={styles.wrapper}>
      {selectedItem.notfound ? (
        <p className={styles['flex-center']}>해당하는 데이터를 찾을 수 없습니다.</p>
      ) : selectedItem.loading ? (
        <div className={styles['flex-center']}>
          <img src={loadingIcon} alt="loading" />
        </div>
      ) : (
        <div className={styles.detail}>
          <div className={styles['detail-header']}>
            <div className={styles['detail-header-section']}>
              <p>
                {HISTORY_TAB[tab]}: {selectedItem.title}
              </p>
              <button className={styles.copyBtn} onClick={copy}>
                <img src={clipboardIcon} alt="복사 버튼" />
              </button>
            </div>
            <div className={styles['detail-header-section']}>
            </div>
          </div>
          <div
            className={`${styles['detail-body']} reset-font-size`}
            dangerouslySetInnerHTML={{ __html: getMainContent(true) }}
          />
          <div className={styles['detail-footer']}>
            {tab !== 'refer' && (
              <div className={styles['detail-footer-item']}>
                <span className={styles['detail-footer-item-label']}>Comment:</span>
                <div className={styles['flex-col']}>
                  {isEditMode ? (
                    <div className={styles['detail-footer-item-textarea']}>
                      <textarea
                        cols="30"
                        rows="10"
                        value={newMemo}
                        onChange={(e) => setNewMemo(e.target.value)}
                      />
                    </div>
                  ) : (
                    selectedItem.memo && (
                      <div className={styles['detail-footer-item-content']}>
                        {selectedItem.memo}
                      </div>
                    )
                  )}
                  <div className={styles.buttons}>
                    <BaseButton
                      color={isEditMode ? 'light' : 'primary'}
                      onClick={handleChangeEditMode}
                    >
                      {isEditMode ? '취소' : '수정'}
                    </BaseButton>
                    {isEditMode && (
                      <BaseButton onClick={handleClickSaveMemo}>저장</BaseButton>
                    )}
                  </div>
                </div>
              </div>
            )}
            {tab === 'result' && (
              <div className={styles['detail-footer-item']}>
                <span className={styles['detail-footer-item-label']}>Files:</span>
                <div className={styles['detail-footer-item-list']}>
                  {selectedItem.chat && (
                    <button
                      className={styles['detail-footer-item-list-item']}
                      onClick={() => handleClickDownloadQuestion(selectedItem.chat.id)}
                    >
                      {selectedItem.chat.filename}
                    </button>
                  )}
                </div>
              </div>
            )}
            <div className={styles['detail-footer-item']}>
              <span className={styles['detail-footer-item-label']}>Links:</span>
              <div className={styles['detail-footer-item-list']}>
                {Array.isArray(selectedItem.prompt) &&
                  selectedItem.prompt.map((prompt) => (
                    <button
                      key={prompt.id}
                      className={styles['detail-footer-item-list-item']}
                      onClick={() => navigate('prompt', prompt.id)}
                    >
                      프롬프트: {prompt.roleName} - {prompt.order} -{' '}
                      {formatDate(prompt.date, 'num')}
                    </button>
                  ))}
                {selectedItem.prompt &&
                  !Array.isArray(selectedItem.prompt) &&
                  selectedItem.prompt.id && (
                    <button
                      className={styles['detail-footer-item-list-item']}
                      onClick={() => navigate('prompt', selectedItem.prompt.id)}
                    >
                      프롬프트: {formatDate(selectedItem.prompt.date, 'num')}
                    </button>
                  )}
                {(selectedItem.query || selectedItem.chat) && (
                  <button
                    className={styles['detail-footer-item-list-item']}
                    onClick={() =>
                      navigate(
                        'query',
                        selectedItem.query ? selectedItem.query.id : selectedItem.chat.id
                      )
                    }
                  >
                    파인콘:{' '}
                    {formatDate(
                      selectedItem.query ? selectedItem.query.date : selectedItem.chat.date,
                      true
                    )}
                  </button>
                )}
                {selectedItem.result &&
                  selectedItem.result.map((item) => (
                    <button
                      key={item.id}
                      className={styles['detail-footer-item-list-item']}
                      onClick={() => navigate('result', item.id)}
                    >
                      결과: {formatDate(item.date, 'num')}
                    </button>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
