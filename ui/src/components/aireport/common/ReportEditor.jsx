import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { getCookieValue } from '@/utils/utils.js'
import UiButton from '@/components/aireport/ui/UiButton'
import styles from './ReportEditor.module.scss'

/**
 * ReportEditor - CKEditor-based rich text editor for report editing.
 * In Vue this used the <ckeditor> component with DecoupledEditor.
 * In React, CKEditor5 integration would use @ckeditor/ckeditor5-react.
 * The editor config and logic are preserved here for integration.
 */
export default function ReportEditor({
  ready,
  value,
  onChange,
  onButton,
  onDrawChart,
  topStatic
}) {
  const { t, i18n } = useTranslation()
  const serviceLocale = getCookieValue('locale')
  const locale = serviceLocale || i18n.language

  const [hasShadow, setHasShadow] = useState(false)
  const editorToolbarRef = useRef(null)
  const editorRef = useRef(null)

  const editorConfig = useMemo(
    () => ({
      toolbar: {
        items: [
          'undo',
          'redo',
          '|',
          'heading',
          '|',
          'fontSize',
          'fontFamily',
          'fontColor',
          'fontBackgroundColor',
          '|',
          'bold',
          'italic',
          'underline',
          'strikethrough',
          '|',
          'link',
          'highlight',
          '|',
          'alignment',
          '|',
          'bulletedList',
          'numberedList',
          'outdent',
          'indent'
        ],
        shouldNotGroupWhenFull: false
      },
      htmlSupport: {
        allow: [
          {
            name: /.*/,
            attributes: true,
            classes: true,
            styles: true
          }
        ],
        disallow: [{ name: 'img' }],
        allowEmpty: ['i', 'span', 'hr']
      },
      allowedContent: true,
      heading: {
        options: [
          { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
          { model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1' },
          { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' },
          { model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3' },
          { model: 'heading4', view: 'h4', title: 'Heading 4', class: 'ck-heading_heading4' },
          { model: 'heading5', view: 'h5', title: 'Heading 5', class: 'ck-heading_heading5' },
          { model: 'heading6', view: 'h6', title: 'Heading 6', class: 'ck-heading_heading6' }
        ]
      },
      fontFamily: { supportAllValues: true },
      fontSize: {
        options: [10, 12, 14, 16, 18, 20, 22, 'default'],
        supportAllValues: true
      },
      list: {
        properties: { styles: true, startIndex: true, reversed: true }
      },
      initialData: '',
      link: {
        addTargetToExternalLinks: true,
        defaultProtocol: 'https://',
        decorators: {
          toggleDownloadable: {
            mode: 'manual',
            label: 'Downloadable',
            attributes: { download: 'file' }
          }
        }
      },
      placeholder: '',
      ui: {
        poweredBy: { position: 'inside', side: 'right' }
      }
    }),
    []
  )

  const handleEditorReady = useCallback(
    (editor) => {
      editorRef.current = editor
      if (!editorToolbarRef.current) return
      const toolbarEl = editorToolbarRef.current
      Array.from(toolbarEl.children).forEach((child) => child.remove())
      toolbarEl.appendChild(editor.ui.view.toolbar.element)
      onDrawChart?.('#report-editor')
    },
    [onDrawChart]
  )

  useEffect(() => {
    const handleScroll = () => {
      setHasShadow(window.scrollY > 0)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div id="report-editor" className={styles.reportEditor}>
      <div className={`${styles.toolbar} ${hasShadow ? styles.shadow : ''}`}>
        <div className={styles.toolbarExternal}>
          <div className={styles.toolbarExternalContent}>
            <i className="icon icon--editor-black" />
            <p className={styles.toolbarExternalContentTitle}>
              {t('aireport.editor.toolbar.title', { lng: locale })}
            </p>
            <div className={styles.toolbarExternalContentDivider} />
            <p className={styles.toolbarExternalContentSub}>
              {t('aireport.editor.toolbar.description', { lng: locale })}
            </p>
          </div>
          <div className={styles.toolbarExternalButtons}>
            <UiButton size="small" onClick={() => onButton?.('cancel')}>
              {t('common.cancel', { lng: locale })}
            </UiButton>
            <UiButton
              size="small"
              primary
              iconName="icon--check-white"
              onClick={() => onButton?.('save')}
            >
              {t('aireport.editor.button.done', { lng: locale })}
            </UiButton>
          </div>
        </div>
        <div className={styles.editorContainerToolbar} ref={editorToolbarRef} />
      </div>
      {topStatic}
      {ready && (
        <div
          className={styles.editorContainer}
          contentEditable
          suppressContentEditableWarning
          dangerouslySetInnerHTML={{ __html: value || '' }}
          onInput={(e) => onChange?.(e.currentTarget.innerHTML)}
        />
      )}
    </div>
  )
}
