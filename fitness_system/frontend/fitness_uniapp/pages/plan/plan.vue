<template>
  <view class="container">
    <view class="hero-card">
      <view class="hero-tag">个性化推荐引擎</view>
      <view class="hero-title">AI 训练计划</view>
      <view class="hero-desc">现在每次生成计划时，系统会结合你的目标、偏好、发现页互动行为以及最近计划历史做“轮换推荐”，不再固定推同一套。</view>
    </view>

    <view class="section-card">
      <view class="section-title">推荐引擎状态</view>
      <view class="kv-row"><text>当前阶段</text><text class="strong">{{ engine.stage || '内容推荐' }}</text></view>
      <view class="kv-row"><text>报名挑战</text><text class="strong">{{ engine.challenge_count || 0 }}</text></view>
      <view class="kv-row"><text>收藏课程</text><text class="strong">{{ engine.course_favorite_count || 0 }}</text></view>
      <view class="kv-row"><text>收藏文章</text><text class="strong">{{ engine.article_favorite_count || 0 }}</text></view>
      <view class="kv-row"><text>点赞动态</text><text class="strong">{{ engine.feed_like_count || 0 }}</text></view>

      <view class="progress-wrap">
        <view class="progress-label">协同过滤增强准备度 {{ engineProgress }}%</view>
        <view class="progress-bg"><view class="progress-bar" :style="{ width: engineProgress + '%' }"></view></view>
      </view>

      <view class="sub-title">行为关键词</view>
      <view class="tag-list">
        <text v-for="(tag, index) in (engine.behavior_keywords || [])" :key="index" class="tag">{{ tag }}</text>
      </view>

      <view class="sub-title">近期已推荐过</view>
      <view class="tag-list">
        <text v-for="(tag, index) in (engine.recent_exercises || [])" :key="'re' + index" class="tag gray">{{ tag }}</text>
        <text v-for="(tag, index) in (engine.recent_foods || [])" :key="'rf' + index" class="tag gray">{{ tag }}</text>
        <text v-if="!(engine.recent_exercises || []).length && !(engine.recent_foods || []).length" class="tips">暂无历史计划，当前会优先根据档案与偏好推荐。</text>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">算法解释</view>
      <view v-for="(item, index) in reasonList" :key="index" class="reason-item">
        <view class="reason-title">理由 {{ index + 1 }}</view>
        <view class="reason-desc">{{ item }}</view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">候选训练与饮食</view>
      <view class="sub-title">候选训练</view>
      <view class="tag-list"><text v-for="(item, index) in (engine.exercise_candidates || [])" :key="'e' + index" class="tag">{{ item }}</text></view>
      <view class="sub-title">候选饮食</view>
      <view class="tag-list"><text v-for="(item, index) in (engine.food_candidates || [])" :key="'f' + index" class="tag green">{{ item }}</text></view>
    </view>

    <view class="section-card">
      <view class="section-title">当前最新计划</view>
      <view v-if="latestPlan">
        <view class="plan-highlight">
          <view class="plan-badge">本次推荐结果</view>
          <view class="plan-main">{{ latestPlan.exercise_title || extractTitle(latestPlan.exercise_text, '今日训练：') }}</view>
          <view class="plan-sub">{{ latestPlan.food_name || extractTitle(latestPlan.diet_text, '今日饮食：推荐 ') }}</view>
        </view>
        <view class="plan-block">
          <view class="plan-label">训练卡片</view>
          <view class="plan-text">{{ latestPlan.exercise_text }}</view>
        </view>
        <view class="plan-block">
          <view class="plan-label">饮食卡片</view>
          <view class="plan-text">{{ latestPlan.diet_text }}</view>
        </view>
        <view class="plan-block">
          <view class="plan-label">执行建议</view>
          <view class="plan-text">{{ latestPlan.suggestion }}</view>
        </view>
      </view>
      <view v-else class="empty-text">暂无计划，请先生成一条计划。</view>

      <view class="btn-row">
        <view class="btn primary" @click="generatePlan">个性化生成今日计划</view>
        <view class="btn success" @click="goMine">去打卡</view>
      </view>
    </view>
  </view>
</template>

<script>
import { request } from '@/utils/request.js'
import { getUserId } from '@/utils/session.js'
import { getPlanEngine, getPlanList, generatePlan as generatePlanApi } from '@/api/plans.js'

export default {
  data() {
    return {
      userId: '',
      engine: {},
      latestPlan: null
    }
  },
  computed: {
    reasonList() {
      var reasons = this.engine.reasons || []
      return reasons.length ? reasons : ['目标类型匹配', '运动偏好匹配', '饮食目标匹配']
    },
    engineProgress() {
      var total = (this.engine.challenge_count || 0)
        + (this.engine.course_favorite_count || 0)
        + (this.engine.article_favorite_count || 0)
        + (this.engine.feed_like_count || 0)
      return Math.min(100, total * 15)
    }
  },
  onShow() {
    this.userId = getUserId()
    if (!this.userId) {
      uni.reLaunch({ url: '/pages/login/login' })
      return
    }
    this.loadEngine()
    this.loadPlans()
  },
  methods: {
    extractTitle(text, prefix) {
      if (!text) return ''
      var t = text.replace(prefix, '')
      return t.split('，')[0].split('。')[0]
    },
    loadEngine() {
      var that = this
      getPlanEngine(that.userId).then(function(data) {
        that.engine = data || {}
      }).catch(function(err) {
        console.log('engine error =>', err)
      })
    },
    loadPlans() {
      var that = this
      getPlanList(that.userId).then(function(data) {
        if (Array.isArray(data) && data.length) {
          that.latestPlan = data[0]
        } else {
          that.latestPlan = null
        }
      }).catch(function(err) {
        console.log('plan list error =>', err)
      })
    },
    generatePlan() {
      var that = this
      generatePlanApi(that.userId).then(function(data) {
        uni.showToast({ title: '计划已生成', icon: 'success' })
        that.latestPlan = data || null
        that.loadEngine()
        that.loadPlans()
      }).catch(function(err) {
        console.log('generate plan error =>', err)
        uni.showToast({ title: '生成失败', icon: 'none' })
      })
    },
    goMine() {
      uni.switchTab({ url: '/pages/mine/mine' })
    }
  }
}
</script>

<style>
.container { padding: 24rpx; }
.hero-card { background: linear-gradient(135deg, #4f46e5, #22c1dc); border-radius: 28rpx; padding: 28rpx; color: #fff; margin-bottom: 24rpx; }
.hero-tag { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: rgba(255,255,255,0.18); font-size: 22rpx; margin-bottom: 14rpx; }
.hero-title { font-size: 42rpx; font-weight: 700; }
.hero-desc { font-size: 24rpx; margin-top: 10rpx; line-height: 1.7; }
.section-card { background: #fff; border-radius: 24rpx; padding: 24rpx; margin-bottom: 24rpx; box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05); }
.section-title { font-size: 34rpx; font-weight: 700; margin-bottom: 18rpx; }
.kv-row { display: flex; justify-content: space-between; margin-bottom: 16rpx; color: #334155; font-size: 28rpx; }
.strong { font-weight: 700; }
.progress-wrap { margin-top: 18rpx; }
.progress-label { font-size: 24rpx; margin-bottom: 10rpx; color: #475569; }
.progress-bg { height: 14rpx; border-radius: 999rpx; background: #e2e8f0; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #22c1dc); }
.sub-title { font-size: 28rpx; font-weight: 600; margin-top: 8rpx; margin-bottom: 10rpx; }
.tag-list { margin-top: 12rpx; }
.tag { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: #eef2ff; color: #4f46e5; font-size: 22rpx; margin-right: 10rpx; margin-bottom: 10rpx; }
.tag.green { background: #ecfdf5; color: #059669; }
.tag.gray { background: #f1f5f9; color: #64748b; }
.tips { font-size: 24rpx; color: #94a3b8; }
.reason-item { background: #f8fafc; border-radius: 18rpx; padding: 18rpx; margin-bottom: 14rpx; }
.reason-title { font-size: 28rpx; font-weight: 700; margin-bottom: 8rpx; }
.reason-desc { font-size: 24rpx; color: #475569; line-height: 1.8; }
.plan-highlight { background: linear-gradient(135deg, #eff6ff, #ecfeff); border-radius: 18rpx; padding: 18rpx; margin-bottom: 14rpx; }
.plan-badge { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: #dbeafe; color: #2563eb; font-size: 22rpx; margin-bottom: 10rpx; }
.plan-main { font-size: 32rpx; font-weight: 700; color: #1e293b; }
.plan-sub { font-size: 24rpx; color: #475569; margin-top: 8rpx; }
.plan-block { background: #f8fafc; border-radius: 18rpx; padding: 18rpx; margin-bottom: 14rpx; }
.plan-label { font-size: 28rpx; font-weight: 700; margin-bottom: 10rpx; }
.plan-text { font-size: 24rpx; color: #475569; line-height: 1.8; }
.btn-row { display: flex; gap: 18rpx; margin-top: 18rpx; }
.btn { flex: 1; text-align: center; border-radius: 18rpx; padding: 22rpx 0; font-weight: 700; font-size: 28rpx; }
.primary { color: #fff; background: linear-gradient(90deg, #3b82f6, #6366f1); }
.success { color: #fff; background: linear-gradient(90deg, #10b981, #14b8a6); }
.empty-text { text-align: center; color: #94a3b8; padding: 30rpx 0; }
</style>
