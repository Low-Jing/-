<template>
  <view class="container">
    <view class="card" style="background: linear-gradient(135deg,#4f46e5,#06b6d4); color:#fff;">
      <view class="tag" style="background: rgba(255,255,255,0.16); color:#fff;">今日健康主场</view>
      <view class="title">你好，{{ dashboard.profile.username || userInfo.username || '用户' }}</view>
      <view class="small" style="opacity:0.92; margin-bottom: 20rpx;">
        把训练、饮食和连续打卡放在同一个仪表盘里，做成更像产品而不是简单页面。
      </view>
      <view style="display:flex; gap:20rpx;">
        <view class="card" style="flex:1; background: rgba(255,255,255,0.14); margin-bottom:0;">
          <view class="small">目标达成度</view>
          <view style="font-size:48rpx; font-weight:700; margin-top:12rpx;">{{ dashboard.goal_progress || 0 }}%</view>
        </view>
        <view class="card" style="flex:1; background: rgba(255,255,255,0.14); margin-bottom:0;">
          <view class="small">连续打卡</view>
          <view style="font-size:48rpx; font-weight:700; margin-top:12rpx;">{{ dashboard.streak_days || 0 }}天</view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="subtitle">快捷功能</view>
      <view style="display:grid; grid-template-columns:repeat(4, 1fr); gap:16rpx;">
        <view class="card" style="margin-bottom:0; text-align:center;" @click="goPlan">
          <view style="font-size:34rpx;">🔥</view>
          <view class="small">今日计划</view>
        </view>
        <view class="card" style="margin-bottom:0; text-align:center;" @click="goRecords">
          <view style="font-size:34rpx;">📈</view>
          <view class="small">健康记录</view>
        </view>
        <view class="card" style="margin-bottom:0; text-align:center;" @click="goDiscover">
          <view style="font-size:34rpx;">✨</view>
          <view class="small">发现内容</view>
        </view>
        <view class="card" style="margin-bottom:0; text-align:center;" @click="goMine">
          <view style="font-size:34rpx;">👤</view>
          <view class="small">个人中心</view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="subtitle">当前摘要</view>
      <view class="row"><text class="label">推荐阶段</text><text>{{ dashboard.engine_stage || '--' }}</text></view>
      <view class="row"><text class="label">最近记录数</text><text>{{ dashboard.recent_record_count || 0 }}</text></view>
      <view class="row"><text class="label">最新体重</text><text>{{ dashboard.latest_record ? dashboard.latest_record.weight + ' kg' : '--' }}</text></view>
      <view class="row"><text class="label">最新 BMI</text><text>{{ dashboard.latest_record ? dashboard.latest_record.bmi : '--' }}</text></view>
      <view style="margin-top: 16rpx;">
        <text v-for="(tag, index) in dashboard.quick_tags || []" :key="index" class="tag">{{ tag }}</text>
      </view>
    </view>

    <view class="card">
      <view class="subtitle">今日推荐计划</view>
      <template v-if="dashboard.latest_plan">
        <view class="card" style="margin-bottom:16rpx; background:#f8fafc;">
          <view class="small">训练建议</view>
          <view style="margin-top:10rpx;">{{ dashboard.latest_plan.exercise_text }}</view>
        </view>
        <view class="card" style="margin-bottom:16rpx; background:#f8fafc;">
          <view class="small">饮食建议</view>
          <view style="margin-top:10rpx;">{{ dashboard.latest_plan.diet_text }}</view>
        </view>
        <view class="card" style="background:#f8fafc;">
          <view class="small">执行建议</view>
          <view style="margin-top:10rpx;">{{ dashboard.latest_plan.suggestion }}</view>
        </view>
      </template>
      <view v-else class="empty">暂无计划，请去计划页生成</view>
      <view style="display:flex; gap:20rpx; margin-top: 20rpx;">
        <view class="btn" style="flex:1; margin-bottom:0;" @click="goPlan">查看计划中心</view>
        <view class="btn btn-secondary" style="flex:1; margin-bottom:0;" @click="goMine">查看成长中心</view>
      </view>
    </view>
  </view>
</template>

<script>
import { getDashboard } from '@/api/home.js'
import { getUserInfo } from '@/utils/session.js'

export default {
  data() {
    return {
      userInfo: {},
      dashboard: {
        profile: {},
        latest_record: null,
        latest_plan: null,
        goal_progress: 0,
        streak_days: 0,
        recent_record_count: 0,
        engine_stage: '',
        quick_tags: []
      }
    }
  },
  onShow() {
    this.userInfo = getUserInfo()
    if (!this.userInfo.user_id) {
      uni.reLaunch({ url: '/pages/login/login' })
      return
    }
    this.loadDashboard()
  },
  methods: {
    loadDashboard() {
      var that = this
      getDashboard().then(function(data) {
        that.dashboard = data || that.dashboard
      }).catch(function(err) {
        console.log('dashboard 加载失败 =>', err)
        uni.showToast({ title: '首页数据加载失败', icon: 'none' })
      })
    },
    goPlan() {
      uni.switchTab({ url: '/pages/plan/plan' })
    },
    goRecords() {
      uni.switchTab({ url: '/pages/records/records' })
    },
    goDiscover() {
      uni.switchTab({ url: '/pages/discover/discover' })
    },
    goMine() {
      uni.switchTab({ url: '/pages/mine/mine' })
    }
  }
}
</script>

<style>
</style>
