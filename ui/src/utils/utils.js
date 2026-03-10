import punycode from 'punycode'
import i18n from '@/lang/index'
import { BA_URL } from '@/utils/constants'

export const getCookieValue = (cookieName) => {
  let cookies = document.cookie
  let cookiesArray = cookies.split(';')

  for (let i = 0; i < cookiesArray.length; i++) {
    let cookiePair = cookiesArray[i].split('=')
    let name = cookiePair[0].trim()
    let value = cookiePair[1]

    if (name === cookieName) {
      return value
    }
  }
  return null
}

export const getTimeString = (value, lang = null) => {
  const t = i18n.t.bind(i18n)

  let hour = Math.floor(value / 3600)
  let minute = Math.floor(value / 60) % 60
  let second = Math.round(value % 60)
  if (second > 59) {
    second = 0
    minute++
  }
  if (minute > 59) {
    minute = 0
    hour++
  }
  if (hour >= 1) {
    return lang === 'en'
      ? `${hour}h ${minute}m ${second}s`
      : `${hour}${t('time.h')} ${minute}${t('time.m')} ${second}${t('time.s')}`
  }
  if (minute >= 1) {
    return lang === 'en'
      ? `${minute}m ${second}s`
      : `${minute}${t('time.m')} ${second}${t('time.s')}`
  }
  return lang === 'en' ? `${second}s` : `${second}${t('time.s')}`
}

export const getDayOfWeek = (yyyyMMdd) => {
  const dayOfWeekArr = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
  const dayOfWeekArrIdx = new Date(yyyyMMdd).getDay()

  return dayOfWeekArr[dayOfWeekArrIdx]
}

export const capitalizeFirstLetter = (string) => {
  if (typeof string !== 'string' || string.length === 0) {
    return string
  }
  return string.charAt(0).toUpperCase() + string.slice(1)
}

export const getJourneyHref = (treeId, data) => {
  const { type, sid, subSid, firstPath, _id } = data

  let journeyLink = `${BA_URL}/tool/${type}?sid=${sid}`
  if (subSid) {
    journeyLink += `&subSid=${subSid}`
    if (firstPath) {
      journeyLink += `&path=${firstPath}`
    }
  }
  journeyLink += `&aiReportId=${_id}`
  if (treeId) {
    journeyLink += `&aiReportTreeId=${treeId}`
  }
  return journeyLink
}

export const getS3Url = (pathKey, timestamp) => {
  if (!pathKey) {
    return null
  }

  const [bucketName, filePath] = pathKey.split(':')

  let endPoint = 'https://s3.ap-northeast-2.amazonaws.com'
  let url = `${endPoint}/${bucketName}/${filePath}`

  if (timestamp) {
    url += `?v=${timestamp}`
  }
  return url
}

export function getDomainForView(value) {
  let domain = value.trim().replace('http://', '').replace('https://', '')

  if (domain.startsWith('xn--') > -1) {
    return punycode.toUnicode(domain)
  } else {
    return value
  }
}

export function getDomainForData(value) {
  let domain = value.trim()
  if (/[\u3131-\uD79D]/.test(domain)) {
    return punycode.toASCII(domain)
  } else {
    return domain
  }
}

function b64DecodeUnicode(str) {
  return decodeURIComponent(
    Array.prototype.map
      .call(atob(str), (c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join('')
  )
}

export function parseJwt(token) {
  return JSON.parse(b64DecodeUnicode(token.split('.')[1].replace('-', '+').replace('_', '/')))
}
