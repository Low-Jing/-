<template>
  <view class="container">
    <view class="hero-card">
      <view class="badge" style="background: rgba(255,255,255,0.18); margin-bottom: 16rpx;">推荐算法增强入口</view>
      <view class="page-title">AI 训练计划</view>
      <view class="page-desc">前期以内容推荐为主，后期把挑战报名、内容收藏、社区点赞等行为接进来，形成协同过滤增强。</view>
    </view>

    <view class="card">
      <view class="section-title">推荐引擎状态</view>
      <view class="row"><text class="muted">当前阶段</text><text class="value-strong">{{ enginePhaseText }}</text></view>
      <view class="row"><text class="muted">报名挑战</text><text class="value-strong">{{ interactionCounts.joined_challenges || 0 }}</text></view>
      <view class="row"><text class="muted">收藏课程</text><text class="value-strong">{{ interactionCounts.favorite_courses || 0 }}</text></view>
      <view class="row"><text class="muted">收藏文章</text><text class="value-strong">{{ interactionCounts.favorite_articles || 0 }}</text></view>
      <view class="row"><text class="muted">点赞动态</text><text class="value-strong">{{ interactionCounts.liked_posts || 0 }}</text></view>
      <view style="margin-top: 16rpx;">
        <text class="tag" v-for="item in behaviorTags" :key="item">{{ item }}</text>
      </view>
      <view class="small muted" style="margin-top: 12rpx;">这些标签来自发现页互动行为，会用于后期推荐增强。</view>
    </view>

    <view class="card">
      <view class="section-title">算法解释</view>
      <view v-if="engine.reason_list && engine.reason_list.length">
        <view class="list-card" v-for="(item,index) in engine.reason_list" :key="index">
          <view class="course-title">理由 {{ index + 1 }}</view>
          <view class="course-meta">{{ item }}</view>
        </view>
      </view>
      <view v-else class="empty">暂未生成解释，先点下方按钮生成一份计划。</view>
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
      <view class="section-title">推荐预览</view>
      <view v-if="engine.exercise_text">
        <view class="list-card">
          <view class="course-title">候选训练</view>
          <view class="course-meta">{{ engine.exercise_text }}</view>
        </view>
        <view class="list-card">
          <view class="course-title">候选饮食</view>
          <view class="course-meta">{{ engine.diet_text }}</view>
        </view>
      </view>
      <view v-else class="empty">暂无预览信息</view>
    </view>
  </view>
</template>

<script>
import { request, requestSafe, getUserId, ensureLogin } from '@/utils/request.js'

export default {
  data() {
    return {
      latestPlan: {},
      engine: {},
      dashboard: {},
      exerciseList: [],
      foodList: []
    }
  },
  computed: {
    enginePhaseText() {
      if (this.engine.algorithm_type === 'hybrid_cf') return '内容推荐 + 协同过滤增强'
      return this.dashboard.recommendation_phase || '内容推荐'
    },
    interactionCounts() {
      return (this.engine.behavior_summary && this.engine.behavior_summary.interaction_counts) || this.dashboard.interaction_counts || {}
    },
    behaviorTags() {
      var summary = (this.engine.behavior_summary || {})
      var arr = []
      if (summary.exercise_keywords && summary.exercise_keywords.length) arr = arr.concat(summary.exercise_keywords)
      if (summary.diet_keywords && summary.diet_keywords.length) arr = arr.concat(summary.diet_keywords)
      if (!arr.length && this.dashboard.behavior_keywords) arr = this.dashboard.behavior_keywords
      return arr
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
      requestSafe({ url: '/plans/engine/?user_id=' + userId }, {}).then(function(res) {
        that.engine = res || {}
      })
      requestSafe({ url: '/plans/dashboard/?user_id=' + userId }, {}).then(function(res) {
        that.dashboard = res || {}
      })
    },
    generatePlan() {
      var that = this
      request({
        url: '/plans/recommend/',
        method: 'POST',
        data: {
          user_id: getUserId()
        }
      }).then(function(data) {
        that.latestPlan = data || {}
        that.loadAll()
        uni.showToast({ title: '计划已生成', icon: 'success' })
      }).catch(function(err) {
        console.log('generate plan error =>', err)
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
