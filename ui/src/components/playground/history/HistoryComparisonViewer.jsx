import { useState, useMemo, useCallback } from 'react'
import DiffMatchPatch from 'diff-match-patch'
import { convertMarkdownToHtml } from '@/utils/parse'
import { formatDate } from '@/utils/parse'
import { HISTORY_TAB, VERSION_SELECTED, VERSION_COMPARED } from '@/utils/constants'
import { updateMemo, downloadQuestion } from '@/api/adminApi'
import BaseButton from '@/components/playground/common/BaseButton'
import styles from './HistoryComparisonViewer.module.scss'

export default function HistoryComparisonViewer({
  tab,
  agent,
  selectedItem,
  comparisonItem,
  onNavigate,
  onReload
}) {
  const [isEditMode, setIsEditMode] = useState({
    [VERSION_SELECTED]: false,
    [VERSION_COMPARED]: false
  })
  const [newMemo, setNewMemo] = useState({
    [VERSION_SELECTED]: '',
    [VERSION_COMPARED]: ''
  })
  const [isTooltipVisible, setIsTooltipVisible] = useState(false)

  const dmp = useMemo(() => new DiffMatchPatch(), [])

  const getMainContent = useCallback(
    (item, markdown = false) => {
      let content
      if (tab === 'result') {
        content = item?.message || ''
      } else {
        content = item?.prompt || ''
      }
      if (markdown) {
        return convertMarkdownToHtml(content)
      } else {
        return content
      }
    },
    [tab]
  )

  const diff = useMemo(() => {
    if (!selectedItem || !comparisonItem) return []
    const selectedContent = getMainContent(selectedItem)
    const comparisonContent = getMainContent(comparisonItem)
    const diffMain = dmp.diff_main(selectedContent, comparisonContent)
    dmp.diff_cleanupEfficiency(diffMain)
    return diffMain
  }, [selectedItem, comparisonItem, dmp, getMainContent])

  const diffStyles = useMemo(
    () => ({
      added: 'background: #9eff9e7d; text-decoration: underline',
      removed: 'background: #ffa6a687; text-decoration: line-through;'
    }),
    []
  )

  const getDiffHtml = useCallback(
    (diffData) => {
      let diffHtml = ''
      for (const group of diffData) {
        const key = group[0]
        let value = group[1]
        if ((key === -1 || key === 1) && !/\S/.test(value)) {
          const linebreaks = value.match(/(\S)*(\r\n|\r|\n)/g)
          if (linebreaks) {
            if (key === -1) value = '\u00b6'.repeat(linebreaks.length)
            if (key === 1) value = '\u00b6\n'.repeat(linebreaks.length)
          }
        }
        let nodeStyles = ''
        if (key === 1) nodeStyles = diffStyles.added
        if (key === -1) nodeStyles = diffStyles.removed
        diffHtml += `<span style='${nodeStyles}'>${value}</span>`
      }
      return diffHtml
    },
    [diffStyles]
  )

  const handleChangeEditMode = useCallback(
    (kind) => {
      setIsEditMode((prev) => {
        const next = { ...prev, [kind]: !prev[kind] }
        if (!prev[kind]) {
          // entering edit mode
          setNewMemo((prevMemo) => ({
            ...prevMemo,
            [kind]:
              kind === VERSION_SELECTED
                ? selectedItem?.memo || ''
                : comparisonItem?.memo || ''
          }))
        } else {
          // leaving edit mode
          setNewMemo((prevMemo) => ({ ...prevMemo, [kind]: '' }))
        }
        return next
      })
    },
    [selectedItem, comparisonItem]
  )

  const handleClickSaveMemo = useCallback(
    (kind) => {
      const versionId =
        kind === VERSION_SELECTED ? selectedItem?.id : comparisonItem?.id
      const data = {
        id: versionId,
        kind: tab,
        memo: newMemo[kind],
        agent
      }

      updateMemo(data)
        .then((res) => {
          console.log(res)
          onReload?.(tab, versionId, kind === VERSION_COMPARED)
          alert('메모 업데이트 완료')
        })
        .catch((e) => {
          console.log(e)
          alert('메모 업데이트에 실패했습니다.')
        })
        .finally(() => {
          handleChangeEditMode(kind)
        })
    },
    [
      selectedItem,
      comparisonItem,
      tab,
      newMemo,
      agent,
      onReload,
      handleChangeEditMode
    ]
  )

  const navigate = useCallback(
    (navTab, id, type = null) => {
      onNavigate?.(navTab, id, type)
    },
    [onNavigate]
  )

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

  const footerItems = useMemo(
    () => [
      { kind: VERSION_SELECTED, ...selectedItem },
      { kind: VERSION_COMPARED, ...comparisonItem }
    ],
    [selectedItem, comparisonItem]
  )

  if (!selectedItem) return null

  return (
    <div className={styles.detail}>
      <div className={styles['detail-header']}>
        <p>
          {HISTORY_TAB[tab]}: {selectedItem.title} &amp; {comparisonItem?.title}
        </p>
        <div
          className={styles['detail-header-legend']}
          onMouseOver={() => setIsTooltipVisible(true)}
          onMouseOut={() => setIsTooltipVisible(false)}
        >
          {isTooltipVisible && (
            <div className={styles['detail-header-legend-tooltip']}>
              <div className={styles['detail-header-legend-tooltip-triangle']} />
              <div className={styles['detail-header-legend-tooltip-content']}>
                <span className={styles.add}>이 줄이 추가되었습니다.</span>
                <span className={styles.delete}>이 줄이 삭제되었습니다.</span>
              </div>
            </div>
          )}
          범례 보기
        </div>
      </div>
      <div className={styles['detail-body']}>
        {(selectedItem.notfound || comparisonItem?.notfound) && (
          <p>해당하는 데이터를 찾을 수 없습니다.</p>
        )}
        <div dangerouslySetInnerHTML={{ __html: getDiffHtml(diff) }} />
      </div>
      <div className={styles['detail-footer']}>
        {footerItems.map((item, index) => (
          <div
            key={item.id || index}
            className={styles['detail-footer-section']}
          >
            <div className={styles['detail-footer-section-item']}>
              <span className={styles['detail-footer-section-item-label']}>
                Comment:
              </span>
              <div className={styles['flex-col']}>
                {isEditMode[item.kind] ? (
                  <div className={styles['detail-footer-section-item-textarea']}>
                    <textarea
                      cols="30"
                      rows="10"
                      value={newMemo[item.kind]}
                      onChange={(e) =>
                        setNewMemo((prev) => ({
                          ...prev,
                          [item.kind]: e.target.value
                        }))
                      }
                    />
                  </div>
                ) : (
                  item.memo && (
                    <div className={styles['detail-footer-section-item-content']}>
                      {item.memo}
                    </div>
                  )
                )}
                <div className={styles.buttons}>
                  <BaseButton
                    color={isEditMode[item.kind] ? 'light' : 'primary'}
                    onClick={() => handleChangeEditMode(item.kind)}
                  >
                    {isEditMode[item.kind] ? '취소' : '수정'}
                  </BaseButton>
                  {isEditMode[item.kind] && (
                    <BaseButton onClick={() => handleClickSaveMemo(item.kind)}>
                      저장
                    </BaseButton>
                  )}
                </div>
              </div>
            </div>
            {tab === 'result' && (
              <div className={styles['detail-footer-section-item']}>
                <span className={styles['detail-footer-section-item-label']}>
                  Files:
                </span>
                <div className={styles['detail-footer-section-item-list']}>
                  {item.chat && (
                    <button
                      className={styles['detail-footer-section-item-list-item']}
                      onClick={() => handleClickDownloadQuestion(item.chat.id)}
                    >
                      {item.chat.filename}
                    </button>
                  )}
                </div>
              </div>
            )}
            <div className={styles['detail-footer-section-item']}>
              <span className={styles['detail-footer-section-item-label']}>
                Links:
              </span>
              <div className={styles['detail-footer-section-item-list']}>
                {Array.isArray(item.prompt) &&
                  item.prompt.map((prompt) => (
                    <button
                      key={prompt.id}
                      className={styles['detail-footer-section-item-list-item']}
                      onClick={() => navigate('prompt', prompt.id)}
                    >
                      프롬프트: {prompt.roleName} - {prompt.order} -{' '}
                      {formatDate(prompt.date, 'num')}
                    </button>
                  ))}
                {item.prompt && !Array.isArray(item.prompt) && item.prompt.id && (
                  <button
                    className={styles['detail-footer-section-item-list-item']}
                    onClick={() => navigate('prompt', item.prompt.id)}
                  >
                    프롬프트: {formatDate(item.prompt.date, 'num')}
                  </button>
                )}
                {(item.query || item.chat) && (
                  <button
                    className={styles['detail-footer-section-item-list-item']}
                    onClick={() =>
                      navigate(
                        'query',
                        item.query ? item.query.id : item.chat.id
                      )
                    }
                  >
                    파인콘:{' '}
                    {formatDate(
                      item.query ? item.query.date : item.chat.date,
                      'num'
                    )}
                  </button>
                )}
                {item.result &&
                  item.result.map((result) => (
                    <button
                      key={result.id}
                      className={styles['detail-footer-section-item-list-item']}
                      onClick={() =>
                        navigate('result', result.id)
                      }
                    >
                      결과: {formatDate(result.date, 'num')}
                    </button>
                  ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
