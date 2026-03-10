import { useMemo, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { useTranslation } from 'react-i18next'
import { getDialogData } from '@/utils/dialogMessages.js'
import UiButton from '@/components/aireport/ui/UiButton'
import styles from './UiModal.module.scss'

export default function UiModal({
  optionMsg,
  dialogType,
  customData,
  yesValue = true,
  noValue = false,
  dimmed = true,
  fixed = true,
  contentStyle,
  customLocale,
  onClose
}) {
  const { t, i18n } = useTranslation()
  const locale = customLocale || i18n.language

  const dialogData = useMemo(() => {
    if (customData) {
      return customData
    }
    const data = getDialogData(locale)
    return data[dialogType] || {}
  }, [customData, dialogType, locale])

  useEffect(() => {
    if (document.activeElement) {
      document.activeElement.blur()
    }
  }, [])

  const onCloseClick = (value) => {
    onClose?.(value)
  }

  const modalContent = (
    <div
      className={[
        styles.app_dialog,
        dimmed && styles.dimmed,
        fixed && styles.fixed
      ]
        .filter(Boolean)
        .join(' ')}
    >
      <div className={styles.dialog_content} style={contentStyle}>
        {dialogData.iconClass && (
          <span className={`${styles.icon} ${dialogData.iconClass}`} />
        )}
        {dialogData.title && (
          <p
            className={`${styles.title} ${dialogData.titleClass || ''}`}
            dangerouslySetInnerHTML={{ __html: dialogData.title }}
          />
        )}
        {dialogData.description && (
          <p
            className={styles.description}
            dangerouslySetInnerHTML={{ __html: dialogData.description }}
          />
        )}
        {!dialogData.description && optionMsg && (
          <p
            className={styles.description}
            dangerouslySetInnerHTML={{ __html: optionMsg }}
          />
        )}

        <p className={styles.action}>
          {dialogData.type === 'confirm' && (
            <>
              <UiButton onClick={() => onCloseClick(noValue)}>
                {t('common.cancel', { lng: locale })}
              </UiButton>
              <UiButton primary2 onClick={() => onCloseClick(yesValue)}>
                {t('common.confirm', { lng: locale })}
              </UiButton>
            </>
          )}
          {dialogData.type === 'alert' && (
            <UiButton onClick={() => onCloseClick(yesValue)}>
              {t('common.confirm', { lng: locale })}
            </UiButton>
          )}
        </p>
      </div>
    </div>
  )

  const modalRoot = document.getElementById('modals')
  if (modalRoot) {
    return createPortal(modalContent, modalRoot)
  }
  return modalContent
}
