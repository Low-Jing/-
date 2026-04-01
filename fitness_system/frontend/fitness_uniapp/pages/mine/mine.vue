<template>
  <view class="container">
    <view class="hero-card">
      <view class="page-title">个人中心</view>
      <view class="page-desc">个人档案、打卡反馈、目标管理和成长信息。</view>
    </view>

    <view class="card">
      <view class="section-title">我的档案</view>
      <view class="row"><text class="muted">用户名</text><text class="value-strong">{{ profile.username || '-' }}</text></view>
      <view class="row"><text class="muted">年龄</text><text class="value-strong">{{ profile.age || '-' }}</text></view>
      <view class="row"><text class="muted">性别</text><text class="value-strong">{{ profile.gender || '-' }}</text></view>
      <view class="row"><text class="muted">身高</text><text class="value-strong">{{ profile.height || '-' }} cm</text></view>
      <view class="row"><text class="muted">目标</text><text class="value-strong">{{ goalText }}</text></view>
      <view class="row"><text class="muted">可用时间</text><text class="value-strong">{{ profile.available_time || '-' }}</text></view>
    </view>

    <view class="card">
      <view class="section-title">今日打卡</view>
      <view class="label">打卡内容</view>
      <input class="input" v-model="checkin.content" placeholder="例如：完成 30 分钟跑步" />
      <view class="label">主观感受</view>
      <input class="input" v-model="checkin.feeling" placeholder="例如：节奏稳定，后半程有点累" />
      <view class="grid-2">
        <view class="grid-item-2"><view class="btn" @click="submitCheckin">提交打卡</view></view>
        <view class="grid-item-2"><view class="btn btn-light" @click="goPlan">查看当前计划</view></view>
      </view>
      <view class="small muted" style="margin-top: 14rpx;">系统默认使用最新推荐计划进行打卡关联。</view>
    </view>

    <view class="card">
      <view class="section-title">成长概览</view>
      <view class="grid-2">
        <view class="grid-item-2">
          <view class="kpi-card" style="background: linear-gradient(135deg,#4f46e5 0%,#8b5cf6 100%);">
            <view class="kpi-title">累计打卡</view>
            <view class="kpi-value">{{ checkins.length }}</view>
          </view>
        </view>
        <view class="grid-item-2">
          <view class="kpi-card" style="background: linear-gradient(135deg,#0ea5e9 0%,#06b6d4 100%);">
            <view class="kpi-title">连续天数</view>
            <view class="kpi-value">{{ streak }}</view>
          </view>
        </view>
      </view>
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
