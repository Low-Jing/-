<template>
  <view class="container">
    <view class="hero-card">
      <view class="badge" style="background: rgba(255,255,255,0.18); margin-bottom: 16rpx;">今日健康主场</view>
      <view class="page-title">你好，{{ username || '同学' }}</view>
      <view class="page-desc">把训练、饮食和连续打卡放在同一个仪表盘里，做成更像产品的毕设首页。</view>
      <view class="grid-2" style="margin-top: 24rpx;">
        <view class="grid-item-2">
          <view class="kpi-card" style="background: rgba(255,255,255,0.16);">
            <view class="kpi-title">目标达成度</view>
            <view class="kpi-value">{{ progress }}%</view>
          </view>
        </view>
        <view class="grid-item-2">
          <view class="kpi-card" style="background: rgba(255,255,255,0.16);">
            <view class="kpi-title">连续打卡</view>
            <view class="kpi-value">{{ streak }}天</view>
          </view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="section-title">快捷功能</view>
      <view class="grid-4">
        <view class="grid-item-4" v-for="item in quickList" :key="item.text" @click="goQuick(item)">
          <view class="quick-item">
            <view class="quick-icon">{{ item.icon }}</view>
            <view class="quick-text">{{ item.text }}</view>
          </view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="section-title">今日推荐计划</view>
      <view class="section-subtitle">先基于内容做冷启动匹配，后续再叠加协同过滤增强。</view>
      <view v-if="latestPlan && latestPlan.id">
        <view class="list-card">
          <view class="course-title">训练建议</view>
          <view class="course-meta">{{ latestPlan.exercise_text }}</view>
        </view>
        <view class="list-card">
          <view class="course-title">饮食建议</view>
          <view class="course-meta">{{ latestPlan.diet_text }}</view>
        </view>
        <view class="list-card">
          <view class="course-title">调整建议</view>
          <view class="course-meta">{{ latestPlan.suggestion }}</view>
        </view>
      </view>
      <view v-else class="empty">暂时还没有计划，先点下面按钮生成一份。</view>
      <view class="grid-2">
        <view class="grid-item-2"><view class="btn" @click="generatePlan">生成今日计划</view></view>
        <view class="grid-item-2"><view class="btn btn-light" @click="goPlan">查看计划中心</view></view>
      </view>
    </view>
  </view>
</template>

<script>
import { requestSafe, request, getUserId, getUsername, ensureLogin } from '@/utils/request.js'
import { formatGoal, calcProgress, calcStreak, latestRecord } from '@/utils/helpers.js'

export default {
  data() {
    return {
      username: '',
      profile: {},
      latestPlan: {},
      healthRecords: [],
      checkins: [],
      quickList: [
        { icon: '🔥', text: '今日计划', url: '/pages/plan/plan', type: 'tab' },
        { icon: '🥗', text: '饮食建议', url: '/pages/plan/plan', type: 'tab' },
        { icon: '📈', text: '健康记录', url: '/pages/records/records', type: 'tab' },
        { icon: '🏅', text: '连续打卡', url: '/pages/mine/mine', type: 'tab' },
        { icon: '🧠', text: '算法说明', url: '/pages/plan/plan', type: 'tab' },
        { icon: '🌟', text: '发现内容', url: '/pages/discover/discover', type: 'tab' },
        { icon: '👤', text: '个人中心', url: '/pages/mine/mine', type: 'tab' },
        { icon: '⚡', text: '快速生成', action: 'generate' }
      ]
    }
  },
  computed: {
    goalText() {
      return formatGoal(this.profile.goal_type)
    },
    progress() {
      return calcProgress(this.profile.current_weight, this.profile.target_weight)
    },
    streak() {
      return calcStreak(this.checkins)
    },
    latestHealth() {
      return latestRecord(this.healthRecords)
    }
  },
  onShow() {
    if (!ensureLogin()) return
    this.username = getUsername()
    this.loadAll()
  },
  methods: {
    loadAll() {
      var userId = getUserId()
      var that = this
      requestSafe({ url: '/users/profile/?user_id=' + userId }, {}).then(function(res) { that.profile = res || {} })
      requestSafe({ url: '/plans/list/?user_id=' + userId }, []).then(function(res) { that.latestPlan = res && res.length ? res[0] : {} })
      requestSafe({ url: '/health/records/list/?user_id=' + userId }, []).then(function(res) { that.healthRecords = res || [] })
      requestSafe({ url: '/plans/checkins/list/?user_id=' + userId }, []).then(function(res) { that.checkins = res || [] })
    },
    goQuick(item) {
      if (item.action === 'generate') {
        this.generatePlan()
        return
      }
      if (item.type === 'tab') {
        uni.switchTab({ url: item.url })
      }
    },
    goPlan() {
      uni.switchTab({ url: '/pages/plan/plan' })
    },
    generatePlan() {
      var that = this
      request({
        url: '/plans/recommend/',
        method: 'POST',
        data: { user_id: getUserId() }
      }).then(function(data) {
        that.latestPlan = data || {}
        uni.showToast({ title: '计划已生成', icon: 'success' })
      }).catch(function(err) {
        console.log('generatePlan error =>', err)
        uni.showToast({ title: '生成失败，请检查后端', icon: 'none' })
      })
    }
  }
}
</script>

<style>
</style>
