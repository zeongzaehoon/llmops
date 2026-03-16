import { getTimeString } from '@/utils/utils'
const CHART_DATA_COLOR = {
  1: { chartBar: '#FFAA2B', chartBg: '#FFD17766', chartLine: '#FFD177', chartPoint: '#fff' },
  2: { chartBar: '#EF487A', chartBg: '#FFCEDD66', chartLine: '#FFAEC6', chartPoint: '#fff' },
  3: { chartBar: '#707EC5', chartBg: '#d8deff66', chartLine: '#BAC5FF', chartPoint: '#fff' },
  4: { chartBar: '#50B2DD', chartBg: '#cdf0ff66', chartLine: '#89DBFF', chartPoint: '#fff' }
}

const RANKING_COLORS = {
  stayin: { borderColor: 'rgb(129 165 7)', bgColor: 'rgb(129, 165, 7, 0.15)' },
  drop: { borderColor: 'rgb(255 74 0)', bgColor: 'rgb(255, 74, 0, 0.15)' },
  interval: { borderColor: 'rgb(75 143 13)', bgColor: 'rgb(129, 165, 7, 0.15)' },
  rollback: { borderColor: 'rgb(150 101 227)', bgColor: 'rgb(150, 101, 227, 0.15)' },
  reload: { borderColor: 'rgb(0 116 255)', bgColor: 'rgb(0, 116, 255, 0.15)' }
}

export const defaultOption = {
  responsive: false,
  plugins: {
    datalabels: {
      font: {
        weight: 700,
        size: 16
      }
    },
    legend: {
      align: 'start',
      labels: {
        color: '#000000',
        boxWidth: 0,
        font: {
          size: 16,
          weight: 500
        }
      }
    }
  },
  layout: {
    padding: {
      top: 30
    }
  },
  scales: {
    x: {
      grid: {
        drawOnChartArea: false
      },
      offset: true
    },
    y: {
      border: {
        display: false
      },
      beginAtZero: true,
      ticks: {
        padding: 10
      },
      afterBuildTicks: function (axis) {
        const tickValues = axis.ticks.map((tick) => tick.value)
        const max = tickValues[tickValues.length - 1]
        const stepSize = Math.round(max / 2)

        axis.ticks = [
          { label: 0, value: 0 },
          { label: stepSize, value: stepSize },
          { label: 2 * stepSize, value: 2 * stepSize }
        ]
      }
    }
  }
}

export const percentageOption = {
  scales: {
    x: {
      grid: {
        drawOnChartArea: false
      },
      offset: true
    },
    y: {
      beginAtZero: true,
      min: 0,
      max: 100,
      border: {
        display: false
      },
      ticks: {
        stepSize: 50,
        padding: 10,
        callback: function (value) {
          return value + '%'
        }
      }
    }
  }
}

export const defaultDatasets = {
  datalabels: { align: 'end', anchor: 'end' },
  maxBarThickness: 24
}

export const category3ChartOption = {
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    r: {
      ticks: {
        display: false
      },
      pointLabels: {
        color: '#888888',
        font: {
          size: 12
        }
      }
    }
  },
  elements: {
    point: {
      radius: 0
    }
  },
  responsive: false
}

export const getTrendChartDataSets = (idx = null) => {
  return {
    line: {
      borderColor: idx ? CHART_DATA_COLOR[idx].chartLine : '#61D5E7',
      borderWidth: 2,
      pointRadius: 4,
      pointBorderColor: idx ? CHART_DATA_COLOR[idx].chartLine : '#61D5E7',
      pointBackgroundColor: idx ? CHART_DATA_COLOR[idx].chartPoint : '#fff',
      type: 'line',
      order: 0
    },
    bar: {
      backgroundColor: idx ? CHART_DATA_COLOR[idx].chartBar : '#0E90A5',
      borderColor: idx ? CHART_DATA_COLOR[idx].chartBar : '#0E90A5',
      borderWidth: 0,
      order: 1
    },
    background: {
      backgroundColor: idx ? CHART_DATA_COLOR[idx].chartBg : 'rgba(219, 222, 152, 0.40)',
      borderWidth: 0,
      type: 'line',
      order: 2,
      fill: true
    }
  }
}

export const trendChartOption = {
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: false
    },
    myPlugin: {
      shiftAmount: 5
    }
  },
  scales: {
    x: {
      border: {
        color: '#767676',
        width: 1
      },
      ticks: {
        color: '#444444',
        padding: 12,
        font: {
          size: 13
        }
      },
      grid: {
        drawOnChartArea: false,
        offset: false,
        tickColor: '#767676',
        tickLength: 6
      }
    },
    y: {
      border: {
        display: false
      },
      ticks: {
        color: '#444444',
        padding: 12,
        font: {
          size: 13
        }
      },
      grid: {
        drawTicks: false
      },
      afterFit(scale) {
        scale.width = 110
      }
    }
  },
  responsive: false,
  maxBarThickness: 24,
  elements: {
    point: {
      radius: 0
    }
  }
}

export const getRankingScatterChartDataSets = (type) => {
  return {
    showLine: true,
    fill: true,
    tension: 0.4,
    borderWidth: 1.6,
    borderColor: RANKING_COLORS[type].borderColor,
    backgroundColor: RANKING_COLORS[type].bgColor,
    label: 'Page'
  }
}

export const getRankingScatterChartOption = (type) => {
  return {
    maintainAspectRatio: false,
    responsive: true,
    plugins: {
      legend: {
        display: false
      }
    },
    elements: {
      point: {
        radius: 0
      }
    },
    scales: {
      x: {
        border: {
          color: '#767676',
          width: 1
        },
        ticks: {
          color: '#444444',
          font: {
            size: 7
          },
          callback: function (value) {
            if (type === 'interval') {
              return getTimeString(value)
            }
            return value
          }
        },
        grid: {
          drawOnChartArea: false,
          offset: false,
          tickColor: '#767676',
          tickLength: 3
        },
        min: type === 'interval' ? -90 : -5,
        max: type === 'interval' ? 1890 : 105,
        afterBuildTicks: function (axis) {
          if (type === 'interval') {
            axis.ticks = [
              { label: 0, value: 0 },
              { label: 900, value: 900 },
              { label: 1800, value: 1800 }
            ]
          } else {
            axis.ticks = [
              { label: 0, value: 0 },
              { label: 50, value: 50 },
              { label: 100, value: 100 }
            ]
          }
        }
      },
      y: {
        grid: {
          drawTicks: false
        },
        border: {
          display: false
        },
        ticks: {
          padding: 6,
          color: '#444444',
          font: {
            size: 7
          }
        },
        afterBuildTicks: function (axis) {
          // y축 tick이 0포함 3개가 생기도록
          const tickValues = axis.ticks.map((tick) => tick.value)
          const max = tickValues[tickValues.length - 1]
          const stepSize = Math.round(max / 2)

          axis.ticks = [
            { label: 0, value: 0 },
            { label: stepSize, value: stepSize },
            { label: 2 * stepSize, value: 2 * stepSize }
          ]
        },
        afterFit(scale) {
          scale.width = 21
        }
      }
    }
  }
}

export const scrollReportChartColors = [
  '#000204',
  '#02080C',
  '#030D13',
  '#04121A',
  '#051720',
  '#061D29',
  '#07222F',
  '#082839',
  '#092B3B',
  '#073043',
  '#0B374D',
  '#0D3C54',
  '#0D4059',
  '#0E4763',
  '#0F4C68',
  '#115374',
  '#125678',
  '#125C80',
  '#136087',
  '#15678F',
  '#166C96',
  '#17729E',
  '#1877A4',
  '#197BAC',
  '#1B81B3',
  '#1B87B7',
  '#1A8BB1',
  '#1890A9',
  '#1794A2',
  '#179A9A',
  '#159F91',
  '#14A28B',
  '#13A883',
  '#0FAC7B',
  '#0EB173',
  '#10B76D',
  '#0CBA65',
  '#0EBF60',
  '#0AC457',
  '#0CCA51',
  '#0BCD4C',
  '#0AD245',
  '#09D83C',
  '#08DB36',
  '#07E12E',
  '#05E626',
  '#05EA21',
  '#04EE1A',
  '#02F311',
  '#01F809',
  '#00FE00',
  '#03FE00',
  '#11FB02',
  '#1CF904',
  '#26F705',
  '#2DF606',
  '#37F307',
  '#42F109',
  '#4DEE0A',
  '#56ED0B',
  '#61EB0D',
  '#6BE90E',
  '#72E80F',
  '#7DE510',
  '#85E311',
  '#90E113',
  '#9CDE14',
  '#A5DD15',
  '#AFDB17',
  '#B9D919',
  '#C3D719',
  '#CED51B',
  '#D7D31C',
  '#E3D11E',
  '#EECE1F',
  '#F5CD20',
  '#FCC821',
  '#FCBF1F',
  '#FCB81E',
  '#FCB01C',
  '#FDA71B',
  '#FD9F17',
  '#FD9619',
  '#FD8E17',
  '#FD8616',
  '#FD7D14',
  '#FE7914',
  '#FE6D12',
  '#FD6711',
  '#FD5E0F',
  '#FE570F',
  '#FE4F0D',
  '#FE460B',
  '#FF3F0B',
  '#FE3509',
  '#FF2E08',
  '#FF2006',
  '#FF2106',
  '#FE1904',
  '#FF1003',
  '#FF0902'
]
