<template>
  <view class="container">
    <view class="hero-card">
      <view class="hero-top">
        <view>
          <view class="hero-tag">成长画像中心</view>
          <view class="hero-title">我的</view>
          <view class="hero-desc">把档案、互动、打卡、成长等级和推荐阶段统一收口到一个页面。</view>
        </view>
        <view class="hero-stage">{{ summary.recommendation_phase || '内容推荐' }}</view>
      </view>

      <view class="user-row">
        <view class="avatar-circle">{{ avatarText }}</view>
        <view class="user-meta">
          <view class="user-name">{{ profile.username || '未登录用户' }}</view>
          <view class="user-sub">{{ goalText }} ｜ {{ profile.available_time || '晚间30分钟' }}</view>
          <view class="level-chip">Lv.{{ summary.level || 1 }} · {{ summary.level_name || '新手起步' }}</view>
        </view>
      </view>

      <view class="hero-grid">
        <view class="hero-metric">
          <view class="metric-label">成长积分</view>
          <view class="metric-value">{{ summary.points || 0 }}</view>
        </view>
        <view class="hero-metric">
          <view class="metric-label">下一级还差</view>
          <view class="metric-value">{{ summary.next_gap || 0 }}</view>
        </view>
        <view class="hero-metric">
          <view class="metric-label">累计打卡</view>
          <view class="metric-value">{{ summary.checkin_count || 0 }}</view>
        </view>
      </view>

      <view class="progress-wrap">
        <view class="progress-text">等级进度 {{ summary.progress || 0 }}%</view>
        <view class="progress-bg"><view class="progress-bar" :style="{ width: (summary.progress || 0) + '%' }"></view></view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">互动行为统计</view>
      <view class="stats-grid">
        <view class="stat-box blue"><view class="stat-name">已报名挑战</view><view class="stat-value">{{ summary.challenge_count || 0 }}</view></view>
        <view class="stat-box green"><view class="stat-name">已收藏课程</view><view class="stat-value">{{ summary.course_favorite_count || 0 }}</view></view>
        <view class="stat-box purple"><view class="stat-name">已收藏文章</view><view class="stat-value">{{ summary.article_favorite_count || 0 }}</view></view>
        <view class="stat-box orange"><view class="stat-name">已点赞动态</view><view class="stat-value">{{ summary.feed_like_count || 0 }}</view></view>
      </view>
      <view class="tips">这些行为会作为后期协同过滤增强的基础信号。</view>
    </view>

    <view class="two-col">
      <view class="section-card half">
        <view class="section-title">我的档案</view>
        <view class="kv-row"><text>年龄</text><text>{{ profile.age || '--' }}</text></view>
        <view class="kv-row"><text>性别</text><text>{{ profile.gender || '--' }}</text></view>
        <view class="kv-row"><text>身高</text><text>{{ profile.height || '--' }} cm</text></view>
        <view class="kv-row"><text>当前体重</text><text>{{ profile.current_weight || '--' }} kg</text></view>
        <view class="kv-row"><text>目标体重</text><text>{{ profile.target_weight || '--' }} kg</text></view>
      </view>

      <view class="section-card half">
        <view class="section-title">成长概览</view>
        <view class="kv-row"><text>连续天数</text><text>{{ summary.streak_days || 0 }}</text></view>
        <view class="kv-row"><text>互动总数</text><text>{{ summary.interaction_total || 0 }}</text></view>
        <view class="kv-row"><text>推荐阶段</text><text>{{ summary.recommendation_phase || '内容推荐' }}</text></view>
        <view class="kv-row"><text>行为关键词</text><text>{{ (summary.behavior_keywords || []).length ? (summary.behavior_keywords || []).length + ' 个' : '暂无' }}</text></view>
        <view class="tag-list"><text v-for="(tag, index) in (summary.behavior_keywords || [])" :key="index" class="tag">{{ tag }}</text></view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">成长徽章</view>
      <view class="badge-grid">
        <view v-for="(item, index) in (summary.badges || [])" :key="index" class="badge-item" :class="{ active: item.active }">
          <view class="badge-icon">{{ item.icon }}</view>
          <view class="badge-name">{{ item.name }}</view>
          <view class="badge-desc">{{ item.desc }}</view>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">最近互动记录</view>
      <view v-if="(summary.recent_actions || []).length">
        <view v-for="(item, index) in summary.recent_actions" :key="index" class="timeline-item">
          <view class="timeline-dot"></view>
          <view class="timeline-content">
            <view class="timeline-title">{{ item.action }}</view>
            <view class="timeline-desc">{{ item.desc || item.target }}</view>
            <view class="timeline-time">{{ item.time_text }}</view>
          </view>
        </view>
      </view>
      <view v-else class="empty-text">暂无互动记录</view>
    </view>

    <view class="section-card">
      <view class="section-title">今日打卡</view>
      <input v-model="checkinForm.content" class="input" placeholder="例如：完成 30 分钟跑步与拉伸" />
      <textarea v-model="checkinForm.feeling" class="textarea" placeholder="例如：前半段很稳，后半段略疲劳"></textarea>
      <view class="btn-row">
        <view class="btn primary" @click="submitCheckin">提交打卡</view>
        <view class="btn light" @click="goPlan">查看当前计划</view>
      </view>
      <view class="btn danger" @click="logout">退出登录</view>
    </view>
  </view>
</template>

<script>
import { clearLogin, getUserId } from '@/utils/request.js'
import { getMyProfile } from '@/api/user.js'
import { getDiscoverGrowthSummary } from '@/api/discover.js'
import { createCheckin, getPlanList } from '@/api/plans.js'

export default {
  data() {
    return {
      userId: '',
      profile: {},
      summary: {},
      checkinForm: {
        content: '',
        feeling: ''
      }
    }
  },
  computed: {
    avatarText() {
      var name = this.profile.username || 'U'
      return name.slice(0, 1).toUpperCase()
    },
    goalText() {
      var map = {
        lose_weight: '减脂塑形',
        gain_muscle: '增肌提升',
        keep_fit: '保持健康'
      }
      return map[this.profile.goal_type] || '健康管理'
    }
  },
  onShow() {
    this.userId = getUserId()
    if (!this.userId) {
      uni.reLaunch({ url: '/pages/login/login' })
      return
    }
    this.loadProfile()
    this.loadSummary()
  },
  methods: {
    loadProfile() {
      var that = this
      getMyProfile(that.userId).then(function(data) {
        that.profile = data || {}
      }).catch(function(err) {
        console.log('profile error =>', err)
      })
    },
    loadSummary() {
      var that = this
      getDiscoverGrowthSummary(that.userId).then(function(data) {
        that.summary = data || {}
      }).catch(function(err) {
        console.log('growth summary error =>', err)
      })
    },
    submitCheckin() {
      var that = this
      if (!that.checkinForm.content) {
        uni.showToast({ title: '请输入打卡内容', icon: 'none' })
        return
      }

      getPlanList(that.userId).then(function(plans) {
        var planId = plans && plans.length ? plans[0].id : null
        if (!planId) {
          uni.showToast({ title: '请先生成计划', icon: 'none' })
          return
        }
        return createCheckin({
          user: that.userId,
          plan: planId,
          checkin_type: 'exercise',
          content: that.checkinForm.content,
          feeling: that.checkinForm.feeling || ''
        })
      }).then(function(result) {
        if (!result) {
          return
        }
        uni.showToast({ title: '打卡成功', icon: 'success' })
        that.checkinForm = { content: '', feeling: '' }
        that.loadSummary()
      }).catch(function(err) {
        console.log('checkin error =>', err)
        uni.showToast({ title: err.message || '打卡失败', icon: 'none' })
      })
    },
    goPlan() {
      uni.switchTab({ url: '/pages/plan/plan' })
    },
    logout() {
      clearLogin()
      uni.showToast({ title: '已退出', icon: 'success' })
      setTimeout(function() {
        uni.reLaunch({ url: '/pages/login/login' })
      }, 400)
    }
  }
}
</script>

<style>
.container { padding: 24rpx; background: #f3f6fb; min-height: 100vh; }
.hero-card { background: linear-gradient(135deg, #4f46e5 0%, #0ea5e9 55%, #06b6d4 100%); border-radius: 28rpx; padding: 28rpx; color: #fff; box-shadow: 0 18rpx 44rpx rgba(59,130,246,0.18); margin-bottom: 24rpx; }
.hero-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 20rpx; }
.hero-tag { display: inline-block; padding: 8rpx 18rpx; background: rgba(255,255,255,0.18); border-radius: 999rpx; font-size: 22rpx; margin-bottom: 12rpx; }
.hero-title { font-size: 46rpx; font-weight: 800; }
.hero-desc { font-size: 24rpx; color: #e0f2fe; margin-top: 10rpx; line-height: 1.6; }
.hero-stage { padding: 10rpx 18rpx; border-radius: 999rpx; background: rgba(255,255,255,0.16); font-size: 24rpx; }
.user-row { display: flex; align-items: center; margin-top: 26rpx; }
.avatar-circle { width: 88rpx; height: 88rpx; border-radius: 50%; background: rgba(255,255,255,0.18); display: flex; align-items: center; justify-content: center; font-size: 38rpx; font-weight: 800; margin-right: 20rpx; }
.user-name { font-size: 40rpx; font-weight: 800; }
.user-sub { font-size: 24rpx; color: #dbeafe; margin-top: 6rpx; }
.level-chip { display: inline-block; margin-top: 12rpx; padding: 8rpx 16rpx; background: rgba(255,255,255,0.18); border-radius: 999rpx; font-size: 22rpx; }
.hero-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin-top: 24rpx; }
.hero-metric { background: rgba(255,255,255,0.14); border-radius: 20rpx; padding: 18rpx; }
.metric-label { font-size: 22rpx; color: #e0f2fe; }
.metric-value { font-size: 40rpx; font-weight: 800; margin-top: 10rpx; }
.progress-wrap { margin-top: 22rpx; }
.progress-text { font-size: 22rpx; color: #e0f2fe; margin-bottom: 10rpx; }
.progress-bg { height: 16rpx; background: rgba(255,255,255,0.16); border-radius: 999rpx; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #a7f3d0 0%, #fef08a 100%); border-radius: 999rpx; }
.section-card { background: #fff; border-radius: 24rpx; padding: 24rpx; box-shadow: 0 10rpx 24rpx rgba(15,23,42,0.05); margin-bottom: 24rpx; }
.section-title { font-size: 34rpx; font-weight: 800; color: #0f172a; margin-bottom: 18rpx; }
.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16rpx; }
.stat-box { border-radius: 22rpx; padding: 20rpx; color: #fff; }
.stat-box.blue { background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); }
.stat-box.green { background: linear-gradient(135deg, #0f766e 0%, #2dd4bf 100%); }
.stat-box.purple { background: linear-gradient(135deg, #9333ea 0%, #ec4899 100%); }
.stat-box.orange { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }
.stat-name { font-size: 24rpx; opacity: 0.95; }
.stat-value { font-size: 42rpx; font-weight: 800; margin-top: 12rpx; }
.tips { margin-top: 14rpx; color: #64748b; font-size: 24rpx; }
.two-col { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16rpx; }
.half { min-height: 280rpx; }
.kv-row { display: flex; justify-content: space-between; padding: 10rpx 0; color: #334155; font-size: 26rpx; }
.tag-list { display: flex; flex-wrap: wrap; gap: 12rpx; margin-top: 14rpx; }
.tag { padding: 8rpx 16rpx; border-radius: 999rpx; background: #eef2ff; color: #4f46e5; font-size: 22rpx; }
.badge-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; }
.badge-item { border-radius: 20rpx; border: 2rpx solid #e2e8f0; padding: 18rpx; text-align: center; background: #f8fafc; opacity: 0.65; }
.badge-item.active { background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%); border-color: #93c5fd; opacity: 1; }
.badge-icon { font-size: 34rpx; }
.badge-name { font-size: 24rpx; font-weight: 700; color: #0f172a; margin-top: 8rpx; }
.badge-desc { font-size: 20rpx; color: #64748b; margin-top: 8rpx; line-height: 1.5; }
.timeline-item { display: flex; gap: 16rpx; margin-bottom: 18rpx; }
.timeline-dot { width: 18rpx; height: 18rpx; border-radius: 50%; background: #4f46e5; margin-top: 12rpx; flex-shrink: 0; }
.timeline-content { flex: 1; background: #f8fafc; border-radius: 18rpx; padding: 16rpx; }
.timeline-title { font-size: 26rpx; font-weight: 700; color: #0f172a; }
.timeline-desc { font-size: 24rpx; color: #475569; margin-top: 8rpx; line-height: 1.6; }
.timeline-time { font-size: 22rpx; color: #94a3b8; margin-top: 10rpx; }
.input, .textarea { width: 100%; box-sizing: border-box; border-radius: 18rpx; border: 2rpx solid #e2e8f0; background: #f8fafc; padding: 20rpx; font-size: 28rpx; margin-top: 12rpx; }
.textarea { min-height: 150rpx; margin-top: 18rpx; }
.btn-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16rpx; margin-top: 18rpx; }
.btn { text-align: center; border-radius: 18rpx; padding: 22rpx 16rpx; font-size: 28rpx; font-weight: 700; }
.btn.primary { color: #fff; background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%); }
.btn.light { color: #334155; background: #e2e8f0; }
.btn.danger { color: #fff; background: linear-gradient(135deg, #ef4444 0%, #f97316 100%); margin-top: 16rpx; }
.empty-text { color: #94a3b8; text-align: center; padding: 30rpx 0; }
@media screen and (max-width: 768px) {
  .two-col, .badge-grid, .hero-grid, .stats-grid, .btn-row { grid-template-columns: 1fr; }
}
</style>
