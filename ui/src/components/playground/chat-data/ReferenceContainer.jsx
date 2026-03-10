import { useState, useMemo, useRef } from 'react'
import { useStore } from '@/store'
import { unescape, formatDate } from '@/utils/parse'
import { getReference } from '@/api/adminApi'
import { refresh } from '@/api/connectApi'
import BaseButton from '@/components/playground/common/BaseButton'

import styles from './ReferenceContainer.module.scss'

import iconLoading from '@/assets/icon--loading-animated.svg'
import iconTrashcan from '@/assets/icon--trashcan.svg'
import iconChevronLeft from '@/assets/icon--chevronLeft.svg'
import iconEmpty from '@/assets/icon--empty.svg'

const ReferenceContainer = ({ agent }) => {
  const store = useStore()
  const referenceList = useMemo(() => store.state.referenceList[agent], [store.state.referenceList, agent])
  const [selectedIndex, setSelectedIndex] = useState(undefined)
  const [searchText, setSearchText] = useState('')
  const [prompt, setPrompt] = useState('')
  const scrollerRef = useRef(null)
  const [isSearchLoading, setIsSearchLoading] = useState(false)

  const handleOpenDetail = (item, index) => {
    if (selectedIndex === index) {
      setSelectedIndex(null)
    } else {
      setSelectedIndex(index)
    }
  }

  const handleDeleteReference = (event, reversedIndex) => {
    if (selectedIndex === reversedIndex) {
      setSelectedIndex(null)
    }
    let newReferenceList = referenceList
    const index = newReferenceList.length - reversedIndex - 1
    newReferenceList = [...newReferenceList.slice(0, index), ...newReferenceList.slice(index + 1)]
    store.dispatch('changeReferenceList', {
      agent,
      referenceList: newReferenceList
    })
  }

  const setReferenceItem = () => {
    setIsSearchLoading(true)
    setPrompt(searchText)

    const data = {
      agent,
      prompt: searchText
    }

    scrollToTop()

    getReference(agent, data)
      .then((res) => {
        const reference = {
          question: searchText,
          reference: res.data.data.refer,
          answer: '...',
          created: new Date()
        }
        setSelectedIndex(null)
        store.dispatch('insertReferenceItem', { agent, reference })
      })
      .catch((e) => {
        if (e.response.status === 401) {
          refresh(agent)
          alert('세션이 연장되었습니다. 다시 검색해주세요.')
        }
        console.log(e)
      })
      .finally(() => {
        setIsSearchLoading(false)
      })
    setSearchText('')
  }

  const handleClickInsert = () => {
    if (searchText.length === 0) {
      alert('검색 프롬프트를 입력해주세요.')
      return
    }

    setReferenceItem()
  }

  const scrollToTop = () => {
    if (!scrollerRef.current) return

    scrollerRef.current.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }

  return (
    <div className={styles['reference-container']}>
      <p className={styles['container-header']}>참고 데이터</p>
      <div className={styles['container-body']}>
        {(referenceList && referenceList.length > 0) || isSearchLoading ? (
          <div className={styles['reference-list-wrapper']}>
            <div
              className={styles['reference-list-loading']}
              style={{ display: isSearchLoading ? undefined : 'none' }}
            >
              <img src={iconLoading} alt="loading" />
            </div>
            {referenceList && referenceList.length > 0 && (
              <div className={styles['reference-list']} ref={scrollerRef}>
                {referenceList.slice().reverse().map((item, index) => (
                  <div
                    className={[
                      styles['reference-item'],
                      index === selectedIndex ? styles.selected : ''
                    ].filter(Boolean).join(' ')}
                    key={index}
                  >
                    <div className={styles['reference-item-header']}>
                      <p><span>Q. </span>{item.question}</p>
                      <button
                        className={styles['delete-button']}
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteReference(e, index)
                        }}
                      >
                        <img src={iconTrashcan} alt="delete" />
                      </button>
                    </div>
                    <div className={styles['reference-item-body']}>
                      <div className={styles['reference-body-field']}>
                        <span>Date: </span>
                        <p>{formatDate(item.created)}</p>
                      </div>
                      {index === selectedIndex ? (
                        <div className={styles['reference-body-field']}>
                          <span className={styles['long-text-title']}>Reference: </span>
                          {item.reference.map((refer, refIndex) => (
                            <div className={styles['reference-item-list']} key={refIndex}>
                              <p className={styles['reference-subject']}>
                                {refIndex + 1}. {refer.subject}
                              </p>
                              <p className={styles['reference-source']}>
                                - 출처: {refer.agent}
                              </p>
                              <p className={styles['reference-url']}>
                                - URL: <a href={refer.url} target="blank">{refer.url}</a>
                              </p>
                              <p className={styles['text-content']}>
                                {unescape(refer.content.trim())}
                              </p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className={styles['reference-body-field']}>
                          <span className={styles['long-text-title']}>Reference: </span>
                          <p>{item.reference[0].subject}...</p>
                        </div>
                      )}
                    </div>
                    <div
                      className={styles['item-fold-button']}
                      onClick={() => handleOpenDetail(item, index)}
                    >
                      <img src={iconChevronLeft} alt="fold reference item" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className={styles['empty-container']}>
            <img src={iconEmpty} alt="empty icon" />
            <p>저장된 참고 데이터가 없습니다.</p>
          </div>
        )}
      </div>
      <div className={styles.search}>
        <input
          id="reference-search-input"
          className={styles['search-input']}
          type="text"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          placeholder="참고 데이터 검색어를 입력해주세요."
          onKeyDown={(e) => { if (e.key === 'Enter') handleClickInsert() }}
          autoComplete="off"
        />
        <BaseButton size="medium" onClick={handleClickInsert}>검색</BaseButton>
      </div>
    </div>
  )
}

export default ReferenceContainer
