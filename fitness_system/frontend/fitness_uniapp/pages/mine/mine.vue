<template>
  <view class="container">
    <view class="hero-card">
      <view class="page-title">我的</view>
      <view class="page-desc">个人档案、成长统计、互动行为和打卡反馈统一放到这里。</view>
      <view class="row" style="margin-top: 20rpx;">
        <view>
          <view style="font-size: 40rpx; font-weight: 800; color:#fff;">{{ profile.username || '-' }}</view>
          <view class="small" style="color:#e0f2fe; margin-top: 8rpx;">{{ goalText }} ｜ {{ profile.available_time || '-' }}</view>
        </view>
        <view class="badge" style="background: rgba(255,255,255,0.18); color:#fff;">{{ dashboard.recommendation_phase || '内容推荐' }}</view>
      </view>
    </view>

    <view class="card">
      <view class="section-title">互动行为统计</view>
      <view class="grid-2">
        <view class="grid-item-2"><view class="kpi-card" style="background:linear-gradient(135deg,#2563eb 0%,#06b6d4 100%);"><view class="kpi-title">已报名挑战</view><view class="kpi-value">{{ interaction.joined_challenges_count || 0 }}</view></view></view>
        <view class="grid-item-2"><view class="kpi-card" style="background:linear-gradient(135deg,#0f766e 0%,#14b8a6 100%);"><view class="kpi-title">已收藏课程</view><view class="kpi-value">{{ interaction.favorite_courses_count || 0 }}</view></view></view>
        <view class="grid-item-2"><view class="kpi-card" style="background:linear-gradient(135deg,#9333ea 0%,#ec4899 100%);"><view class="kpi-title">已收藏文章</view><view class="kpi-value">{{ interaction.favorite_articles_count || 0 }}</view></view></view>
        <view class="grid-item-2"><view class="kpi-card" style="background:linear-gradient(135deg,#f59e0b 0%,#f97316 100%);"><view class="kpi-title">已点赞动态</view><view class="kpi-value">{{ interaction.liked_posts_count || 0 }}</view></view></view>
      </view>
      <view class="small muted" style="margin-top: 12rpx;">这些行为会作为后期协同过滤增强的基础信号。</view>
    </view>

    <view class="grid-2">
      <view class="grid-item-2">
        <view class="card" style="height: 100%;">
          <view class="section-title">我的档案</view>
          <view class="row"><text class="muted">年龄</text><text class="value-strong">{{ profile.age || '-' }}</text></view>
          <view class="row"><text class="muted">性别</text><text class="value-strong">{{ profile.gender || '-' }}</text></view>
          <view class="row"><text class="muted">身高</text><text class="value-strong">{{ profile.height || '-' }} cm</text></view>
          <view class="row"><text class="muted">当前体重</text><text class="value-strong">{{ profile.current_weight || '-' }} kg</text></view>
          <view class="row"><text class="muted">目标体重</text><text class="value-strong">{{ profile.target_weight || '-' }} kg</text></view>
        </view>
      </view>
      <view class="grid-item-2">
        <view class="card" style="height: 100%;">
          <view class="section-title">成长概览</view>
          <view class="row"><text class="muted">累计打卡</text><text class="value-strong">{{ checkins.length }}</text></view>
          <view class="row"><text class="muted">连续天数</text><text class="value-strong">{{ streak }}</text></view>
          <view class="row"><text class="muted">互动总数</text><text class="value-strong">{{ interaction.interaction_total || 0 }}</text></view>
          <view class="row"><text class="muted">推荐阶段</text><text class="value-strong">{{ dashboard.recommendation_phase || '内容推荐' }}</text></view>
          <view style="margin-top: 16rpx;">
            <text class="tag" v-for="item in (dashboard.behavior_keywords || [])" :key="item">{{ item }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="section-title">今日打卡</view>
      <view class="label">打卡内容</view>
      <input class="input" v-model="checkin.content" placeholder="例如：完成 30 分钟跑步与拉伸" />
      <view class="label">主观感受</view>
      <input class="input" v-model="checkin.feeling" placeholder="例如：前半段很稳，后半段略疲劳" />
      <view class="grid-2">
        <view class="grid-item-2"><view class="btn" @click="submitCheckin">提交打卡</view></view>
        <view class="grid-item-2"><view class="btn btn-light" @click="goPlan">查看当前计划</view></view>
      </view>
    </view>

    <view class="card">
      <view class="section-title">最近互动</view>
      <view v-if="interaction.recent_actions && interaction.recent_actions.length">
        <view class="list-card" v-for="(item,index) in interaction.recent_actions" :key="index">
          <view class="row"><text class="muted">行为</text><text class="value-strong">{{ item.text }}</text></view>
          <view class="small muted">对象：{{ item.title }}</view>
        </view>
      </view>
      <view v-else class="empty">还没有互动行为，去发现页点一点更像完整产品。</view>
    </view>

    <view class="card">
      <view class="section-title">最近打卡记录</view>
      <view v-if="checkins.length">
        <view class="list-card" v-for="item in checkins" :key="item.id">
          <view class="row"><text class="muted">类型</text><text class="value-strong">{{ item.checkin_type }}</text></view>
          <view class="row"><text class="muted">内容</text><text class="value-strong">{{ item.content }}</text></view>
          <view class="small muted">感受：{{ item.feeling || '无' }}</view>
          <view class="small muted" style="margin-top: 8rpx;">时间：{{ item.created_at }}</view>
        </view>
      </view>
      <view v-else class="empty">暂无打卡记录</view>
      <view class="btn btn-danger" @click="logout">退出登录</view>
    </view>
  </view>
</template>

<script>
import { request, requestSafe, getUserId, ensureLogin, clearLogin } from '@/utils/request.js'
import { calcStreak, formatGoal } from '@/utils/helpers.js'

export default {
  data() {
    return {
      profile: {},
      latestPlan: {},
      checkins: [],
      interaction: {},
      dashboard: {},
      checkin: { content: '', feeling: '' }
    }
  },
  computed: {
    streak() {
      return calcStreak(this.checkins)
    },
    goalText() {
      return formatGoal(this.profile.goal_type)
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
      requestSafe({ url: '/users/profile/?user_id=' + userId }, {}).then(function(res) { that.profile = res || {} })
      requestSafe({ url: '/plans/list/?user_id=' + userId }, []).then(function(res) { that.latestPlan = res && res.length ? res[0] : {} })
      requestSafe({ url: '/plans/checkins/list/?user_id=' + userId }, []).then(function(res) { that.checkins = res || [] })
      requestSafe({ url: '/discover/user-summary/?user_id=' + userId }, {}).then(function(res) { that.interaction = res || {} })
      requestSafe({ url: '/plans/dashboard/?user_id=' + userId }, {}).then(function(res) { that.dashboard = res || {} })
    },
    submitCheckin() {
      var that = this
      if (!that.latestPlan || !that.latestPlan.id) {
        uni.showToast({ title: '请先生成计划', icon: 'none' })
        return
      }
      if (!that.checkin.content) {
        uni.showToast({ title: '请填写打卡内容', icon: 'none' })
        return
      }
      request({
        url: '/plans/checkins/',
        method: 'POST',
        data: {
          user: getUserId(),
          plan: that.latestPlan.id,
          checkin_type: 'exercise',
          content: that.checkin.content,
          feeling: that.checkin.feeling
        }
      }).then(function() {
        uni.showToast({ title: '打卡成功', icon: 'success' })
        that.checkin = { content: '', feeling: '' }
        that.loadAll()
      }).catch(function(err) {
        console.log('submit checkin error =>', err)
        uni.showToast({ title: '打卡失败', icon: 'none' })
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
      }, 300)
    }
  }
}
</script>

<style>
</style>
