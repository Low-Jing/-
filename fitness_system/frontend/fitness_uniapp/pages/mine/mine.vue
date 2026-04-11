<template>
  <view class="container">
    <view class="card" style="background: linear-gradient(135deg,#4f46e5,#06b6d4); color:#fff;">
      <view class="small" style="opacity:0.9;">我的</view>
      <view style="display:flex; align-items:center; justify-content:space-between; margin-top:12rpx;">
        <view style="display:flex; align-items:center; gap:20rpx;">
          <view style="width:100rpx; height:100rpx; line-height:100rpx; border-radius:50%; text-align:center; background:rgba(255,255,255,0.16); font-size:42rpx; font-weight:700;">
            {{ avatarText }}
          </view>
          <view>
            <view class="title" style="margin-bottom:8rpx;">{{ profile.username || userInfo.username || '用户' }}</view>
            <view class="small">{{ profile.goal_type || '目标待完善' }} ｜ {{ profile.available_time || '时间待完善' }}</view>
          </view>
        </view>
        <view class="tag" style="background:rgba(255,255,255,0.16); color:#fff;">{{ growth.stage || '内容推荐' }}</view>
      </view>
    </view>

    <view class="card">
      <view class="subtitle">成长体系</view>
      <view class="row"><text class="label">成长积分</text><text>{{ growth.points || 0 }}</text></view>
      <view class="row"><text class="label">当前等级</text><text>Lv.{{ growth.level || 1 }} {{ growth.level_name || '新手启动' }}</text></view>
      <view class="row"><text class="label">连续天数</text><text>{{ growth.streak_days || 0 }}</text></view>
      <view style="height:14rpx; background:#e5e7eb; border-radius:999rpx; overflow:hidden; margin-top:16rpx;">
        <view :style="{ width: (growth.progress || 0) + '%', height:'100%', background:'linear-gradient(90deg,#4f46e5,#06b6d4)' }"></view>
      </view>
      <view class="small text-muted" style="margin-top:12rpx;">升级进度 {{ growth.progress || 0 }}%</view>
    </view>

    <view class="card">
      <view class="subtitle">互动行为统计</view>
      <view style="display:grid; grid-template-columns:repeat(2, 1fr); gap:16rpx;">
        <view class="card" style="margin-bottom:0; background:linear-gradient(135deg,#3b82f6,#06b6d4); color:#fff;">
          <view class="small">已报名挑战</view>
          <view style="font-size:44rpx; font-weight:700; margin-top:8rpx;">{{ growth.challenge_joined_count || 0 }}</view>
        </view>
        <view class="card" style="margin-bottom:0; background:linear-gradient(135deg,#0f766e,#34d399); color:#fff;">
          <view class="small">已收藏课程</view>
          <view style="font-size:44rpx; font-weight:700; margin-top:8rpx;">{{ growth.course_favorite_count || 0 }}</view>
        </view>
        <view class="card" style="margin-bottom:0; background:linear-gradient(135deg,#9333ea,#ec4899); color:#fff;">
          <view class="small">已收藏文章</view>
          <view style="font-size:44rpx; font-weight:700; margin-top:8rpx;">{{ growth.article_favorite_count || 0 }}</view>
        </view>
        <view class="card" style="margin-bottom:0; background:linear-gradient(135deg,#f59e0b,#f97316); color:#fff;">
          <view class="small">已点赞动态</view>
          <view style="font-size:44rpx; font-weight:700; margin-top:8rpx;">{{ growth.post_like_count || 0 }}</view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="subtitle">我的档案</view>
      <view class="row"><text class="label">年龄</text><text>{{ profile.age || '--' }}</text></view>
      <view class="row"><text class="label">性别</text><text>{{ profile.gender || '--' }}</text></view>
      <view class="row"><text class="label">身高</text><text>{{ profile.height ? profile.height + ' cm' : '--' }}</text></view>
      <view class="row"><text class="label">当前体重</text><text>{{ profile.current_weight ? profile.current_weight + ' kg' : '--' }}</text></view>
      <view class="row"><text class="label">目标体重</text><text>{{ profile.target_weight ? profile.target_weight + ' kg' : '--' }}</text></view>
    </view>

    <view class="card">
      <view class="subtitle">成长徽章</view>
      <view style="display:grid; grid-template-columns:repeat(2, 1fr); gap:16rpx;">
        <view v-for="(badge, index) in growth.badges || []" :key="index" class="card" :style="badge.earned ? 'margin-bottom:0; background:#eef2ff;' : 'margin-bottom:0; background:#f8fafc; opacity:0.65;'">
          <view style="font-weight:700;">{{ badge.name }}</view>
          <view class="small text-muted" style="margin-top:8rpx;">{{ badge.desc }}</view>
          <view class="small" style="margin-top:8rpx; color:#4f46e5;">{{ badge.earned ? '已点亮' : '未解锁' }}</view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="subtitle">最近互动记录</view>
      <template v-if="growth.recent_actions && growth.recent_actions.length">
        <view v-for="(item, index) in growth.recent_actions" :key="index" style="padding:18rpx 0; border-bottom:1px solid #f1f5f9;">
          <view style="font-weight:600;">{{ item.type }}</view>
          <view class="small" style="margin-top:6rpx;">{{ item.title }}</view>
          <view class="small text-muted" style="margin-top:6rpx;">{{ formatTime(item.time) }}</view>
        </view>
      </template>
      <view v-else class="empty">暂无互动记录</view>
    </view>

    <view class="card">
      <view class="subtitle">账号操作</view>
      <view class="btn btn-danger" style="margin-bottom:0;" @click="logout">退出登录</view>
    </view>
  </view>
</template>

<script>
import { getGrowthSummary } from '@/api/home.js'
import { getUserInfo, clearSession } from '@/utils/session.js'

export default {
  data() {
    return {
      userInfo: {},
      profile: {},
      growth: {
        points: 0,
        level: 1,
        level_name: '新手启动',
        progress: 0,
        stage: '内容推荐',
        challenge_joined_count: 0,
        course_favorite_count: 0,
        article_favorite_count: 0,
        post_like_count: 0,
        badges: [],
        recent_actions: []
      }
    }
  },
  computed: {
    avatarText() {
      const name = this.profile.username || this.userInfo.username || 'U'
      return String(name).slice(0, 1).toUpperCase()
    }
  },
  onShow() {
    this.userInfo = getUserInfo()
    if (!this.userInfo.user_id) {
      uni.reLaunch({ url: '/pages/login/login' })
      return
    }
    this.loadGrowth()
  },
  methods: {
    loadGrowth() {
      var that = this
      getGrowthSummary().then(function(data) {
        that.profile = data.profile || {}
        that.growth = data.growth || that.growth
      }).catch(function(err) {
        console.log('growth 加载失败 =>', err)
        uni.showToast({ title: '成长数据加载失败', icon: 'none' })
      })
    },
    formatTime(value) {
      if (!value) return '--'
      return String(value).replace('T', ' ').slice(0, 16)
    },
    logout() {
      clearSession()
      uni.showToast({ title: '已退出', icon: 'success' })
      setTimeout(function() {
        uni.reLaunch({ url: '/pages/login/login' })
      }, 500)
    }
  }
}
</script>

<style>
</style>
