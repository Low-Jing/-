<template>
  <view class="container">
    <view class="hero-card">
      <view class="badge" style="background: rgba(255,255,255,0.18); margin-bottom: 16rpx;">算法升级版计划中心</view>
      <view class="page-title">AI 训练计划</view>
      <view class="page-desc">前期基于内容推荐，后期叠加协同过滤增强推荐质量。</view>
    </view>

    <view class="card">
      <view class="section-title">当前最新计划</view>
      <view v-if="latestPlan && latestPlan.id">
        <view class="list-card">
          <view class="course-title">训练卡片</view>
          <view class="course-meta">{{ latestPlan.exercise_text }}</view>
        </view>
        <view class="list-card">
          <view class="course-title">饮食卡片</view>
          <view class="course-meta">{{ latestPlan.diet_text }}</view>
        </view>
        <view class="list-card">
          <view class="course-title">执行建议</view>
          <view class="course-meta">{{ latestPlan.suggestion }}</view>
        </view>
      </view>
      <view v-else class="empty">还没有计划，点击下方按钮生成一份新的。</view>
      <view class="grid-2">
        <view class="grid-item-2"><view class="btn" @click="generatePlan">重新生成</view></view>
        <view class="grid-item-2"><view class="btn btn-green" @click="gotoMine">去打卡</view></view>
      </view>
    </view>

    <view class="card">
      <view class="section-title">动作库精选</view>
      <view class="list-card" v-for="item in exerciseList" :key="item.title">
        <view class="row">
          <view class="course-title">{{ item.title }}</view>
          <text class="badge-light">{{ item.fit_goal_text || item.fit_goal || '训练' }}</text>
        </view>
        <view class="course-meta">分类：{{ item.category || '综合' }} ｜ 时长：{{ item.duration_minutes || 20 }} 分钟 ｜ 消耗：{{ item.calories || 180 }} 千卡</view>
        <view class="course-meta">{{ item.description || '用于丰富前端展示与训练库层次。' }}</view>
      </view>
    </view>

    <view class="card">
      <view class="section-title">饮食库精选</view>
      <view class="list-card" v-for="item in foodList" :key="item.name">
        <view class="row">
          <view class="course-title">{{ item.name }}</view>
          <text class="badge-light">{{ item.preference_tag || '营养' }}</text>
        </view>
        <view class="course-meta">热量：{{ item.calories || 280 }} 千卡 ｜ 蛋白质：{{ item.protein || 20 }} g</view>
        <view class="course-meta">{{ item.description || '用于展示饮食推荐层次。' }}</view>
      </view>
    </view>
  </view>
</template>

<script>
import { requestSafe, request, getUserId, ensureLogin } from '@/utils/request.js'

export default {
  data() {
    return {
      latestPlan: {},
      exerciseList: [
        { title: '燃脂跑步', category: '有氧', duration_minutes: 30, calories: 280, fit_goal_text: '减脂', description: '适合减脂用户的基础有氧课程。' },
        { title: '自重 HIIT 循环', category: 'HIIT', duration_minutes: 20, calories: 240, fit_goal_text: '减脂', description: '提升代谢，适合居家训练。' },
        { title: '上肢力量入门', category: '力量', duration_minutes: 25, calories: 180, fit_goal_text: '增肌', description: '适合前期增肌和体态改善。' }
      ],
      foodList: [
        { name: '鸡胸肉藜麦沙拉', calories: 320, protein: 32, preference_tag: '高蛋白', description: '低油清淡，适合减脂期。' },
        { name: '牛肉全麦能量碗', calories: 420, protein: 35, preference_tag: '增肌', description: '提高蛋白摄入与饱腹感。' },
        { name: '酸奶水果坚果杯', calories: 260, protein: 18, preference_tag: '轻食', description: '适合早餐或加餐。' }
      ]
    }
  },
  onShow() {
    if (!ensureLogin()) return
    this.loadAll()
  },
  methods: {
    loadAll() {
      var userId = getUserId()
      var that = this
      requestSafe({ url: '/plans/list/?user_id=' + userId }, []).then(function(res) {
        that.latestPlan = res && res.length ? res[0] : {}
      })
      requestSafe({ url: '/plans/exercises/' }, that.exerciseList).then(function(res) {
        that.exerciseList = res && res.length ? res.slice(0, 6) : that.exerciseList
      })
      requestSafe({ url: '/plans/foods/' }, that.foodList).then(function(res) {
        that.foodList = res && res.length ? res.slice(0, 6) : that.foodList
      })
    },
    generatePlan() {
      var that = this
      request({
        url: '/plans/recommend/',
        method: 'POST',
        data: { user_id: getUserId() }
      }).then(function(data) {
        that.latestPlan = data || {}
        uni.showToast({ title: '已生成', icon: 'success' })
      }).catch(function(err) {
        console.log('plan generate error =>', err)
        uni.showToast({ title: '生成失败', icon: 'none' })
      })
    },
    gotoMine() {
      uni.switchTab({ url: '/pages/mine/mine' })
    }
  }
}
</script>

<style>
</style>
