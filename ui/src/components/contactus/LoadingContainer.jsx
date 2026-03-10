import { useEffect, useRef } from 'react'
import styles from './LoadingContainer.module.scss'

export default function LoadingContainer() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const context = canvas.getContext('2d')
    const img = new Image()

    canvas.width = 996
    canvas.height = 747

    let animationId

    img.onload = () => {
      const w = img.width
      const h = img.height
      const a = 30

      const set = () => {
        context.clearRect(-a, -a, w + 50, h + 50)
        const inc = 0.5
        for (let j = 0; j <= h; j++) {
          const dx = ~~(inc * (Math.random() - 0.5) * a)
          context.drawImage(img, 0, j, w, 1, dx, j, w, 1)
        }
        animationId = window.requestAnimationFrame(set)
      }

      set()
    }

    img.src = '/solomon-screenshot.png'

    return () => {
      if (animationId) {
        window.cancelAnimationFrame(animationId)
      }
    }
  }, [])

  return (
    <div className={styles.loading}>
      <canvas ref={canvasRef}></canvas>
    </div>
  )
}
