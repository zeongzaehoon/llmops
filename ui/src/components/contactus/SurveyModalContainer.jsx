import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getImageUrl } from '@/utils/parse'
import { updateSurveyResponse } from '@/api/chatApi'
import styles from './SurveyModalContainer.module.scss'

export default function SurveyModalContainer({ agent, reset, onClose }) {
  const { t } = useTranslation()
  const [emailTabActivated, setEmailTabActivated] = useState(false)
  const [email, setEmail] = useState('')
  const [isEmailValid, setIsEmailValid] = useState(true)
  const [sended, setSended] = useState(false)

  const validateEmail = (e) => {
    const text = e.target.value
    const isValid = String(text)
      .toLowerCase()
      .match(
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      )
    setIsEmailValid(!!isValid)
  }

  const checkSendAvailablity = () => {
    return isEmailValid && email.length !== 0
  }

  const postMessage = (event, msg) => {
    return window.parent.postMessage({ event, msg }, '*')
  }

  const handleClickSend = () => {
    updateSurveyResponse(agent, { email })
      .then(() => setSended(true))
      .catch(() => alert('이메일 주소 저장에 실패했습니다.'))
  }

  const closeSolomon = () => {
    postMessage('close')
    reset()
    onClose()
  }

  const handleChangeEmailTabActivated = () => {
    setEmailTabActivated((prev) => !prev)
  }

  const handleResetTab = () => {
    if (!emailTabActivated) return
    setEmail('')
    setIsEmailValid(true)
    setEmailTabActivated((prev) => !prev)
  }

  const handleEmailChange = (e) => {
    setEmail(e.target.value)
    validateEmail(e)
  }

  return (
    <div className={styles.surveyModalWrapper}>
      <div className={styles.surveyModal}>
        {sended ? (
          <div className={`${styles.surveyModalCont} ${styles.sended}`}>
            <div className={styles.surveyModalContImageContainer}>
              <img src={getImageUrl('icon--survey-done.svg')} alt="survey header icon" />
            </div>
            <div className={styles.surveyModalContTitle}>{t('survey.title.sended')}</div>
            <button className={styles.button} onClick={closeSolomon}>
              {t('survey.button.close')}
            </button>
          </div>
        ) : (
          <div className={styles.surveyModalCont}>
            <div className={styles.surveyModalContHeader}>
              <p>{t('survey.title.init')}</p>
            </div>
            <div
              className={`${styles.surveyModalContBody} ${emailTabActivated ? styles.expanded : ''}`}
            >
              <div className={styles.sectionLeft}>
                <p className={styles.sectionMaintext}>{t('survey.answer.yes')}</p>
                <p className={styles.sectionSubtext}>{t('survey.answer.needMoreInfo')}</p>
                {emailTabActivated ? (
                  <div className={styles.input}>
                    <div className={styles.inputWrapper}>
                      <input
                        type="text"
                        placeholder={t('survey.inputPlaceHolder')}
                        value={email}
                        onChange={handleEmailChange}
                      />
                      <button
                        className={`${styles.sendButton} ${!checkSendAvailablity() ? styles.disabled : ''}`}
                        disabled={!checkSendAvailablity()}
                        onClick={handleClickSend}
                      >
                        {t('survey.send')}
                      </button>
                    </div>
                    <div className={styles.inputError}>
                      {!isEmailValid && <p>{t('survey.inputError')}</p>}
                    </div>
                  </div>
                ) : (
                  <button className={styles.button} onClick={handleChangeEmailTabActivated}>
                    {t('survey.button.getMoreSupport')}
                  </button>
                )}
                <p
                  className={`${styles.sectionSubtext} ${styles.small}`}
                  dangerouslySetInnerHTML={{ __html: t('survey.confirmEmail') }}
                ></p>
              </div>
              <div className={styles.sectionRight} onClick={handleResetTab}>
                <p className={styles.sectionMaintext}>{t('survey.answer.no')}</p>
                <p className={styles.sectionSubtext}>{t('survey.answer.enoughInfo')}</p>
                <button className={`${styles.button} ${styles.highlight}`} onClick={closeSolomon}>
                  {t('survey.button.end')}
                </button>
                <p
                  className={`${styles.sectionSubtext} ${styles.small}`}
                  dangerouslySetInnerHTML={{ __html: t('survey.endConversation') }}
                ></p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
