import Tooltip from './tooltip'
import './tooltip.css'
const defaultOpt = {
  trigger: 'hover', // click | hover
  maxWidth: 330,
  size: 'normal',
  theme: 'light', // light | dark
  direction: 'top', // top | bottom | left | right
  align: 'center', // start | center | end
  transition: 'linear',
  textAlign: 'left',
  offset: 10,
  customClass: 'btf-tooltip'
}

export default {
  install(app, options = {}) {
    const extendOption = { ...defaultOpt, ...options }
    app.directive('btf-tooltip', Tooltip(extendOption))
  }
}
