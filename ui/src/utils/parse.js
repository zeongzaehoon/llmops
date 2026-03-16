import { unified } from 'unified'
import remarkGfm from 'remark-gfm'
import markdown from 'remark-parse'
import remark2rehype from 'remark-rehype'
import html from 'rehype-stringify'
import rehypePrismPlus from 'rehype-prism-plus'
import rehypeExternalLinks from 'rehype-external-links'
import { visit } from 'unist-util-visit'
import i18n from '@/lang/index'
const COMPARE_TABLE_COL_NAMES = [
  'data1', 'data2', 'data 1', 'data 2',
  '1주차', '2주차', '1 주차', '2 주차',
  '기간1', '기간2', '기간 1', '기간 2'
]

const regex = /&(nbsp|amp|lt|gt|quot|#39);/g
const chars = {
  '&nbsp;': ' ',
  '&amp;': '&',
  '&lt;': '<',
  '&gt;': '>',
  '&quot;': '"',
  '&#39;': "'"
}

const rawDataStrings = [
  'false',
  'exist',
  'true',
  'AICategory2',
  'JSON',
  'All',
  'Drop Rate',
  'Conversion Rate',
  'Reload Rate',
  'Interval',
  'Rollback Rate'
]

export const unescape = (str) => {
  if (regex.test(str)) {
    return str.replace(regex, (matched) => chars[matched] || matched)
  }

  return str
}

const setAdditionalHtmlProcess = ({ reportId, chartOption }) => {
  let tableNum = 0
  const headingTags = ['h2', 'h3', 'h4', 'h5', 'h6']

  return (tree) => {
    const newParent = {
      type: 'element',
      tagName: 'div',
      properties: { className: 'gpt_report_content' },
      children: tree.children
    }

    tree.children = [newParent]

    visit(tree, 'element', (node) => {
      const orderReg1 = /^\d+-\d+$/
      const orderReg2 = /^\d+-\d+-\d+$/

      if (headingTags.indexOf(node.tagName) !== -1) {
        if (node.children.length > 0 && node.children[0].type === 'text') {
          const textArr = node.children[0].value.split(' ')
          if (!textArr || textArr.length === 0) return
          const preText = textArr[0]
          if (orderReg1.test(preText)) {
            node.children[0].value = node.children[0].value.slice(preText.length + 1)
            node.children.unshift({
              type: 'element',
              tagName: 'span',
              properties: { className: 'order step2' },
              children: [{ type: 'text', value: preText }]
            })
          }
          if (orderReg2.test(preText)) {
            node.children[0].value = node.children[0].value.slice(preText.length + 1)
            node.children.unshift({
              type: 'element',
              tagName: 'span',
              properties: { className: 'order step3' },
              children: [{ type: 'text', value: preText }]
            })
          }
        }
      }
      const numRegex = /\d{1,3}(,\d{3})*(\.\d+)?/

      if (!chartOption) return

      if (node.tagName === 'table') {
        const tablelist = []
        const labels = []
        for (let child of node.children) {
          if (child.tagName === 'thead') {
            for (let theadChild of child.children) {
              if (theadChild.tagName === 'tr') {
                for (let trchild of theadChild.children) {
                  if (trchild.tagName === 'th' && trchild.children.length > 0) {
                    labels.push(trchild.children[0].value)
                  }
                }
              }
            }

            const isCompare = labels.every((item) => COMPARE_TABLE_COL_NAMES.includes(item))

            if (!isCompare) return
          } else if (child.tagName === 'tbody') {
            for (let tbodyChild of child.children) {
              if (tbodyChild.tagName === 'tr') {
                const table = { title: '', value: [] }
                let tdIndex = 0
                for (let trchild of tbodyChild.children) {
                  if (trchild.tagName === 'td' && trchild.children.length > 0) {
                    const textValue = findLastChildValue(trchild)

                    if (tdIndex === 0) table.title = textValue
                    else {
                      let num = textValue.match(numRegex)[0]
                      const numOnly = num.replace(',', '')
                      table.value.push(numOnly)
                    }
                    tdIndex++
                  }
                }
                tablelist.push(table)
              }
            }
          }
        }

        node.tagName = 'div'
        node.properties.className = 'canvasDiv'
        node.children = []
        for (let table of tablelist) {
          const tableData = {
            labels,
            datasets: [
              {
                label: table.title,
                data: table.value
              }
            ]
          }
          const tableId = reportId + '-' + tableNum + '-' + table.title
          sessionStorage.setItem(tableId, JSON.stringify(tableData))
          const canvasNode = {
            type: 'element',
            tagName: 'canvas',
            properties: {
              id: tableId,
              width: '324',
              height: '230',
              style: 'border: 1px solid #00000020'
            }
          }
          node.children.push(canvasNode)
        }

        tableNum++
      }
    })
  }
}

function findLastChildValue(obj) {
  if (!obj.children || obj.children.length === 0) {
    return obj.value
  }
  return findLastChildValue(obj.children[0])
}

const applyAdditionalFormatting = (reportOption = null) => {
  reportOption = reportOption || {}
  return (tree) => {
    visit(tree, 'element', (node) => {
      if (node.tagName === 'pre' && node.properties.className) {
        const className = node.properties.className.find((cls) => cls.startsWith('language-'))
        if (className) {
          const language = className.replace('language-', '')
          node.properties['data-language'] = language
        }
      }

      if (node.tagName === 'img') {
        node.properties.style = 'max-width: 80%; height: auto; padding: 20px 0;'
      }

      if (reportOption.reportId) {
        const children = getRawWordFormattedChild(node, reportOption.locale)
        if (children) node.children = children
      }
    })
  }
}

const getRawWordFormattedChild = (node, locale) => {
  if (!node || !node.children || !Array.isArray(node.children)) {
    return null
  }

  if (node.tagName === 'a') {
    return node.children
  }

  const processNode = (currentNode) => {
    if (currentNode.tagName === 'a' || node.properties['data-processed']) {
      return currentNode
    }
    if (currentNode.type === 'text') {
      const fragments = currentNode.value.split(new RegExp(`(${rawDataStrings.join('|')})`))
      return fragments.map((fragment) => {
        if (rawDataStrings.includes(fragment)) {
          return {
            type: 'element',
            tagName: 'a',
            properties: {
              href: i18n.t('aireport.common.rawWordRefUrl', { lng: locale }),
              title: i18n.t('aireport.common.rawWordRefAlt', { lng: locale }),
              target: '_blank',
              style: 'display: inline-flex; align-items: center; gap: 2px;',
              'data-processed': 'true'
            },
            children: [
              {
                type: 'element',
                tagName: 'span',
                properties: {
                  style: 'text-decoration: underline; color: #0074FF;',
                  'data-processed': 'true'
                },
                children: [
                  {
                    type: 'text',
                    value: fragment
                  }
                ]
              },
              {
                type: 'element',
                tagName: 'i',
                properties: {
                  className: 'icon icon--questionMark'
                }
              }
            ]
          }
        }
        return { type: 'text', value: fragment }
      })
    } else if (currentNode.type === 'element' && currentNode.children) {
      return {
        ...currentNode,
        children: currentNode.children.map(processNode).flat()
      }
    }
    return currentNode
  }

  return node.children.map(processNode).flat()
}

export const convertMarkdownToHtml = (markDownText) => {
  const htmlText = unified()
    .use(markdown)
    .use(remarkGfm, { singleTilde: false })
    .use(remark2rehype)
    .use(rehypePrismPlus)
    .use(rehypeExternalLinks, { rel: ['nofollow'], target: '_blank' })
    .use(applyAdditionalFormatting)
    .use(html)
    .processSync(markDownText)
  return htmlText
}

export const convertMarkdownToHtmlReport = (markDownText, reportOption = null) => {
  let processor = unified()
    .use(markdown)
    .use(remarkGfm, { singleTilde: false })
    .use(remark2rehype)
    .use(rehypeExternalLinks, { rel: ['nofollow'], target: '_blank' })
    .use(applyAdditionalFormatting, { ...reportOption })

  if (reportOption) {
    processor = processor.use(setAdditionalHtmlProcess, { ...reportOption })
  }

  return processor.use(html).processSync(markDownText)
}

export const formatDate = (dateStr, type = null) => {
  if (!dateStr) return ''
  const iso = typeof dateStr === 'string' && dateStr.endsWith('Z') ? dateStr : dateStr + 'Z'
  const date = new Date(iso)
  const TIME_ZONE = 9 * 60 * 60 * 1000

  if (Object.prototype.toString.call(date) !== '[object Date]' || isNaN(date)) {
    return ''
  }

  if (type === 'num') {
    return (
      date
        .toLocaleDateString('ko-KR', {
          timeZone: 'Asia/Seoul',
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        })
        .replace(/[^0-9]/g, '') +
      ' ' +
      date
        .toLocaleTimeString('ko-KR', {
          timeZone: 'Asia/Seoul',
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
        .replace(/[^0-9]/g, '')
    )
  }
  if (type === 'yyyy-mm-dd') {
    return new Date(date.getTime() + TIME_ZONE).toISOString().replace('T', ' ').slice(0, -5)
  }

  return date.toLocaleDateString('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric'
  })
}

export const getImageUrl = (name) => {
  return new URL(`../assets/${name}`, import.meta.url).href
}
