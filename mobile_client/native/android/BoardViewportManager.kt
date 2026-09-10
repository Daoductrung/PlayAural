package __PLAYAURAL_PACKAGE__

import android.graphics.Rect
import android.os.Bundle
import android.os.SystemClock
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.View
import android.view.ViewTreeObserver
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.OverScroller
import android.widget.ScrollView
import com.facebook.react.uimanager.ThemedReactContext
import com.facebook.react.uimanager.annotations.ReactProp
import com.facebook.react.uimanager.events.NativeGestureUtil
import com.facebook.react.uimanager.util.ReactFindViewUtil
import com.facebook.react.views.view.ReactViewGroup
import com.facebook.react.views.view.ReactViewManager
import kotlin.math.roundToInt

/** One native gesture owner and accessibility scroll surface for both board axes. */
class BoardViewportManager : ReactViewManager() {
  override fun getName() = "PlayAuralBoardViewport"

  override fun createViewInstance(context: ThemedReactContext): ReactViewGroup = BoardViewport(context)

  @ReactProp(name = "panningEnabled", defaultBoolean = true)
  fun setPanningEnabled(view: ReactViewGroup, enabled: Boolean) {
    (view as BoardViewport).setPanningEnabled(enabled)
  }

  @ReactProp(name = "focusTarget")
  fun setFocusTarget(view: ReactViewGroup, target: String?) {
    (view as BoardViewport).setFocusTarget(target)
  }
}

private class BoardViewport(context: ThemedReactContext) : ReactViewGroup(context) {
  private val scroller = OverScroller(context)
  private var panningEnabled = true
  private var dragging = false
  private var interceptedEvent = false
  private var panX = 0f
  private var panY = 0f
  private var focusTarget: String? = null
  private var focusedCell: View? = null
  private val focusRect = Rect()
  // A row may move even when the total board size stays the same. Observe the
  // final geometry before drawing: React Native lays out children directly and
  // does not guarantee Android global-layout callbacks for these updates.
  private val layoutListener = ViewTreeObserver.OnPreDrawListener {
    constrainAndReveal()
    true
  }

  private val detector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
    override fun onDown(event: MotionEvent): Boolean {
      val wasMoving = !scroller.isFinished
      scroller.forceFinished(true)
      panX = scrollX.toFloat()
      panY = scrollY.toFloat()
      if (wasMoving) beginDrag(event)
      return true
    }

    override fun onScroll(first: MotionEvent?, event: MotionEvent, distanceX: Float, distanceY: Float): Boolean {
      beginDrag(event)
      panX = (panX + distanceX).coerceIn(0f, maxX.toFloat())
      panY = (panY + distanceY).coerceIn(0f, maxY.toFloat())
      scrollTo(panX.roundToInt(), panY.roundToInt())
      return true
    }

    override fun onFling(first: MotionEvent?, event: MotionEvent, velocityX: Float, velocityY: Float): Boolean {
      scroller.fling(scrollX, scrollY, -velocityX.roundToInt(), -velocityY.roundToInt(), 0, maxX, 0, maxY)
      postInvalidateOnAnimation()
      return true
    }
  }).apply { setIsLongpressEnabled(false) }

  init {
    isHorizontalScrollBarEnabled = true
    isVerticalScrollBarEnabled = true
    clipChildren = true
  }

  private val contentWidth get() = getChildAt(0)?.width ?: 0
  private val contentHeight get() = getChildAt(0)?.height ?: 0
  private val maxX get() = (contentWidth - width).coerceAtLeast(0)
  private val maxY get() = (contentHeight - height).coerceAtLeast(0)

  fun setPanningEnabled(enabled: Boolean) {
    if (panningEnabled == enabled) return
    cancelInteraction()
    panningEnabled = enabled
    sendAccessibilityEvent(AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED)
  }

  fun setFocusTarget(target: String?) {
    if (focusTarget != target) focusedCell = null
    focusTarget = target
    postInvalidateOnAnimation()
  }

  private fun beginDrag(event: MotionEvent) {
    if (dragging) return
    dragging = true
    parent?.requestDisallowInterceptTouchEvent(true)
    NativeGestureUtil.notifyNativeGestureStarted(this, event)
  }

  private fun cancelInteraction() {
    scroller.forceFinished(true)
    val now = SystemClock.uptimeMillis()
    val cancel = MotionEvent.obtain(now, now, MotionEvent.ACTION_CANCEL, 0f, 0f, 0)
    detector.onTouchEvent(cancel)
    if (dragging) NativeGestureUtil.notifyNativeGestureEnded(this, cancel)
    cancel.recycle()
    dragging = false
    interceptedEvent = false
    parent?.requestDisallowInterceptTouchEvent(false)
  }

  override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
    if (!panningEnabled) return false
    detector.onTouchEvent(event)
    interceptedEvent = dragging
    return dragging
  }

  override fun onTouchEvent(event: MotionEvent): Boolean {
    if (!panningEnabled) return false
    // The first intercepted event already reached GestureDetector above.
    if (!interceptedEvent) detector.onTouchEvent(event)
    interceptedEvent = false
    if (event.actionMasked == MotionEvent.ACTION_UP || event.actionMasked == MotionEvent.ACTION_CANCEL) {
      if (dragging) NativeGestureUtil.notifyNativeGestureEnded(this, event)
      dragging = false
      parent?.requestDisallowInterceptTouchEvent(false)
      if (event.actionMasked == MotionEvent.ACTION_CANCEL) scroller.forceFinished(true)
    }
    return true
  }

  override fun scrollTo(x: Int, y: Int) {
    super.scrollTo(x.coerceIn(0, maxX), y.coerceIn(0, maxY))
  }

  override fun computeScroll() {
    if (scroller.computeScrollOffset()) {
      scrollTo(scroller.currX, scroller.currY)
      postInvalidateOnAnimation()
    }
  }

  override fun computeHorizontalScrollRange() = contentWidth.coerceAtLeast(width)
  override fun computeVerticalScrollRange() = contentHeight.coerceAtLeast(height)
  override fun computeHorizontalScrollOffset() = scrollX
  override fun computeVerticalScrollOffset() = scrollY
  override fun canScrollHorizontally(direction: Int) = panningEnabled && if (direction < 0) scrollX > 0 else scrollX < maxX
  override fun canScrollVertically(direction: Int) = panningEnabled && if (direction < 0) scrollY > 0 else scrollY < maxY

  override fun onScrollChanged(x: Int, y: Int, oldX: Int, oldY: Int) {
    super.onScrollChanged(x, y, oldX, oldY)
    awakenScrollBars()
    sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SCROLLED)
  }

  private fun constrainAndReveal() {
    if (scrollX > maxX || scrollY > maxY) scroller.forceFinished(true)
    scrollTo(scrollX, scrollY)
    val target = focusTarget ?: return
    // Reuse the view across repaints, but discard a removed/replaced cell.
    var ancestor = focusedCell?.parent
    while (ancestor != null && ancestor !== this) ancestor = ancestor.parent
    if (ancestor !== this) focusedCell = ReactFindViewUtil.findView(this, target)
    focusedCell?.let { revealChild(it) }
  }

  private fun revealOffset(offset: Int, start: Int, end: Int, extent: Int): Int = when {
    start < offset || end - start > extent -> start
    end > offset + extent -> end - extent
    else -> offset
  }

  private fun revealRect(rect: Rect): Boolean {
    val x = revealOffset(scrollX, rect.left, rect.right, width).coerceIn(0, maxX)
    val y = revealOffset(scrollY, rect.top, rect.bottom, height).coerceIn(0, maxY)
    if (x == scrollX && y == scrollY) return false
    scroller.forceFinished(true)
    scrollTo(x, y)
    return true
  }

  private fun revealChild(child: View) {
    if (child.width <= 0 || child.height <= 0 || width <= 0 || height <= 0) return
    child.getDrawingRect(focusRect)
    offsetDescendantRectToMyCoords(child, focusRect)
    revealRect(focusRect)
  }

  override fun requestChildRectangleOnScreen(child: View, rectangle: Rect, immediate: Boolean): Boolean {
    // Native-reader requests never replace the self-voicing cursor's viewport.
    if (!panningEnabled) return false
    focusRect.set(rectangle)
    offsetDescendantRectToMyCoords(child, focusRect)
    return revealRect(focusRect)
  }

  override fun requestChildFocus(child: View, focused: View) {
    super.requestChildFocus(child, focused)
    if (panningEnabled) revealChild(focused)
  }

  override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
    super.onInitializeAccessibilityNodeInfo(info)
    info.className = ScrollView::class.java.name
    info.isScrollable = panningEnabled && (maxX > 0 || maxY > 0)
    if (!panningEnabled) return
    if (scrollX > 0) info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_LEFT)
    if (scrollX < maxX) info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_RIGHT)
    if (scrollY > 0) info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_UP)
    if (scrollY < maxY) info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_DOWN)
    if (scrollY > 0 || scrollX > 0) info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_BACKWARD)
    if (scrollY < maxY || scrollX < maxX) info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD)
  }

  override fun performAccessibilityAction(action: Int, arguments: Bundle?): Boolean {
    if (!panningEnabled) return super.performAccessibilityAction(action, arguments)
    val target = when (action) {
      AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_LEFT.id -> Pair(scrollX - width, scrollY)
      AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_RIGHT.id -> Pair(scrollX + width, scrollY)
      AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_UP.id -> Pair(scrollX, scrollY - height)
      AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_DOWN.id -> Pair(scrollX, scrollY + height)
      AccessibilityNodeInfo.ACTION_SCROLL_FORWARD -> if (scrollY < maxY) Pair(scrollX, scrollY + height) else Pair(scrollX + width, scrollY)
      AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD -> if (scrollY > 0) Pair(scrollX, scrollY - height) else Pair(scrollX - width, scrollY)
      else -> return super.performAccessibilityAction(action, arguments)
    }
    val x = target.first.coerceIn(0, maxX)
    val y = target.second.coerceIn(0, maxY)
    if (x == scrollX && y == scrollY) return false
    scroller.startScroll(scrollX, scrollY, x - scrollX, y - scrollY)
    postInvalidateOnAnimation()
    return true
  }

  override fun onInitializeAccessibilityEvent(event: AccessibilityEvent) {
    super.onInitializeAccessibilityEvent(event)
    event.className = ScrollView::class.java.name
    event.isScrollable = panningEnabled && (maxX > 0 || maxY > 0)
    event.scrollX = scrollX
    event.scrollY = scrollY
    event.maxScrollX = maxX
    event.maxScrollY = maxY
  }

  override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    viewTreeObserver.addOnPreDrawListener(layoutListener)
    postInvalidateOnAnimation()
  }

  override fun onDetachedFromWindow() {
    viewTreeObserver.removeOnPreDrawListener(layoutListener)
    cancelInteraction()
    focusedCell = null
    super.onDetachedFromWindow()
  }
}
