import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { AGENT } from '@/utils/constants'
import iconChevronLeft from '@/assets/icon--chevronLeft.svg'
import iconSolomon from '@/assets/icon--solomon.svg'
import iconAiSolomon from '@/assets/icon--aisolomon.svg'
import iconCrown from '@/assets/icon--crown.svg'
import iconWrite from '@/assets/icon--write.svg'
import iconHistory from '@/assets/icon--history.svg'
import styles from './ChatHeader.module.scss'

export default function ChatHeader({ agent, title, info, onOpenSetting }) {
  const navigate = useNavigate()
  const [isTooltipVisible, setIsTooltipVisible] = useState(false)

  const isHistory = agent === 'history'

  const path = window.location.pathname
  const pathArr = path.split('/')
  const currentMenu = pathArr[pathArr.length - 2]

  const handleClickBackButton = () => {
    if (currentMenu === 'chat') {
      navigate('/admin')
    } else if (currentMenu === 'history') {
      navigate(path.replace('history', 'chat'))
    } else {
      navigate(-1)
    }
  }

  const handleClickNewChatButton = () => {
    for (let cat of Object.values(AGENT)) {
      localStorage.removeItem(`${cat}_accessToken`)
      localStorage.removeItem(`${cat}_refreshToken`)
    }
    location.reload()
  }

  const handleClickSettingButton = () => {
    onOpenSetting?.()
  }

  return (
    <div className={styles['chat-header']}>
      <div className={styles['chat-header-wrapper']}>
        <img
          onClick={handleClickBackButton}
          className={styles['back-button']}
          src={iconChevronLeft}
          alt="back button"
        />
        <div className={styles['solomon-profile']}>
          {agent === AGENT.CS ? (
            <img alt="solomon logo" src={iconSolomon} />
          ) : (
            <img alt="solomon logo" src={iconAiSolomon} />
          )}
        </div>
        <div className={styles['solomon-detail']}>
          <div className={styles['solomon-name']}>
            <p>{title}</p>
            <img alt="crown" src={iconCrown} />
          </div>
          <p className={styles['status']}>
            {info} in {agent}
          </p>
        </div>
        {!isHistory && (
          <button
            className={styles['new-chat-button']}
            onMouseOver={() => setIsTooltipVisible(true)}
            onMouseOut={() => setIsTooltipVisible(false)}
            onClick={handleClickNewChatButton}
          >
            <div
              className={styles['new-chat-tooltip']}
              style={{ display: isTooltipVisible ? '' : 'none' }}
            >
              <span className={styles['tooltip-title']}>{'\uC0C8 \uCC44\uD305 \uC2DC\uC791'}</span>
              <br />
              {'\uB300\uD654 \uAE30\uB85D\uC774 \uCD08\uAE30\uD654 \uB429\uB2C8\uB2E4.'}
            </div>
            <img src={iconWrite} alt={'\uC0C8 \uCC44\uD305 \uC2DC\uC791 \uBC84\uD2BC'} />
          </button>
        )}
        {!isHistory && (
          <button className={styles['setting-button']} onClick={handleClickSettingButton}>
            <div></div>
            <div></div>
            <div></div>
          </button>
        )}
        {!isHistory && (
          <button
            className={styles['history-button']}
            onClick={() => navigate(`/admin/history/${agent}`)}
          >
            <img src={iconHistory} alt={'\uD788\uC2A4\uD1A0\uB9AC \uBC84\uD2BC'} />
          </button>
        )}
      </div>
    </div>
  )
}
