import { useState, useCallback } from 'react'
import { useStore } from '@/store'
import { themes } from '@/utils/constants'
import chevronLeftIcon from '@/assets/icon--chevronLeft.svg'
import CustomChatTheme from './CustomChatTheme'
import styles from './ChatSetting.module.scss'

const ChatSetting = ({ onClose }) => {
  const colorTheme = useStore((state) => state.getColorTheme())
  const updateColorTheme = useStore((state) => state.updateColorTheme)
  const [showCustomTheme, setShowCustomTheme] = useState(false)

  const handleSelectTheme = useCallback(
    (themeName) => {
      updateColorTheme({ theme: themeName })
    },
    [updateColorTheme]
  )

  const handleShowCustomTheme = useCallback(() => {
    setShowCustomTheme((prev) => !prev)
  }, [])

  const getThemeButtonStyle = (theme) => ({
    backgroundImage: `linear-gradient(${theme.colorCodes[0]},${theme.colorCodes[1]},${theme.colorCodes[2]},${theme.colorCodes[3]})`
  })

  return (
    <div className={styles.settingContainer}>
      {showCustomTheme && <CustomChatTheme onClose={handleShowCustomTheme} />}
      <div className={styles.settingContainerWrapper}>
        <h1 className={styles.title}>
          <img
            className={styles.closeButton}
            src={chevronLeftIcon}
            alt="뒤로가기 버튼"
            onClick={onClose}
          />
          설정
        </h1>
        <div>
          <h2 className={styles.subtitle}>테마 변경</h2>
          <div className={styles.themeItemList}>
            {themes.map((item) => (
              <div
                className={styles.themeItem}
                key={item.name}
                onClick={() => handleSelectTheme(item.name)}
              >
                <div className={styles.themeItemColorWrapper}>
                  <div className={styles.themeItemColor} style={getThemeButtonStyle(item)} />
                </div>
                <div className={styles.colorName}>
                  {colorTheme === item.name && <span className={styles.selectedMark} />}
                  {item.name}
                </div>
              </div>
            ))}
            <div className={styles.themeItem}>
              <div className={styles.themeItemColorWrapper} onClick={handleShowCustomTheme}>
                <div
                  className={styles.themeItemColor}
                  style={{
                    backgroundImage: 'linear-gradient(red, yellow, green, skyblue, purple)'
                  }}
                />
              </div>
              <div className={styles.colorName}>
                {colorTheme === 'custom' && <span className={styles.selectedMark} />}
                custom
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatSetting
