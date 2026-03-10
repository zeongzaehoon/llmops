import { useMemo, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { capitalizeFirstLetter } from '@/utils/utils.js'
import styles from './ReportInfoTable.module.scss'

import iconChevronDown from '@/assets/icon--chevronDown.svg'

export default function ReportInfoTable({ basicInfo, reportDataArr }) {
  const { t } = useTranslation()

  const thead = [
    'type',
    'domain',
    'firstPath',
    'date',
    'device',
    'marketing',
    'refer',
    'exist',
    'session',
    'pv'
  ]
  const { infoIdx, isMashup } = basicInfo

  const infoArr = useMemo(() => {
    if (!reportDataArr) return []
    return reportDataArr.map((reportData) => {
      const rawData = reportData.rawData

      const timeDiff =
        new Date(rawData.info.endDate) - new Date(rawData.info.startDate)
      const dayDiff = timeDiff / (1000 * 60 * 60 * 24)
      const totalPv = rawData.info.totalPvCount
      const avgPv = Number((totalPv / (dayDiff + 1)).toFixed(1)).toLocaleString()
      const totalSession = rawData.info.totalSessionCount
      const avgSession = Number(
        (totalSession / (dayDiff + 1)).toFixed(1)
      ).toLocaleString()

      const type = capitalizeFirstLetter(rawData.info.type)
      const domain = rawData.info.subDomain
        ? rawData.info.subDomain
        : `*.${rawData.info.domain}`
      const firstPath = rawData.info.firstPath ? rawData.info.firstPath : '-'
      const date = `${rawData.info.startDate} ~ ${rawData.info.endDate}`
      const device = rawData.info.device
        ? capitalizeFirstLetter(rawData.info.device)
        : 'All'
      const refer = rawData.info.refer ? rawData.info.refer : 'All'
      const exist =
        rawData.info.exist === 'All'
          ? rawData.info.exist
          : rawData.info.exist
            ? 'Return'
            : 'New'
      const pv = `${totalPv.toLocaleString()} (${avgPv} PVs / 1day)`
      const session = `${totalSession.toLocaleString()} (${avgSession}Sessions / 1day)`

      let marketing = {}

      if (rawData.info.utm && rawData.info.utm !== 'All') {
        marketing['title'] = 'UTM Parameter'
        marketing['list'] = Object.entries(rawData.info.utm).map(
          ([key, value]) => {
            let utmValue = 'All'
            if (Array.isArray(value)) {
              utmValue = value.join(', ')
            } else {
              utmValue = value
            }
            return { title: key, value: utmValue }
          }
        )
      } else if (rawData.info.survey && rawData.info.survey !== 'All') {
        marketing['title'] = 'Survey'
        marketing['target'] = rawData.info.survey.noTarget
          ? t('aireport.common.infoTable.survey.noTarget')
          : t('aireport.common.infoTable.survey.target')
        marketing['answer'] = rawData.info.survey.noAnswer
          ? t('aireport.common.infoTable.survey.noAnswer')
          : t('aireport.common.infoTable.survey.answer')

        marketing['list'] = Object.entries(
          rawData.info.survey.answerOptions
        ).map(([key, value]) => {
          let subList = []
          if (value.questionType === 'checkbox') {
            reportData.survey?.answerOptions?.[key]?.forEach((answerIdx) => {
              if (answerIdx === 'None') {
                subList.push(t('aireport.common.infoTable.survey.etc'))
              } else {
                subList.push(value.answerOptions[answerIdx])
              }
            })
          } else if (value.questionType === 'range') {
            subList.push(
              reportData.survey?.answerOptions?.[key]?.join(', ') || ''
            )
          }
          return { title: value.question, subList }
        })
      } else {
        marketing = null
      }

      return {
        type,
        domain,
        firstPath,
        date,
        device,
        marketing,
        refer,
        exist,
        pv,
        session,
        totalPv,
        avgPv,
        totalSession,
        avgSession
      }
    })
  }, [reportDataArr, t])

  const rowList = useMemo(() => {
    return thead.filter((row) => {
      return infoArr.some((info) => info[row] !== '-')
    })
  }, [infoArr])

  const getDiff = useCallback(
    (field) => {
      if (!reportDataArr || reportDataArr.length < 2) return true

      const rawDataArr = reportDataArr.map((r) => r.rawData)

      if (field === 'date') {
        return rawDataArr.every(
          (r) =>
            r.info.startDate === rawDataArr[0].info.startDate &&
            r.info.endDate === rawDataArr[0].info.endDate
        )
      } else if (field === 'domain') {
        return rawDataArr.every(
          (r) =>
            r.info.domain === rawDataArr[0].info.domain &&
            r.info.subDomain === rawDataArr[0].info.subDomain
        )
      } else if (field === 'marketing') {
        const utmArr = reportDataArr.map((r) => r.utm)
        const utmStrArr = utmArr.map((utm) => {
          let result = ''
          for (let key in utm) {
            result += key + JSON.stringify(utm[key])
          }
          return result
        })

        const surveyArr = reportDataArr.map((r) => r.survey)
        const surveyStrArr = surveyArr.map((survey) => {
          let result = ''
          for (let key in survey) {
            result += key + JSON.stringify(survey[key])
          }
          return result
        })

        return (
          utmStrArr.every((s) => s === utmStrArr[0]) &&
          surveyStrArr.every((s) => s === surveyStrArr[0])
        )
      } else if (field === 'session') {
        return infoArr.every(
          (info) =>
            info.totalSession === infoArr[0].totalSession &&
            info.avgSession === infoArr[0].avgSession
        )
      } else if (field === 'pv') {
        return infoArr.every(
          (info) =>
            info.totalPv === infoArr[0].totalPv &&
            info.avgPv === infoArr[0].avgPv
        )
      } else {
        return rawDataArr.every(
          (r) => r.info[field] === rawDataArr[0].info[field]
        )
      }
    },
    [reportDataArr, infoArr]
  )

  const diffRow = useMemo(() => {
    return rowList.filter((row) => !getDiff(row))
  }, [rowList, getDiff])

  const pvGap = useMemo(() => {
    if (!reportDataArr || reportDataArr.length < 2) return '0'
    const max = reportDataArr.reduce(
      (acc, curr) =>
        curr.rawData.info.totalPvCount > acc
          ? curr.rawData.info.totalPvCount
          : acc,
      reportDataArr[0].rawData.info.totalPvCount
    )
    const min = reportDataArr.reduce(
      (acc, curr) =>
        curr.rawData.info.totalPvCount < acc
          ? curr.rawData.info.totalPvCount
          : acc,
      reportDataArr[0].rawData.info.totalPvCount
    )
    return Number((((max - min) / min) * 100).toFixed(1)).toLocaleString()
  }, [reportDataArr])

  const getMarketingIdx = (element) => {
    const idxClass = Array.from(element.classList).find((className) =>
      className.includes('marketingIdx')
    )
    return idxClass ? idxClass.split('_')[1] : null
  }

  useEffect(() => {
    const marketingContArr = document.querySelectorAll(
      `.${styles.marketing}`
    )
    const marketingBtnArr = document.querySelectorAll(
      `.${styles.marketingHeaderBtn}`
    )
    marketingBtnArr.forEach((btn) => {
      const btnIdx = getMarketingIdx(btn)
      const marketingCont = Array.from(marketingContArr).find(
        (el) => getMarketingIdx(el) === btnIdx
      )
      if (marketingCont) {
        const handler = () => {
          marketingCont.classList.toggle(styles.opened)
        }
        btn.addEventListener('click', handler)
      }
    })
  }, [reportDataArr])

  if (!reportDataArr) return null

  return (
    <div id="report-info-table" className={styles.reportInfoTable}>
      <div className={styles.info}>
        <div className={styles.section}>
          <p className={styles.sectionTitle}>
            {infoIdx + 1}. {t('aireport.common.infoTable.title')}
          </p>
          <div className={styles.sectionBody}>
            {isMashup && (
              <p className={styles.sectionBodyText}>
                {t('aireport.common.infoTable.description', {
                  diffCount: diffRow.length,
                  diffSegments: diffRow
                    .map((row) => t(`aireport.common.infoTable.thead.${row}`))
                    .join(', '),
                  pvGap
                })}
              </p>
            )}
            <table className={styles.reportInfoTableEl}>
              {reportDataArr.length > 1 && (
                <thead>
                  <tr>
                    <th />
                    {Array(reportDataArr.length)
                      .fill(null)
                      .map((_, index) => (
                        <td key={index}>Data {index + 1}</td>
                      ))}
                  </tr>
                </thead>
              )}
              <tbody>
                {rowList.map((thItem) => (
                  <tr key={thItem}>
                    <th
                      style={{
                        width:
                          reportDataArr.length === 1 ? '25%' : '17%',
                        whiteSpace:
                          reportDataArr.length > 1 ? 'pre-line' : 'inherit'
                      }}
                    >
                      {t(`aireport.common.infoTable.thead.${thItem}`)}
                    </th>
                    {reportDataArr.map((_, idx) => (
                      <td
                        key={idx}
                        style={{
                          width:
                            reportDataArr.length === 1
                              ? 'auto'
                              : `calc(83% / ${reportDataArr.length})`
                        }}
                      >
                        {thItem === 'marketing' ? (
                          <div
                            className={`${styles.marketing} marketingIdx_${idx}`}
                          >
                            {infoArr[idx]?.[thItem] ? (
                              <div>
                                <div className={styles.marketingHeader}>
                                  <p
                                    className={`${styles.marketingHeaderTitle} ${diffRow.indexOf(thItem) !== -1 ? styles.diff : ''}`}
                                  >
                                    {infoArr[idx][thItem].title}
                                  </p>
                                  <button
                                    className={`${styles.marketingHeaderBtn} marketingIdx_${idx}`}
                                  >
                                    <img
                                      src={iconChevronDown}
                                      alt="chevronButton"
                                    />
                                  </button>
                                </div>
                                <div className={styles.marketingBody}>
                                  {infoArr[idx].marketing?.target && (
                                    <p>{infoArr[idx].marketing.target}</p>
                                  )}
                                  {infoArr[idx].marketing?.answer && (
                                    <p>{infoArr[idx].marketing.answer}</p>
                                  )}
                                  <ul>
                                    {infoArr[idx][thItem].list.map(
                                      (item, itemIdx) => (
                                        <li key={itemIdx}>
                                          <p>{item.title}:</p>
                                          {item.subList ? (
                                            <ul>
                                              {item.subList.map(
                                                (answer, aIdx) => (
                                                  <li key={aIdx}>
                                                    <span>{answer}</span>
                                                  </li>
                                                )
                                              )}
                                            </ul>
                                          ) : (
                                            <span>{item.value}</span>
                                          )}
                                        </li>
                                      )
                                    )}
                                  </ul>
                                </div>
                              </div>
                            ) : (
                              <span
                                className={
                                  diffRow.indexOf(thItem) !== -1
                                    ? styles.diff
                                    : ''
                                }
                              >
                                All
                              </span>
                            )}
                          </div>
                        ) : (
                          <span
                            className={
                              diffRow.indexOf(thItem) !== -1
                                ? styles.diff
                                : ''
                            }
                          >
                            {infoArr[idx]?.[thItem]}
                          </span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
