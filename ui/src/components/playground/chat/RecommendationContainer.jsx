import styles from './RecommendationContainer.module.scss'

const questions = [
  'AARRR \uB370\uC774\uD130\uBD84\uC11D \uD504\uB808\uC784\uC6CC\uD06C\uAC00 \uBB50\uC57C?',
  'CTA \uBD84\uC11D \uBC29\uBC95 \uC54C\uB824\uC918',
  '\uBDF0\uC800\uBE14 \uD788\uD2B8\uB9F5\uC5D0 \uB300\uD574 \uC124\uBA85\uD574\uC918',
  'A/B Testing \uD558\uB294 \uBC29\uBC95 \uC54C\uB824\uC918'
]

export default function RecommendationContainer({ agent, onSubmit, style }) {
  const handleClickQuestion = (question) => {
    onSubmit?.({ prompt: question, agent })
  }

  return (
    <div className={styles['recommendation-container-wrapper']} style={style}>
      <div className={styles['recommendation-container']}>
        <div className={styles['recommendation-header']}>
          <div className={styles['message-icon']}>
            <div></div>
            <div></div>
            <div></div>
          </div>
          <p>{'\uC774\uB7F0 \uC9C8\uBB38\uB3C4 \uD560 \uC218 \uC788\uC5B4\uC694!'}</p>
        </div>
        <div className={styles['recommendation-list-wrapper']}>
          {questions.map((item) => (
            <div
              className={styles['questions-list']}
              key={item}
              onClick={() => handleClickQuestion(item)}
            >
              <div className={styles['question-item']}>
                <p>{item}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
