/**
 * 左滑返回 Hook
 * 支持手势左滑返回上一页
 */

import { useRef, useCallback } from 'react'

const useSwipeBack = (onBack, options = {}) => {
  const { threshold = 80, edgeWidth = 30 } = options
  const touchStartX = useRef(0)
  const touchStartY = useRef(0)
  const isEdgeTouch = useRef(false)

  const onTouchStart = useCallback((e) => {
    const touch = e.touches[0]
    touchStartX.current = touch.clientX
    touchStartY.current = touch.clientY
    // 只有从左边缘开始滑动才触发
    isEdgeTouch.current = touch.clientX < edgeWidth
  }, [edgeWidth])

  const onTouchEnd = useCallback((e) => {
    if (!isEdgeTouch.current) return
    
    const touch = e.changedTouches[0]
    const deltaX = touch.clientX - touchStartX.current
    const deltaY = Math.abs(touch.clientY - touchStartY.current)
    
    // 水平滑动距离大于阈值，且垂直滑动小于水平滑动
    if (deltaX > threshold && deltaY < deltaX) {
      onBack?.()
    }
    
    isEdgeTouch.current = false
  }, [threshold, onBack])

  return {
    onTouchStart,
    onTouchEnd
  }
}

export default useSwipeBack
