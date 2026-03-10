import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { deployPrompt, getDeployList, rollbackPrompt } from '@/api/adminApi.js'
import BaseModal from '@/components/playground/common/BaseModal'
import BaseButton from '@/components/playground/common/BaseButton'
import { HTTP_STATUS } from '@/utils/constants.js'
import BaseLoading from '@/components/playground/common/BaseLoading'

import styles from './PromptDeployModal.module.scss'

import iconVisible from '@/assets/icon--visible.svg'
import iconInvisible from '@/assets/icon--invisible.svg'

const PromptDeployModal = ({ type, onClose, onReload }) => {
  const currentEnv = import.meta.env.VITE_APP_NODE_ENV
  const [pwd, setPwd] = useState('')
  const [pwdInputType, setPwdInputType] = useState('password')
  const [showVerification, setShowVerification] = useState(false)
  const [showCompleteMsg, setShowCompleteMsg] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [deployTargets, setDeployTargets] = useState({ types: [], modules: [] })
  const [isTargetsLoading, setIsTargetsLoading] = useState(true)
  const [deployChecked, setDeployChecked] = useState(false)

  useEffect(() => {
    getDeployList()
      .then((res) => {
        setDeployTargets({
          types: res.data.data.update_type_list,
          modules: res.data.data.update_module_list
        })
      })
      .catch((e) => {
        setDeployTargets(null)
        console.log(e)
      })
      .finally(() => {
        setIsTargetsLoading(false)
      })
  }, [])

  const updatePromptVersion = (action) => {
    const data = { server: currentEnv, password: pwd }
    setIsLoading(true)

    if (action === 'deploy') {
      deployPrompt(data)
        .then((res) => {
          const result = res.data
          if (result.code === HTTP_STATUS.unauthrized) {
            alert('비밀번호가 올바르지 않습니다.')
          } else if (result.code === HTTP_STATUS.forbidden) {
            alert('스테이징 서버에서 실행해주세요.')
          } else {
            setShowCompleteMsg(true)
            onReload()
          }
          setPwd('')
        })
        .catch((e) => {
          alert('알 수 없는 오류가 발생했습니다.')
          console.log(e)
          setPwd('')
        })
        .finally(() => {
          setIsLoading(false)
        })
    } else if (action === 'rollback') {
      rollbackPrompt(data)
        .then((res) => {
          const result = res.data
          if (result.code === HTTP_STATUS.unauthrized) {
            alert('비밀번호가 올바르지 않습니다.')
          } else if (result.code === HTTP_STATUS.forbidden) {
            alert('스테이징 서버에서 실행해주세요.')
          } else {
            setShowCompleteMsg(true)
            onReload()
          }
          setPwd('')
        })
        .catch((e) => {
          alert('알 수 없는 오류가 발생했습니다.')
          console.log(e)
          setPwd('')
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
  }

  const handleChangeInputType = () => {
    if (pwdInputType === 'password') {
      setPwdInputType('text')
    } else {
      setPwdInputType('password')
    }
  }

  const handleClickConfirm = () => {
    if (!deployChecked) {
      alert('배포 대상을 확인해주세요.')
      return
    } else if (
      !deployTargets ||
      (deployTargets.types.length === 0 && deployTargets.modules.length === 0)
    ) {
      alert('배포 대상이 없습니다.')
      return
    }

    setShowVerification(true)
  }

  const modalsRoot = document.getElementById('modals')

  const renderContent = () => {
    if (showCompleteMsg) {
      return (
        <BaseModal timeOut={2000} onClose={onClose}>
          <div className={styles['modal-viewer-body']} slot="body">
            {type === 'deploy' ? '프롬프트 배포' : '프롬프트 롤백'} 완료
          </div>
        </BaseModal>
      )
    }

    if (showVerification) {
      return (
        <BaseModal onClose={onClose} title="비밀번호 확인">
          <div className={styles['modal-viewer-body']} slot="body">
            <div className={styles['pwd-input']}>
              <input
                id="deploy-pwd"
                type={pwdInputType}
                value={pwd}
                onChange={(e) => setPwd(e.target.value)}
                autoComplete="new-password"
                placeholder="비밀번호를 입력해주세요."
              />
              <div className={styles['visible-icon']} onClick={handleChangeInputType}>
                {pwdInputType === 'password' ? (
                  <img src={iconVisible} alt="visible button" />
                ) : (
                  <img src={iconInvisible} alt="visible button" />
                )}
              </div>
            </div>
            <BaseButton size="medium" onClick={() => updatePromptVersion(type)}>확인</BaseButton>
          </div>
        </BaseModal>
      )
    }

    if (type === 'deploy') {
      return (
        <BaseModal onClose={onClose} title={type === 'deploy' ? '프롬프트 배포' : '프롬프트 롤백'}>
          <div className={styles['modal-viewer-body']} slot="body">
            <div className={`${styles['deploy-target']} ${styles.short}`}>
              <p className={styles['deploy-target-title']}>배포 대상 타입 <span>changed</span></p>
              <p className={styles['deploy-target-description']}>모듈 조합이 변경된 타입</p>
              {!isTargetsLoading ? (
                <div className={styles['deploy-target-body']}>
                  {!deployTargets ? (
                    <p className={styles.error}>변경된 프롬프트를 불러올 수 없습니다.</p>
                  ) : deployTargets.types.length > 0 ? (
                    <ul className={styles['deploy-target-body-list']}>
                      {deployTargets.types.map((prompt) => (
                        <li key={prompt}>{prompt}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className={styles.error}>변경된 프롬프트가 없습니다.</p>
                  )}
                </div>
              ) : (
                <BaseLoading />
              )}
            </div>
            <div className={styles['deploy-target']}>
              <p className={styles['deploy-target-title']}>배포 대상 프롬프트 <span>changed</span></p>
              <p className={styles['deploy-target-description']}>생성 혹은 수정된 프롬프트</p>
              {!isTargetsLoading ? (
                <div className={styles['deploy-target-body']}>
                  {!deployTargets ? (
                    <p className={styles.error}>변경된 프롬프트를 불러올 수 없습니다.</p>
                  ) : deployTargets.modules.length > 0 ? (
                    <ul className={styles['deploy-target-body-list']}>
                      {deployTargets.modules.map((prompt) => (
                        <li key={prompt}>{prompt}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className={styles.error}>변경된 프롬프트가 없습니다.</p>
                  )}
                </div>
              ) : (
                <BaseLoading />
              )}
            </div>
            <div className={styles['deploy-confirm']}>
              <input
                type="checkbox"
                id="deploy_checkbox"
                checked={deployChecked}
                onChange={(e) => setDeployChecked(e.target.checked)}
              />
              <label htmlFor="deploy_checkbox">배포 대상을 확인했습니다.</label>
            </div>
            <BaseButton size="medium" onClick={handleClickConfirm}>확인</BaseButton>
          </div>
        </BaseModal>
      )
    }

    // rollback
    return (
      <BaseModal onClose={onClose} title={type === 'deploy' ? '프롬프트 배포' : '프롬프트 롤백'}>
        <div className={styles['modal-viewer-body']} slot="body">
          <p className={styles['deploy-modal-body']}>
            프롬프트 {type === 'deploy' ? '배포' : '롤백'}를 진행하시겠습니까?
          </p>
          <BaseButton size="medium" onClick={() => setShowVerification(true)}>확인</BaseButton>
        </div>
      </BaseModal>
    )
  }

  return createPortal(
    <>
      {renderContent()}
      {isLoading && <BaseModal isLoading={true} />}
    </>,
    modalsRoot
  )
}

export default PromptDeployModal
