const onMouseDown = ({ target: resizer, pageX: initX, pageY: initY }) => {
  if (resizer.className && resizer.className.match('flexible-handle')) {
    const container = resizer.parentElement
    const layout = container.className.match('layout-h') ? 'h' : 'v'
    const pane = resizer.previousElementSibling
    const initPaneWidth = pane.offsetWidth
    const initPaneHeight = pane.offsetHeight

    const { addEventListener: addEvent, removeEventListener: removeEvent } = window

    const resize = (initSize, offset = 0) => {
      if (layout === 'h') {
        let paneWidth = initSize + offset
        pane.style.width = `${paneWidth}px`
      } else {
        let paneHeight = initSize + offset
        pane.style.height = `${paneHeight}px`
      }
    }

    const onMouseMove = ({ pageX, pageY }) => {
      const offset = layout === 'h' ? pageX - initX : pageY - initY
      const initSize = layout === 'h' ? initPaneWidth : initPaneHeight
      resize(initSize, offset)
    }

    const onMouseUp = () => {
      const size = layout === 'h' ? pane.clientWidth : pane.clientHeight
      resize(size)

      removeEvent('mousemove', onMouseMove)
      removeEvent('mouseup', onMouseUp)
    }

    addEvent('mousemove', onMouseMove)
    addEvent('mouseup', onMouseUp)
  }
}

export default onMouseDown
