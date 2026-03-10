import { useState, useCallback } from 'react'
import { useStore } from '@/store'
import chevronLeftIcon from '@/assets/icon--chevronLeft.svg'
import CustomSampleView from './CustomSampleView'
import styles from './CustomChatTheme.module.scss'

const CustomChatTheme = ({ onClose }) => {
  const customColor = useStore((state) => state.getCustomColorTheme())
  const updateColorTheme = useStore((state) => state.updateColorTheme)
  const updateCustomColorTheme = useStore((state) => state.updateCustomColorTheme)

  const [color, setColor] = useState({
    background: customColor.background || '#ffffff',
    textColor: customColor.textColor || '#333333',
    subTextColor: customColor.subTextColor || '#79797f',
    invertedTextColor: customColor.invertedTextColor || '#ffffff',
    themeColor: customColor.themeColor || '#ec0047'
  })

  const handleColorChange = useCallback((key, value) => {
    setColor((prev) => ({ ...prev, [key]: value }))
  }, [])

  const handleClickSave = useCallback(() => {
    updateColorTheme({ theme: 'custom' })
    updateCustomColorTheme({ colors: color })
    onClose()
  }, [color, updateColorTheme, updateCustomColorTheme, onClose])

  return (
    <div className={styles.settingContainer}>
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
        <CustomSampleView color={color} />
        <div className={styles.selectList}>
          <div className={styles.selectItem}>
            <span className={styles.selectColorName}>배경색</span>
            <input
              type="color"
              value={color.background}
              onChange={(e) => handleColorChange('background', e.target.value)}
            />
          </div>
          <div className={styles.selectItem}>
            <span className={styles.selectColorName}>테마 색상</span>
            <input
              type="color"
              value={color.themeColor}
              onChange={(e) => handleColorChange('themeColor', e.target.value)}
            />
          </div>
          <div className={styles.selectItem}>
            <span className={styles.selectColorName}>폰트 색상</span>
            <input
              type="color"
              value={color.textColor}
              onChange={(e) => handleColorChange('textColor', e.target.value)}
            />
          </div>
          <div className={styles.selectItem}>
            <span className={styles.selectColorName}>서브 폰트 색상</span>
            <input
              type="color"
              value={color.subTextColor}
              onChange={(e) => handleColorChange('subTextColor', e.target.value)}
            />
          </div>
          <div className={styles.selectItem}>
            <span className={styles.selectColorName}>반전 폰트 색상</span>
            <input
              type="color"
              value={color.invertedTextColor}
              onChange={(e) => handleColorChange('invertedTextColor', e.target.value)}
            />
          </div>
          <div className={styles.buttonContainer}>
            <div className={styles.saveButton} onClick={handleClickSave}>
              적용
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CustomChatTheme
