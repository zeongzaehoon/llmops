import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { formatDate } from '@/utils/parse.js'
import { getCookieValue } from '@/utils/utils.js'
import styles from './ReportInfoHeader.module.scss'

import logoReport from '@/assets/aireport/logo--cx_report.svg'
import iconAi from '@/assets/aireport/icon--ai.svg'
import iconRobot from '@/assets/aireport/icon--report-robot.png'

export default function ReportInfoHeader({
  info,
  isPromptAdvanced = false,
  isEditMode = false,
  onButton,
  className
}) {
  const { t } = useTranslation()
  const serviceLocale = getCookieValue('locale')
  const titleRef = useRef(null)
  const [dynamicFontSize, setDynamicFontSize] = useState('36px')

  const adjustFontSize = () => {
    const titleElement = titleRef.current
    if (!titleElement) return
    const lineHeight = parseFloat(getComputedStyle(titleElement).lineHeight)
    const maxLines = 2
    const maxHeight = lineHeight * maxLines

    if (titleElement.scrollHeight > maxHeight) {
      setDynamicFontSize('28px')
    }
  }

  useEffect(() => {
    adjustFontSize()
  }, [])

  return (
    <div className={`${styles.infoHeader} ${className || ''}`}>
      <div className={styles.infoHeaderToolbar}>
        {info.isOwner && !isEditMode && (
          <button
            className={`${styles.editButton} tooltip`}
            disabled={!info.editable}
            onClick={() => onButton?.('edit')}
          >
            <i className="icon icon--edit-white" />
            {t('aireport.editor.button.edit', { lng: serviceLocale })}
          </button>
        )}
        <p className={styles.infoHeaderTopDate}>
          {formatDate(info.date, 'yyyy-mm-dd')}
        </p>
      </div>
      <div className={styles.infoHeaderTop}>
        <div className={styles.infoHeaderTopLogo}>
          <img src={logoReport} alt="cx report logo" />
          <img src={iconAi} alt="ai icon" />
        </div>
      </div>
      <div className={styles.infoHeaderType}>
        {info.type && <p>{info.type}</p>}
      </div>
      <div className={styles.infoHeaderTitle}>
        <p ref={titleRef} style={{ fontSize: dynamicFontSize }}>
          {info.title}
          {isPromptAdvanced && ' 2.0'}
          {info.version && (
            <span className={styles.version}> v.{info.version}</span>
          )}
        </p>
        <img className={styles.aiLogo} src={iconRobot} alt="robot icon" />
      </div>
    </div>
  )
}
