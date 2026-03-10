import { useMemo, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { Chart } from 'chart.js'
import { AI_CATEGORY } from '@/utils/constants'

const AIREPORT_TYPE = { ranking: 'ranking', journey: 'journey', trend: 'trend', target: 'target' }
import { getChartData } from '@/utils/reportHelper.js'
import styles from './ReportInfoCategory.module.scss'

import iconAiSolomon from '@/assets/aireport/icon--aisolomon.svg'

export default function ReportInfoCategory({
  rawData,
  summary,
  reportHtml,
  onUpdateIdx
}) {
  const { t, i18n } = useTranslation()
  const locale = i18n.language
  const chartRef = useRef(null)
  const category2MaxLength = 160

  const info = useMemo(() => {
    if (!rawData) return null

    const category2 = rawData.category.AICategory2
    const category3 = rawData.category.AICategory3
    const domainCategory = rawData.info.domainCategory

    const display = {
      category: true,
      category1: true,
      category2to3Chart: rawData.info.type === AIREPORT_TYPE.ranking,
      category2to3Text: rawData.info.type !== AIREPORT_TYPE.ranking
    }

    if (AI_CATEGORY.primary[domainCategory]) {
      if (category2.length === 0 || category3.length === 0) {
        display.category2to3Chart = false
        display.category2to3Text = false
      }
    } else {
      if (category2.length === 0 || category3.length === 0) {
        display.category = false
        onUpdateIdx?.(0)
      } else {
        if (rawData.info.type === AIREPORT_TYPE.ranking) {
          display.category1 = false
        } else {
          display.category = false
          onUpdateIdx?.(0)
        }
      }
    }

    let infoData = {
      display,
      domainCategory: AI_CATEGORY.primary[domainCategory],
      category2Width: {},
      category3Top1: ''
    }

    let maxLength = category2MaxLength

    if (display.category && display.category2to3Chart) {
      const max = category2.reduce(
        (mx, obj) => (obj.value > mx ? obj.value : mx),
        category2[0].value
      )

      if (max > 100000) {
        maxLength = 146
      } else if (max > 10000) {
        maxLength = 154
      }

      const sum = category2.reduce((acc, obj) => acc + obj.value, 0)

      category2.forEach((obj) => {
        obj.width = maxLength * (obj.value / max) + 'px'
        obj.ratio = ((obj.value / sum) * 100).toFixed(1)
        return obj
      })

      category2.sort((a, b) => b.value - a.value)

      infoData.category2Width = category2.reduce((acc, obj) => {
        acc[obj.name] = { value: obj.value.toLocaleString(), width: obj.width }
        return acc
      }, {})
    }

    if (category3.length > 0) {
      if (category3[0].name === 'etc' && category3.length > 1) {
        infoData.category3Top1 = category3[1].name
      } else {
        infoData.category3Top1 = category3[0].name
      }
    }

    return infoData
  }, [rawData, onUpdateIdx])

  useEffect(() => {
    if (rawData?.info?.type === AIREPORT_TYPE.ranking && chartRef.current) {
      const chartData = getChartData('categoryRadar', [rawData], {
        locale
      })
      const chart = new Chart(chartRef.current, chartData)
      return () => chart.destroy()
    }
  }, [rawData, locale])

  if (!rawData || !info) return null

  return (
    <div id="report-info-category" className={styles.reportInfoCategory}>
      <div className={styles.info}>
        {summary && (
          <div className={styles.insight}>
            <div className={styles.insightTitle}>
              <p>{t('aireport.common.insight')}</p>
              <div className={styles.insightTitleSub}>
                {t('aireport.common.insightSub')}
              </div>
            </div>
            <p className={styles.insightText}>"{summary}"</p>
          </div>
        )}
        {reportHtml && (
          <div>
            <div className={styles.reportDevider}>
              <img alt="robot icon" src={iconAiSolomon} />
              <span className={styles.reportDeviderLine} />
            </div>
            <h1 className={styles.reportGptTitle}>
              {t('aireport.common.gptReportTitle')}
            </h1>
            <div
              id="gptReport"
              className={styles.gptReport}
              dangerouslySetInnerHTML={{ __html: reportHtml }}
            />
          </div>
        )}
        {info.display.category && (
          <div className={styles.section}>
            <p className={styles.sectionTitle}>
              1. *.{rawData.info.domain} {t('aireport.common.category.title')}
            </p>
            <div className={styles.sectionBody}>
              {info.display.category1 && info.domainCategory && (
                <div className={styles.category1}>
                  <i
                    className={`${styles.category1Icon} icon-primary-${rawData.info.domainCategory}`}
                  />
                  <div className={styles.category1Info}>
                    <p className={styles.category1InfoTitle}>
                      {info.domainCategory.title[locale]}
                    </p>
                    <p className={styles.category1InfoDescription}>
                      {info.domainCategory.description[locale]}
                    </p>
                  </div>
                </div>
              )}
              {info.display.category2to3Chart && (
                <div className={styles.categoryAnalysis}>
                  <div className={styles.categoryAnalysisSection}>
                    <div className={styles.pageStructure}>
                      <div className={styles.categoryAnalysisSectionTitle}>
                        <p>{t('aireport.common.category.category2Title')}</p>
                        {rawData.category.target === 'CATEGORY' && (
                          <span className={styles.averageLabel}>
                            {t('aireport.common.category.industryAverage')}
                          </span>
                        )}
                      </div>
                      {AI_CATEGORY.secondaryGroup.map((group, groupIdx) => (
                        <div className={styles.pages} key={groupIdx}>
                          <p
                            className={styles.pagesGroupTitle}
                            style={{
                              fontSize: locale === 'en' ? '12px' : '15px',
                              writingMode:
                                locale === 'en' ? 'inherit' : 'vertical-lr'
                            }}
                          >
                            {group.title[locale]}
                          </p>
                          <div className={styles.pagesGroupCategories}>
                            {group.children.map((cat2) => (
                              <div
                                className={styles.pagesGroupCategoriesItem}
                                key={cat2}
                              >
                                <div
                                  className={
                                    styles.pagesGroupCategoriesItemTitle
                                  }
                                >
                                  <p>
                                    {AI_CATEGORY.secondary[cat2]?.title[locale]}
                                  </p>
                                  <div className={styles.padding} />
                                </div>
                                <div
                                  className={styles.pagesGroupCategoriesItemBar}
                                  style={{
                                    backgroundColor:
                                      AI_CATEGORY.secondary[cat2]?.color,
                                    width:
                                      info.category2Width[cat2]?.width || '0px'
                                  }}
                                />
                                <p
                                  className={
                                    styles.pagesGroupCategoriesItemValue
                                  }
                                >
                                  {info.category2Width[cat2]?.value}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                    {rawData.category.AICategory2[0] && (
                      <div className={styles.categoryDetail}>
                        <div className={styles.categoryDetailTitle}>
                          <i
                            className={`${styles.categoryDetailTitleIcon} icon-${rawData.category.AICategory2[0].name}`}
                          />
                          <p className={styles.categoryDetailTitleText}>
                            {
                              AI_CATEGORY.secondary[
                                rawData.category.AICategory2[0].name
                              ]?.title[locale]
                            }{' '}
                            ({rawData.category.AICategory2[0].ratio}%)
                          </p>
                        </div>
                        <p className={styles.categoryDetailDescription}>
                          {
                            AI_CATEGORY.secondary[
                              rawData.category.AICategory2[0].name
                            ]?.description[locale]
                          }
                        </p>
                      </div>
                    )}
                    {rawData.category.AICategory2[1] && (
                      <div className={styles.categoryDetail}>
                        <div className={styles.categoryDetailTitle}>
                          <i
                            className={`${styles.categoryDetailTitleIcon} icon-${rawData.category.AICategory2[1].name}`}
                          />
                          <p className={styles.categoryDetailTitleText}>
                            {
                              AI_CATEGORY.secondary[
                                rawData.category.AICategory2[1].name
                              ]?.title[locale]
                            }{' '}
                            ({rawData.category.AICategory2[1].ratio}%)
                          </p>
                        </div>
                        <p className={styles.categoryDetailDescription}>
                          {
                            AI_CATEGORY.secondary[
                              rawData.category.AICategory2[1].name
                            ]?.description[locale]
                          }
                        </p>
                      </div>
                    )}
                  </div>
                  <div className={styles.categoryAnalysisSection}>
                    <div>
                      <div className={styles.categoryAnalysisSectionTitle}>
                        <p>{t('aireport.common.category.category3Title')}</p>
                        {rawData.category.target === 'CATEGORY' && (
                          <span className={styles.averageLabel}>
                            {t('aireport.common.category.industryAverage')}
                          </span>
                        )}
                      </div>
                      <canvas
                        id="categoryRadar"
                        className={`${styles.category3Chart} draggable`}
                        ref={chartRef}
                        draggable="true"
                      />
                    </div>
                    {info.category3Top1 && AI_CATEGORY.tertiary[info.category3Top1] && (
                      <div className={styles.categoryDetail}>
                        <div className={styles.categoryDetailTitle}>
                          <i
                            className={`${styles.categoryDetailTitleIcon} icon-tertiary-${info.category3Top1}`}
                          />
                          <p className={styles.categoryDetailTitleText}>
                            {
                              AI_CATEGORY.tertiary[info.category3Top1].title[
                                locale
                              ]
                            }
                          </p>
                        </div>
                        <div className={styles.categoryDetailList}>
                          {AI_CATEGORY.tertiary[info.category3Top1].descriptions[
                            locale
                          ]?.map((content, idx) => (
                            <p
                              className={styles.categoryDetailDescription}
                              key={idx}
                            >
                              {content}
                            </p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
              {info.display.category2to3Text &&
                !info.display.category2to3Chart &&
                rawData.category.AICategory2[0] &&
                info.category3Top1 &&
                AI_CATEGORY.tertiary[info.category3Top1] && (
                  <p>
                    {t('aireport.common.category.longGuide', {
                      domain: rawData.info.domain,
                      category2:
                        AI_CATEGORY.secondary[
                          rawData.category.AICategory2[0].name
                        ]?.title[locale],
                      category3:
                        AI_CATEGORY.tertiary[info.category3Top1].title[locale],
                      category2Description:
                        AI_CATEGORY.secondary[
                          rawData.category.AICategory2[0].name
                        ]?.description[locale]
                    })}
                    {AI_CATEGORY.tertiary[info.category3Top1].descriptions[
                      locale
                    ]?.map((content, index) => (
                      <span key={index}>
                        {t(`aireport.common.listIdx[${index}]`)}, {content}{' '}
                      </span>
                    ))}
                  </p>
                )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
