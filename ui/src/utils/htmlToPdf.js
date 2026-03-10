import html2pdf from 'html2pdf.js'

export const htmlToPdf = (location, fileName) => {
  const option = {
    // margin: [0, 0, 0, 0],
    filename: fileName,
    // pagebreak: { mode: 'avoid-all' },
    image: { type: 'jpeg', quality: 1 },
    html2canvas: {
      useCORS: true,
      scrollY: 0,
      scale: 3,
      allowTaint: false, // useCORS 시 필수
      dpi: 300,
      letterRendering: true // 텍스트 품질 향상
    },
    jsPDF: {
      unit: 'px',
      format: [950, 1344],
      orientation: 'portrait', // 세로 방향
      hotfixes: ['px_scaling'] // px 단위 사용 시 필수
    },
    enableLinks: true
  }

  html2pdf().from(location).set(option).save()
}
