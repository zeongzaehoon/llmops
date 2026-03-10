import { AI_CATEGORY } from '@/utils/constants.js'

const RANKING_FIELDS = {
  stayin: { field: 'cvrRate' },
  drop: { field: 'dropRate' },
  interval: { field: 'interval' },
  intervalReverse: { field: 'interval' },
  rollback: { field: 'rollbackRate' },
  reload: { field: 'reloadRate' }
}
import {
  category3ChartOption,
  getRankingScatterChartDataSets,
  getRankingScatterChartOption,
  getTrendChartDataSets,
  trendChartOption
} from '@/utils/chartConfig.js'

const emptySessionObj = {
  empty: true,
  dropCnt: 0,
  dropRate: 0,
  sessionCnt: 0
}

export const lineAlignment = {
  id: 'lineAlignment',
  afterDatasetsDraw(chart) {
    const { data } = chart
    const dataArr = [1, 2]

    dataArr.forEach((i) => {
      const xCoor = []
      const barIndex = chart.data.datasets.findIndex((dataset) => dataset.label === 'bar' + i)
      const lineIndex = chart.data.datasets.findIndex((dataset) => dataset.label === 'line' + i)
      const fillIndex = chart.data.datasets.findIndex((dataset) => dataset.label === 'fill' + i)
      for (let i = 0; i < data.labels.length; i++) {
        xCoor.push(chart.getDatasetMeta(barIndex).data[i].x)
      }
      chart.getDatasetMeta(lineIndex).data.forEach((dataPoint, index) => {
        dataPoint.x = xCoor[index]
      })
      chart.getDatasetMeta(fillIndex).data.forEach((dataPoint, index) => {
        dataPoint.x = xCoor[index]
      })
    })
  }
}

export const getRankingChartRange = (type, rawData) => {
  const rawMax = rawData.pvTop20[type].max
  const rawMin = rawData.pvTop20[type].min

  let rangeData = {
    min: {
      range:
        type === 'interval' ? Math.floor(rawMin / 90) * 90 + 45 : Math.floor(rawMin / 5) * 5 + 2.5,
      value: rawMin
    },
    max: {
      range:
        type === 'interval' ? Math.floor(rawMax / 90) * 90 + 45 : Math.floor(rawMax / 5) * 5 + 2.5,
      value: rawMax
    }
  }

  if (rawMin === 0) {
    rangeData.min.range = rawMin
  }
  if (rawMax === 100 && type !== 'interval') {
    rangeData.max.range = rawMax
  } else if (rawMax === 1800 && type === 'interval') {
    rangeData.max.range = rawMax
  }

  return rangeData
}

export const getRankingChartPoint = (type, rawData) => {
  const data = {}
  const field = RANKING_FIELDS[type].field
  let fullRatio = 0

  if (type === 'interval') {
    let cursor = 45
    data[0] = 0

    while (cursor < 1800) {
      data[cursor] = 0
      cursor += 90
    }

    for (const page of rawData.urlList.slice(0, 20)) {
      if (page[field] === 0) {
        data[page[field]]++
      } else if (page[field] === 1800) {
        fullRatio++
      } else {
        const range = Math.floor(page[field] / 90) * 90 + 45
        data[range]++
      }
    }
  } else {
    let cursor = 2.5
    data[0] = 0

    while (cursor < 100) {
      data[cursor] = 0
      cursor += 5
    }

    for (const page of rawData.urlList.slice(0, 20)) {
      if (page[field] === 0) {
        data[page[field]]++
      } else if (page[field] === 100) {
        fullRatio++
      } else {
        const range = Math.floor(page[field] / 5) * 5 + 2.5
        data[range]++
      }
    }
  }

  const rangeData = getRankingChartRange(type, rawData)

  for (const range in data) {
    if (range < rangeData.min.range || range > rangeData.max.range) {
      delete data[range]
    }
  }

  const dataPoints = Object.keys(data).map((key) => {
    return {
      x: parseFloat(key),
      y: data[key]
    }
  })

  if (fullRatio > 0) {
    dataPoints.push({ x: type === 'interval' ? 1800 : 100, y: fullRatio })
  }

  return dataPoints
}

export const getChartData = (chartType, rawDataArr, options = {}) => {
  if (!rawDataArr || rawDataArr.length === 0) return

  const { locale = 'ko', index = null } = options
  let chartData = {}

  if (chartType === 'categoryRadar') {
    let category3Data = {}

    for (let el of rawDataArr[0].category.AICategory3) {
      if (AI_CATEGORY.tertiary[el.name]) {
        const title = AI_CATEGORY.tertiary[el.name].title[locale]
        category3Data[title] = el.value
      } else {
        const title = AI_CATEGORY.tertiary['etc'].title[locale]
        if (title in category3Data) {
          category3Data[title] += el.value
        } else {
          category3Data[title] = el.value
        }
      }
    }

    chartData = {
      type: 'radar',
      data: {
        labels: Object.keys(category3Data),
        datasets: [
          {
            backgroundColor: '#3D3B3B99',
            borderColor: '#3D3B3B99',
            borderWidth: 0,
            data: Object.values(category3Data)
          }
        ]
      },
      options: category3ChartOption
    }
  } else if (chartType.includes('trend')) {
    const chartDataArr = rawDataArr.map((rawData) => {
      const seqData = Object.values(rawData.data)

      const sessionArray = JSON.parse(JSON.stringify(seqData)).map((seq) => {
        if (!seq.nodes || Object.keys(seq.nodes).length === 0) {
          seq.cvrRate = 0
        } else {
          seq.cvrRate = 100 - Math.round(seq.dropRate)
        }
        return seq
      })

      const sessionArrayForChart = [...sessionArray]

      while (sessionArrayForChart.length < 6) {
        sessionArrayForChart.push(emptySessionObj)
      }

      return {
        label: Array.from({ length: sessionArrayForChart.length }, (_, index) => `${index + 1}seq`),
        data: [...sessionArrayForChart].map((el) => el.sessionCnt)
      }
    })
    const dataSet1 = getTrendChartDataSets(index)
    chartData = {
      type: 'bar',
      data: {
        labels: chartDataArr[0].label,
        datasets: [
          {
            label: 'bar1',
            data: chartDataArr[0].data,
            ...dataSet1.bar
          },
          {
            label: 'line1',
            data: chartDataArr[0].data,
            ...dataSet1.line
          },
          {
            label: 'fill1',
            data: chartDataArr[0].data,
            ...dataSet1.background
          }
        ]
      },
      options: trendChartOption
    }

    if (chartType === 'trendCompare') {
      const dataSet2 = getTrendChartDataSets(index ? index + 1 : null)
      const compareChartData = [
        {
          label: 'bar2',
          data: chartDataArr[1].data,
          ...dataSet2.bar
        },
        {
          label: 'line2',
          data: chartDataArr[1].data,
          ...dataSet2.line
        },
        {
          label: 'fill2',
          data: chartDataArr[1].data,
          ...dataSet2.background
        }
      ]
      chartData.data.datasets.push(...compareChartData)
      chartData['plugins'] = [lineAlignment]
    }
  } else if (chartType === 'rankingDoughnut') {
    const sum = rawDataArr[0].urlList.slice(0, 20).reduce((acc, obj) => {
      return acc + obj.pv
    }, 0)
    const top20Ratio = ((sum / rawDataArr[0].totalPV) * 100).toFixed(1)

    chartData = {
      type: 'doughnut',
      data: {
        datasets: [
          {
            data: [top20Ratio, 100 - top20Ratio],
            backgroundColor: ['#ec0047', '#d8d8d8'],
            borderWidth: 0
          }
        ]
      },
      options: {
        cutout: '36%',
        responsive: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            enabled: false
          }
        }
      }
    }
  } else if (Object.keys(RANKING_FIELDS).indexOf(chartType) !== -1) {
    chartData = {
      type: 'scatter',
      data: {
        datasets: [
          {
            data: getRankingChartPoint(chartType, rawDataArr[0]),
            ...getRankingScatterChartDataSets(chartType)
          }
        ]
      },
      options: getRankingScatterChartOption(chartType)
    }
  }
  return chartData
}

export const getTrendInfoData = (rawData) => {
  const seqData = Object.values(rawData.data)
  const sessionArray = JSON.parse(JSON.stringify(seqData)).map((seq) => {
    if (!seq.nodes || Object.keys(seq.nodes).length === 0) {
      seq.cvrRate = 0
    } else {
      seq.cvrRate = 100 - Math.round(seq.dropRate)
    }
    return seq
  })

  const sessionArrayForChart = [...sessionArray]
  const topData = rawData.top

  while (sessionArrayForChart.length < 6) {
    sessionArrayForChart.push(emptySessionObj)
  }

  const maxDropSq = sessionArray.reduce((minIdx, cur, idx, arr) => {
    // 데이터가 n개 시퀀스까지 있을 경우 1~n 시퀀스 사이에서 최소값 추출
    if (idx === sessionArray.length - 1) return minIdx
    return cur.dropRate > arr[minIdx].dropRate ? idx : minIdx
  }, 0)

  const maxConversionSq = sessionArray.reduce((maxIdx, cur, idx, arr) => {
    // 데이터가 n개 시퀀스까지 있을 경우 1~n 시퀀스 사이에서 최대값 추출
    if (idx === sessionArray.length - 1) return maxIdx
    return cur.cvrRate >= arr[maxIdx].cvrRate ? idx : maxIdx
  }, 0)

  const conversionRate =
    sessionArray[sessionArray.length - 1].sessionCnt / sessionArray[0].sessionCnt

  // 최종 시퀀스까지 전환한 비율 lastSeq / firstSeq
  const finalConversionRate = Math.round(conversionRate * 100)

  return {
    sessionArrayForChart,
    maxDropSq,
    maxConversionSq,
    finalConversionRate,
    seqLength: sessionArray.length,
    topDropCntSeq: Number(topData.dropCnt.position.slice(0, 1)) + 1,
    topDropCntPage: topData.dropCnt.data.domain + topData.dropCnt.data.pathname,
    topDropRateSeq: Number(topData.dropRate.position.slice(0, 1)) + 1,
    topDropRatePage: topData.dropRate.data.domain + topData.dropRate.data.pathname,
    topCvrCntSeq: Number(topData.cvrCnt.position.slice(0, 1)) + 1,
    topCvrCntPage: topData.cvrCnt.data.domain + topData.cvrCnt.data.pathname,
    topCvrRateSeq: Number(topData.cvrRate.position.slice(0, 1)) + 1,
    topCvrRatePage: topData.cvrRate.data.domain + topData.cvrRate.data.pathname
  }
}
