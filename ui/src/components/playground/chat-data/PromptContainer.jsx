import { useState } from 'react'
import onMouseDown from '@/directives/flexible-view/flexible-view.js'

import PromptDetail from './PromptDetail'

import styles from './PromptContainer.module.scss'

import iconVisible from '@/assets/icon--visible.svg'
import iconInvisible from '@/assets/icon--invisible.svg'

const PromptContainer = ({ agent }) => {
  const [invisible, setInvisible] = useState(false)

  return (
    <>
      <div
        className={`${styles['prompt-container']} flexible-container layout-v ${invisible ? styles.invisible : ''}`}
        onMouseDown={onMouseDown}
      >
        <PromptDetail
          title="GPT Prompt"
          kind="prompt"
          size="long"
          agent={agent}
        />
      </div>
      <button className={styles['visible-button']} onClick={() => setInvisible(!invisible)}>
        {invisible ? (
          <img src={iconVisible} alt="visible button" />
        ) : (
          <img src={iconInvisible} alt="invisible button" />
        )}
      </button>
    </>
  )
}

export default PromptContainer
