import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { formatDate } from '@/utils/parse'
import { HISTORY_TAB, COMPARE_SINGLE, COMPARE_DUAL } from '@/utils/constants'
import { getPromptList, getPrompt } from '@/api/adminApi'
import ChatHeader from '@/components/playground/chat/ChatHeader'
import HistoryViewer from './HistoryViewer'
import HistoryComparisonViewer from './HistoryComparisonViewer'
import emptyIcon from '@/assets/icon--empty.svg'
import loadingIcon from '@/assets/icon--loading-animated.svg'
import styles from './HistoryContainer.module.scss'

export default function HistoryContainer({ agent }) {
  const [searchParams] = useSearchParams()
  const tabList = useMemo(() => Object.keys(HISTORY_TAB), [])
  const [selectedTab, setSelectedTab] = useState(null)
  const [selectedItem, setSelectedItem] = useState(null)
  const [comparisonItem, setComparisonItem] = useState(null)
  const [versionList, setVersionList] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [compareOption, setCompareOption] = useState(1)

  const selectedTabRef = useRef(selectedTab)
  const initialized = useRef(false)

  useEffect(() => {
    selectedTabRef.current = selectedTab
  }, [selectedTab])

  const isGroupList = useMemo(
    () => versionList && versionList.length > 0 && 'groupId' in versionList[0],
    [versionList]
  )

  const getPromptVersionList = useCallback(
    async (kind) => {
      try {
        const data = { agent, kind }
        const res = await getPromptList(data)
        const result = res.data.data
        setVersionList(result)
        return result
      } catch (e) {
        console.log(e)
      }
    },
    [agent]
  )

  const getTitle = useCallback(
    (version, includeSymbol = false) => {
      let formatedTitle = formatDate(version.date, 'num')

      if (selectedTabRef.current !== 'result' && includeSymbol) {
        formatedTitle = (version.getResult ? '* ' : '- ') + formatedTitle
      }
      if ('order' in version) {
        formatedTitle = formatedTitle + ' - ' + version.order
      }

      return formatedTitle
    },
    []
  )

  const getPromptById = useCallback(
    async (kind, id) => {
      const data = { agent, kind, id }
      try {
        const res = await getPrompt(data)
        console.log(res)
        return res.data.data
      } catch (e) {
        console.log(e)
      }
    },
    [agent]
  )

  const setCurrentVersion = useCallback(
    async (kind, id, isComparison = false) => {
      if (isComparison) {
        setComparisonItem({ id, loading: true })
        const item = await getPromptById(kind, id)
        if (!item) {
          setComparisonItem({ id, notfound: true })
          return
        }
        setComparisonItem({ title: getTitle(item), ...item })
      } else {
        setSelectedItem({ id, loading: true })
        const item = await getPromptById(kind, id)
        if (!item) {
          setSelectedItem({ id, notfound: true })
          return
        }
        setSelectedItem({ title: getTitle(item), ...item })
      }
    },
    [getPromptById, getTitle]
  )

  const handleChangeTab = useCallback(
    async (tab) => {
      if (selectedTabRef.current === tab) return
      setIsLoading(true)
      setVersionList(null)
      setSelectedItem(null)
      setComparisonItem(null)
      setSelectedTab(tab)
      selectedTabRef.current = tab

      const list = await getPromptVersionList(tab)

      if (!list || list.length === 0) {
        setIsLoading(false)
        return
      }

      const hasGroups = list.length > 0 && 'groupId' in list[0]

      if (hasGroups) {
        await setCurrentVersion(tab, list[0].versions[0].id)
      } else {
        await setCurrentVersion(tab, list[0].id)
      }
      setIsLoading(false)
    },
    [getPromptVersionList, setCurrentVersion]
  )

  const handleSelectItem = useCallback(
    (version) => {
      if (selectedItem && selectedItem.id === version.id) return
      if (comparisonItem) {
        setSelectedItem(null)
        setComparisonItem(null)
      }
      setCurrentVersion(selectedTabRef.current, version.id)
    },
    [selectedItem, comparisonItem, setCurrentVersion]
  )

  const handleSelectComparisonItem = useCallback(
    (version) => {
      if (comparisonItem && comparisonItem.id === version.id) {
        setComparisonItem(null)
      } else {
        setCompareOption(COMPARE_DUAL)
        setCurrentVersion(selectedTabRef.current, version.id, true)
      }
    },
    [comparisonItem, setCurrentVersion]
  )

  const navigateToSelectedItem = useCallback(
    (kind, id, type) => {
      window.open(
        `${location.origin}/admin/history/${agent}?type=${type}&kind=${kind}&id=${id}`
      )
    },
    [agent]
  )

  const handleSelectCompareOption = useCallback((option) => {
    setCompareOption(option)
  }, [])

  // Initialize on mount
  useEffect(() => {
    if (initialized.current) return
    initialized.current = true

    const savedKind = searchParams.get('kind')
    const savedId = searchParams.get('id')

    const init = async () => {
      if (savedKind && savedId) {
        setIsLoading(true)
        setSelectedTab(savedKind)
        selectedTabRef.current = savedKind

        await getPromptVersionList(savedKind)
        await setCurrentVersion(savedKind, savedId)
        setIsLoading(false)
      } else {
        handleChangeTab(tabList[0])
      }
    }

    init()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className={styles.history}>
      <ChatHeader agent="history" title="UX GPT" info={agent} />
      <div className={styles['history-cont']}>
        <div className={styles['history-cont-header']}>
          <div className={styles['history-cont-header-nav']}>
            <div className={styles.tablist}>
              {tabList.map((item) => (
                <div
                  key={item}
                  className={`${styles['tablist-item']} ${
                    selectedTab === item ? styles.selected : ''
                  }`}
                  onClick={() => handleChangeTab(item)}
                >
                  {HISTORY_TAB[item]}
                </div>
              ))}
            </div>
          </div>
          {comparisonItem && (
            <div className={styles['diff-option']}>
              <button
                className={compareOption === COMPARE_DUAL ? styles.selected : ''}
                onClick={() => handleSelectCompareOption(COMPARE_DUAL)}
              >
                2단
              </button>
              <button
                className={compareOption === COMPARE_SINGLE ? styles.selected : ''}
                onClick={() => handleSelectCompareOption(COMPARE_SINGLE)}
              >
                1단
              </button>
            </div>
          )}
        </div>
        <div className={styles['history-cont-body']}>
          <div className={styles.version}>
            {!isLoading ? (
              <div className={styles['version-list']}>
                {isGroupList ? (
                  <div>
                    {versionList &&
                      versionList.map((version) => (
                        <div key={version.groupId} className={styles['version-list-group']}>
                          <div className={styles['version-list-group-label']}>
                            {version.groupId}
                          </div>
                          <div className={styles['version-list-group-content']}>
                            {version.versions.map((prompt) => (
                              <div
                                key={prompt.id}
                                className={`${styles['version-item']} ${styles.small} ${
                                  selectedItem && prompt.id === selectedItem.id
                                    ? styles.selected
                                    : ''
                                } ${
                                  comparisonItem && prompt.id === comparisonItem.id
                                    ? styles.comparing
                                    : ''
                                }`}
                              >
                                <div
                                  className={styles['version-btn']}
                                  title={prompt.memo ? prompt.memo.slice(0, 50) : undefined}
                                  onClick={() => handleSelectItem(prompt)}
                                >
                                  {getTitle(prompt, true)}
                                </div>
                                <div
                                  className={styles['compare-btn']}
                                  onClick={() => handleSelectComparisonItem(prompt)}
                                >
                                  비교
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  <div>
                    {versionList &&
                      versionList.map((version) => (
                        <div
                          key={version.id}
                          className={`${styles['version-item']} ${
                            selectedItem && version.id === selectedItem.id
                              ? styles.selected
                              : ''
                          } ${
                            comparisonItem && version.id === comparisonItem.id
                              ? styles.comparing
                              : ''
                          }`}
                        >
                          {selectedTab === 'refer' ? (
                            <div
                              className={styles['version-btn']}
                              onClick={() => handleSelectItem(version)}
                            >
                              {version.id}
                            </div>
                          ) : (
                            <div
                              className={styles['version-btn']}
                              title={version.memo ? version.memo.slice(0, 50) : undefined}
                              onClick={() => handleSelectItem(version)}
                            >
                              {getTitle(version, true)}
                            </div>
                          )}
                          <div
                            className={styles['compare-btn']}
                            onClick={() => handleSelectComparisonItem(version)}
                          >
                            비교
                          </div>
                        </div>
                      ))}
                  </div>
                )}
                {(!versionList || versionList.length === 0) && (
                  <div className={styles['version-list-empty']}>
                    <img src={emptyIcon} alt="empty icon" />
                    <p>데이터가 없습니다.</p>
                  </div>
                )}
              </div>
            ) : (
              <div className={styles['version-loading']}>
                <img src={loadingIcon} alt="loading" />
              </div>
            )}
          </div>
          <div className={styles['viewer-wrapper']}>
            {(!comparisonItem || compareOption !== COMPARE_SINGLE) && (
              <HistoryViewer
                tab={selectedTab}
                selectedItem={selectedItem}
                agent={agent}
                isComparison={false}
                onNavigate={navigateToSelectedItem}
                onReload={setCurrentVersion}
              />
            )}
            {comparisonItem && compareOption === COMPARE_DUAL && (
              <HistoryViewer
                tab={selectedTab}
                agent={agent}
                selectedItem={comparisonItem}
                isComparison={true}
                onNavigate={navigateToSelectedItem}
                onReload={setCurrentVersion}
              />
            )}
            {comparisonItem && compareOption === COMPARE_SINGLE && (
              <HistoryComparisonViewer
                tab={selectedTab}
                agent={agent}
                selectedItem={selectedItem}
                comparisonItem={comparisonItem}
                onNavigate={navigateToSelectedItem}
                onReload={setCurrentVersion}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
