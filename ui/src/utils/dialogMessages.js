import i18n from '@/lang/index'

export const getDialogData = (locale) => {
  const t = (key) => i18n.t(key, { lng: locale })

  return {
    completeEdit: {
      type: 'alert',
      iconClass: 'icon--dialog-check',
      title: t('aireport.editor.complete.title'),
      description: t('aireport.editor.complete.description')
    },
    errorEdit: {
      type: 'alert',
      iconClass: 'icon--dialog-warning',
      title: t('aireport.editor.error.title'),
      description: t('aireport.editor.error.description')
    },
    excessEdit: {
      type: 'confirm',
      iconClass: 'icon--dialog-warning',
      title: t('aireport.editor.excess.title'),
      description: t('aireport.editor.excess.description')
    },
    exitEdit: {
      type: 'confirm',
      iconClass: 'icon--dialog-warning',
      title: t('aireport.editor.exit.title'),
      description: t('aireport.editor.exit.description')
    },
    claim: {
      claimInput: {
        type: 'textarea',
        iconClass: 'icon--dialog-warning',
        title: t('aireport.claim.title'),
        longDescription: t('aireport.claim.description'),
        placeholder: t('aireport.claim.placeholder')
      },
      claimSuccess: {
        type: 'alert',
        iconClass: 'icon--dialog-check',
        title: t('aireport.claim.success.title'),
        description: t('aireport.claim.success.desc')
      },
      claimFail: {
        type: 'alert',
        iconClass: 'icon--dialog-warning',
        title: t('aireport.claim.fail.title'),
        description: t('aireport.claim.fail.desc')
      }
    }
  }
}
