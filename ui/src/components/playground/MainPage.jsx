import { Link } from 'react-router-dom'
import solomonLogo from '@/assets/icon--solomon-logo.svg'
import arrowUpIcon from '@/assets/icon--arrow-up.svg'
import mainImage from '@/assets/icon--solomon-main.svg'
import styles from './MainPage.module.scss'

const MainPage = () => {
  return (
    <div className={styles.mainContainer}>
      <div className={styles.header}>
        <img className={styles.logo} src={solomonLogo} alt="solomon logo" />
      </div>
      <div className={styles.mainContainerWrapper}>
        <div className={styles.intro}>
          <h1 className={styles.mainTitle}>뷰저블의 생성형 AI 챗봇 UX GPT</h1>
          <p className={styles.mainDescription}>
            뷰저블 서비스, 데이터 분석에 대해 무엇이든 물어보세요. <br />
            UX GPT가 전문적으로 답변해드립니다.
          </p>
          <div className={styles.hashtag}>
            <span>#Beusable</span> <span>#BeusableForum</span> <span>#DataDrivenUX</span>
            <span>#SWCAG</span>
          </div>
          <div className={styles.buttonContainer}>
            <div>
              <Link className={styles.navButton} to="/admin/chat/main">
                UX GPT
                <span>
                  <img src={arrowUpIcon} alt="채팅 시작하기 아이콘" />
                </span>
              </Link>
            </div>
            <div>
              <Link className={styles.navButton} to="/admin/chat/cs">
                CX GPT
                <span>
                  <img src={arrowUpIcon} alt="채팅 시작하기 아이콘" />
                </span>
              </Link>
            </div>
          </div>
        </div>
        <div className={styles.imageContainer}>
          <img className={styles.mainImage} src={mainImage} alt="main image" />
        </div>
      </div>
    </div>
  )
}

export default MainPage
