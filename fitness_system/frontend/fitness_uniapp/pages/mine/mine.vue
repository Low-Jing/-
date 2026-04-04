<template>
  <view class="container">
    <view class="hero-card">
      <view class="hero-top">
        <view>
          <view class="hero-tag">成长画像中心</view>
          <view class="hero-title">我的</view>
          <view class="hero-desc">把档案、互动、打卡、推荐阶段和成长徽章聚合到一个页面。</view>
        </view>
        <view class="hero-stage">{{ summary.stage || '内容推荐' }}</view>
      </view>

      <view class="user-row">
        <view class="avatar-circle">{{ avatarText }}</view>
        <view class="user-meta">
          <view class="user-name">{{ profile.username || '未登录用户' }}</view>
          <view class="user-sub">{{ goalText }} ｜ {{ profile.available_time || '晚间30分钟' }}</view>
          <view class="level-chip">Lv.{{ levelInfo.level }}</view>
        </view>
      </view>

      <view class="hero-grid">
        <view class="hero-metric">
          <view class="metric-label">成长积分</view>
          <view class="metric-value">{{ levelInfo.points }}</view>
        </view>
        <view class="hero-metric">
          <view class="metric-label">下一级还差</view>
          <view class="metric-value">{{ levelInfo.nextGap }}</view>
        </view>
        <view class="hero-metric">
          <view class="metric-label">累计打卡</view>
          <view class="metric-value">{{ growth.checkin_count || 0 }}</view>
        </view>
      </view>

      <view class="progress-wrap">
        <view class="progress-text">等级进度 {{ levelInfo.progress }}%</view>
        <view class="progress-bg">
          <view class="progress-bar" :style="{ width: levelInfo.progress + '%' }"></view>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">互动行为统计</view>
      <view class="stats-grid">
        <view class="stat-box blue">
          <view class="stat-name">已报名挑战</view>
          <view class="stat-value">{{ summary.challenge_count || 0 }}</view>
        </view>
        <view class="stat-box green">
          <view class="stat-name">已收藏课程</view>
          <view class="stat-value">{{ summary.course_favorite_count || 0 }}</view>
        </view>
        <view class="stat-box purple">
          <view class="stat-name">已收藏文章</view>
          <view class="stat-value">{{ summary.article_favorite_count || 0 }}</view>
        </view>
        <view class="stat-box orange">
          <view class="stat-name">已点赞动态</view>
          <view class="stat-value">{{ summary.feed_like_count || 0 }}</view>
        </view>
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
        <view class="kv-row"><text>连续天数</text><text>{{ growth.streak_days || 0 }}</text></view>
        <view class="kv-row"><text>互动总数</text><text>{{ levelInfo.points }}</text></view>
        <view class="kv-row"><text>推荐阶段</text><text>{{ summary.stage || '内容推荐' }}</text></view>
        <view class="kv-row"><text>行为关键词</text><text>{{ summary.behavior_keywords && summary.behavior_keywords.length ? summary.behavior_keywords.length + ' 个' : '暂无' }}</text></view>
        <view class="tag-list">
          <text v-for="(tag, index) in (summary.behavior_keywords || [])" :key="index" class="tag">{{ tag }}</text>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">成长徽章</view>
      <view class="badge-grid">
        <view
          v-for="(item, index) in badges"
          :key="index"
          class="badge-item"
          :class="{ active: item.active }"
        >
          <view class="badge-icon">{{ item.icon }}</view>
          <view class="badge-name">{{ item.name }}</view>
          <view class="badge-desc">{{ item.desc }}</view>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">最近互动记录</view>
      <view v-if="recentActions.length">
        <view v-for="(item, index) in recentActions" :key="index" class="timeline-item">
          <view class="timeline-dot"></view>
          <view class="timeline-content">
            <view class="timeline-title">{{ item.title }}</view>
            <view class="timeline-desc">{{ item.desc }}</view>
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
import { request, getUserId } from '@/utils/request.js'

export default {
  data() {
    return {
      userId: '',
      profile: {},
      summary: {},
      growth: {
        checkin_count: 0,
        streak_days: 0
      },
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
    },
    levelInfo() {
      var points = (this.summary.challenge_count || 0) * 3
        + (this.summary.course_favorite_count || 0) * 2
        + (this.summary.article_favorite_count || 0) * 2
        + (this.summary.feed_like_count || 0)
        + (this.growth.checkin_count || 0) * 2

      var level = 1
      if (points >= 10) level = 2
      if (points >= 20) level = 3
      if (points >= 35) level = 4
      if (points >= 50) level = 5

      var floorMap = { 1: 0, 2: 10, 3: 20, 4: 35, 5: 50 }
      var ceilMap = { 1: 10, 2: 20, 3: 35, 4: 50, 5: 80 }
      var floor = floorMap[level]
      var ceil = ceilMap[level]
      var progress = level === 5 ? 100 : Math.min(100, Math.round((points - floor) * 100 / (ceil - floor)))
      var nextGap = level === 5 ? 0 : Math.max(0, ceil - points)

      return {
        points: points,
        level: level,
        progress: progress,
        nextGap: nextGap
      }
    },
    badges() {
      var summary = this.summary || {}
      var growth = this.growth || {}
      return [
        {
          icon: '🔥',
          name: '打卡新星',
          desc: '累计打卡 3 次',
          active: (growth.checkin_count || 0) >= 3
        },
        {
          icon: '🏃',
          name: '挑战参与者',
          desc: '至少报名 1 个挑战',
          active: (summary.challenge_count || 0) >= 1
        },
        {
          icon: '🎓',
          name: '课程收藏家',
          desc: '收藏 2 门课程',
          active: (summary.course_favorite_count || 0) >= 2
        },
        {
          icon: '📚',
          name: '知识探索者',
          desc: '收藏 2 篇文章',
          active: (summary.article_favorite_count || 0) >= 2
        },
        {
          icon: '💬',
          name: '社区观察员',
          desc: '点赞 2 条动态',
          active: (summary.feed_like_count || 0) >= 2
        },
        {
          icon: '🧠',
          name: '推荐增强样本',
          desc: '互动总量达到 6 次',
          active: this.levelInfo.points >= 6
        }
      ]
    },
    recentActions() {
      var result = []
      var recent = this.summary.recent_actions || []
      for (var i = 0; i < recent.length; i++) {
        var item = recent[i]
        result.push({
          title: item.action || '互动行为',
          desc: item.target || ''
        })
      }
      return result
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
    this.loadCheckins()
  },
  methods: {
    loadProfile() {
      var that = this
      request({
        url: '/users/profile/?user_id=' + that.userId,
        method: 'GET'
      }).then(function(data) {
        that.profile = data || {}
      }).catch(function(err) {
        console.log('profile error =>', err)
      })
    },
    loadSummary() {
      var that = this
      request({
        url: '/discover/user-summary/?user_id=' + that.userId,
        method: 'GET'
      }).then(function(data) {
        that.summary = data || {}
      }).catch(function(err) {
        console.log('summary error =>', err)
      })
    },
    loadCheckins() {
      var that = this
      request({
        url: '/plans/checkins/list/?user_id=' + that.userId,
        method: 'GET'
      }).then(function(data) {
        var list = Array.isArray(data) ? data : []
        that.growth.checkin_count = list.length
        that.growth.streak_days = Math.min(7, list.length)
      }).catch(function(err) {
        console.log('checkin error =>', err)
      })
    },
    submitCheckin() {
      var that = this
      if (!that.checkinForm.content) {
        uni.showToast({ title: '请输入打卡内容', icon: 'none' })
        return
      }

      request({
        url: '/plans/list/?user_id=' + that.userId,
        method: 'GET'
      }).then(function(plans) {
        var planId = plans && plans.length ? plans[0].id : null
        if (!planId) {
          uni.showToast({ title: '请先生成计划', icon: 'none' })
          return
        }
        return request({
          url: '/plans/checkins/',
          method: 'POST',
          data: {
            user: that.userId,
            plan: planId,
            checkin_type: 'exercise',
            content: that.checkinForm.content,
            feeling: that.checkinForm.feeling || ''
          }
        })
      }).then(function(resp) {
        if (!resp) return
        uni.showToast({ title: '打卡成功', icon: 'success' })
        that.checkinForm.content = ''
        that.checkinForm.feeling = ''
        that.loadCheckins()
      }).catch(function(err) {
        console.log('submit checkin error =>', err)
        uni.showToast({ title: '打卡失败', icon: 'none' })
      })
    },
    goPlan() {
      uni.switchTab({ url: '/pages/plan/plan' })
    },
    logout() {
      uni.removeStorageSync('userInfo')
      uni.showToast({ title: '已退出', icon: 'success' })
      setTimeout(function() {
        uni.reLaunch({ url: '/pages/login/login' })
      }, 500)
    }
  }
}
</script>

<style>
.container { padding: 24rpx; }
.hero-card { background: linear-gradient(135deg, #4f46e5, #22c1dc); border-radius: 28rpx; padding: 28rpx; color: #fff; margin-bottom: 24rpx; }
.hero-top { display: flex; justify-content: space-between; align-items: flex-start; }
.hero-tag { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: rgba(255,255,255,0.18); font-size: 22rpx; margin-bottom: 14rpx; }
.hero-title { font-size: 42rpx; font-weight: 700; }
.hero-desc { font-size: 24rpx; opacity: 0.95; margin-top: 10rpx; }
.hero-stage { padding: 10rpx 18rpx; border-radius: 999rpx; background: rgba(255,255,255,0.18); font-size: 22rpx; }
.user-row { display: flex; align-items: center; margin-top: 24rpx; }
.avatar-circle { width: 92rpx; height: 92rpx; border-radius: 50%; background: rgba(255,255,255,0.22); text-align: center; line-height: 92rpx; font-size: 36rpx; font-weight: 700; margin-right: 18rpx; }
.user-name { font-size: 40rpx; font-weight: 700; }
.user-sub { font-size: 24rpx; margin-top: 6rpx; opacity: 0.95; }
.level-chip { display: inline-block; margin-top: 12rpx; padding: 6rpx 14rpx; border-radius: 999rpx; background: rgba(255,255,255,0.22); font-size: 22rpx; }
.hero-grid { display: flex; gap: 18rpx; margin-top: 24rpx; }
.hero-metric { flex: 1; background: rgba(255,255,255,0.14); border-radius: 20rpx; padding: 18rpx; }
.metric-label { font-size: 22rpx; }
.metric-value { font-size: 40rpx; font-weight: 700; margin-top: 6rpx; }
.progress-wrap { margin-top: 20rpx; }
.progress-text { font-size: 22rpx; margin-bottom: 10rpx; }
.progress-bg { height: 14rpx; background: rgba(255,255,255,0.25); border-radius: 999rpx; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #fef3c7, #ffffff); border-radius: 999rpx; }
.section-card { background: #fff; border-radius: 24rpx; padding: 24rpx; margin-bottom: 24rpx; box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05); }
.section-title { font-size: 34rpx; font-weight: 700; margin-bottom: 18rpx; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18rpx; }
.stat-box { color: #fff; border-radius: 20rpx; padding: 22rpx; }
.blue { background: linear-gradient(135deg, #3b82f6, #22c1dc); }
.green { background: linear-gradient(135deg, #0f766e, #2dd4bf); }
.purple { background: linear-gradient(135deg, #9333ea, #ec4899); }
.orange { background: linear-gradient(135deg, #f59e0b, #f97316); }
.stat-name { font-size: 24rpx; }
.stat-value { font-size: 44rpx; font-weight: 700; margin-top: 8rpx; }
.tips { color: #64748b; font-size: 24rpx; margin-top: 16rpx; }
.two-col { display: flex; gap: 18rpx; }
.half { flex: 1; }
.kv-row { display: flex; justify-content: space-between; margin-bottom: 16rpx; color: #334155; font-size: 28rpx; }
.tag-list { margin-top: 8rpx; }
.tag { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: #eef2ff; color: #4f46e5; font-size: 22rpx; margin-right: 10rpx; margin-bottom: 10rpx; }
.badge-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16rpx; }
.badge-item { background: #f8fafc; border-radius: 20rpx; padding: 18rpx; text-align: center; border: 2rpx solid transparent; }
.badge-item.active { background: linear-gradient(180deg, #eef2ff, #ffffff); border-color: #6366f1; }
.badge-icon { font-size: 38rpx; }
.badge-name { font-size: 26rpx; font-weight: 700; margin-top: 8rpx; }
.badge-desc { font-size: 22rpx; color: #64748b; margin-top: 6rpx; line-height: 1.5; }
.timeline-item { display: flex; align-items: flex-start; margin-bottom: 18rpx; }
.timeline-dot { width: 18rpx; height: 18rpx; border-radius: 50%; background: #4f46e5; margin-top: 10rpx; margin-right: 16rpx; }
.timeline-content { flex: 1; background: #f8fafc; border-radius: 18rpx; padding: 16rpx; }
.timeline-title { font-size: 28rpx; font-weight: 600; }
.timeline-desc { font-size: 24rpx; color: #64748b; margin-top: 8rpx; }
.input, .textarea { width: 100%; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 18rpx; padding: 18rpx 20rpx; box-sizing: border-box; margin-bottom: 18rpx; }
.textarea { min-height: 140rpx; }
.btn-row { display: flex; gap: 18rpx; }
.btn { text-align: center; border-radius: 18rpx; padding: 22rpx 0; font-weight: 700; font-size: 28rpx; margin-top: 8rpx; }
.primary { flex: 1; color: #fff; background: linear-gradient(90deg, #3b82f6, #6366f1); }
.light { flex: 1; color: #4f46e5; background: #eef2ff; }
.danger { color: #fff; background: linear-gradient(90deg, #ef4444, #f97316); }
.empty-text { text-align: center; color: #94a3b8; padding: 30rpx 0 10rpx; }
</style>