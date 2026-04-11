<template>
  <view class="container">
    <view class="hero-card">
      <view class="hero-tag">数据驱动健康中心</view>
      <view class="hero-title">健康记录与趋势分析</view>
      <view class="hero-desc">把体重、BMI 和状态备注串成一条可视化轨迹，让“记录”更像产品，而不是只显示一行表格。</view>
      <view class="hero-grid">
        <view class="hero-metric"><view class="metric-label">最新体重</view><view class="metric-value">{{ latestRecord ? latestRecord.weight : '--' }}</view><view class="metric-unit">kg</view></view>
        <view class="hero-metric"><view class="metric-label">最新 BMI</view><view class="metric-value">{{ latestRecord ? latestRecord.bmi : '--' }}</view><view class="metric-unit">指数</view></view>
        <view class="hero-metric"><view class="metric-label">近7天记录</view><view class="metric-value">{{ recentCount }}</view><view class="metric-unit">条</view></view>
      </view>
    </view>

    <view class="two-col">
      <view class="section-card half">
        <view class="section-title">体型目标进度</view>
        <view class="kv-row"><text>当前体重</text><text>{{ profile.current_weight || '--' }} kg</text></view>
        <view class="kv-row"><text>目标体重</text><text>{{ profile.target_weight || '--' }} kg</text></view>
        <view class="kv-row"><text>达成度</text><text>{{ goalProgress }}%</text></view>
        <view class="progress-bg"><view class="progress-bar" :style="{ width: goalProgress + '%' }"></view></view>
        <view class="tips">可以作为答辩时的“可视化反馈”展示。</view>
      </view>
      <view class="section-card half">
        <view class="section-title">一周状态摘要</view>
        <view class="kv-row"><text>平均体重</text><text>{{ weeklyAvgWeight }}</text></view>
        <view class="kv-row"><text>平均体脂估算</text><text>{{ weeklyAvgFat }}</text></view>
        <view class="kv-row"><text>趋势变化</text><text>{{ weightTrendText }}</text></view>
        <view class="kv-row"><text>健康判断</text><text>{{ healthJudge }}</text></view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-head"><view class="section-title">趋势图</view><view class="tab-row"><text class="tab" :class="{active: chartMode==='weight'}" @click="chartMode='weight'">体重</text><text class="tab" :class="{active: chartMode==='body_fat'}" @click="chartMode='body_fat'">体脂估算</text><text class="tab" :class="{active: chartMode==='bmi'}" @click="chartMode='bmi'">BMI</text></view></view>
      <view v-if="pointNodes.length < 2" class="empty-text">暂无足够数据绘制趋势图，请先添加 2 条以上健康记录。</view>
      <view v-else class="chart-box">
        <svg class="chart-svg" viewBox="0 0 690 240">
          <defs><linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#4f46e5"></stop><stop offset="100%" stop-color="#06b6d4"></stop></linearGradient></defs>
          <polyline :points="chartAreaPoints" fill="rgba(79,70,229,0.08)" stroke="none"></polyline>
          <polyline :points="chartPoints" fill="none" stroke="url(#lineGradient)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
          <g v-for="(point, index) in pointNodes" :key="index">
            <circle :cx="point.x" :cy="point.y" r="5" fill="#fff" stroke="#4f46e5" stroke-width="3"></circle>
            <text :x="point.x" :y="point.y - 12" text-anchor="middle" font-size="12" fill="#334155">{{ point.label }}</text>
            <text :x="point.x" y="228" text-anchor="middle" font-size="11" fill="#94a3b8">{{ point.dateLabel }}</text>
          </g>
        </svg>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">新增健康记录</view>
      <view class="tips">除了体重，系统会自动计算 BMI、BMR 和体脂估算。</view>
      <view class="label">体重（kg）</view>
      <input v-model="form.weight" class="input" placeholder="例如 59.5" />
      <view class="label">训练/状态备注</view>
      <textarea v-model="form.note" class="textarea" placeholder="例如：今天完成快走 40 分钟，状态不错"></textarea>
      <view class="btn primary" @click="submitRecord">保存健康记录</view>
    </view>

    <view class="section-card">
      <view class="section-title">记录时间线</view>
      <view v-if="records.length">
        <view v-for="item in records" :key="item.id" class="timeline-item">
          <view class="timeline-dot"></view>
          <view class="timeline-content">
            <view class="timeline-title">{{ item.record_date }} ｜ {{ item.weight }} kg</view>
            <view class="timeline-desc">BMI：{{ item.bmi }} ｜ 体脂估算：{{ item.body_fat || '--' }}%</view>
            <view class="timeline-note">{{ item.note || '暂无备注' }}</view>
          </view>
        </view>
      </view>
      <view v-else class="empty-text">暂无健康记录</view>
    </view>
  </view>
</template>

<script>
import { request } from '@/utils/request.js'
import { getUserId } from '@/utils/session.js'
import { getMyProfile } from '@/api/user.js'
import { getRecordList, createRecord } from '@/api/records.js'

export default {
  data() {
    return {
      userId: '',
      profile: {},
      records: [],
      chartMode: 'weight',
      form: { weight: '', note: '' }
    }
  },
  computed: {
    latestRecord() { return this.records.length ? this.records[0] : null },
    recentCount() { return this.records.slice(0, 7).length },
    goalProgress() {
      var current = Number(this.profile.current_weight || 0)
      var target = Number(this.profile.target_weight || 0)
      if (!current || !target) return 0
      var diff = Math.abs(current - target)
      var baseline = Math.max(current, target)
      return Math.max(0, Math.min(100, Math.round((1 - diff / baseline) * 100)))
    },
    weeklyRecords() { return this.records.slice(0, 7).reverse() },
    weeklyAvgWeight() {
      if (!this.weeklyRecords.length) return '--'
      var total = this.weeklyRecords.reduce((sum, item) => sum + Number(item.weight || 0), 0)
      return (total / this.weeklyRecords.length).toFixed(1) + ' kg'
    },
    weeklyAvgFat() {
      var valid = this.weeklyRecords.filter(item => item.body_fat !== null && item.body_fat !== '' && !isNaN(Number(item.body_fat)))
      if (!valid.length) return '--'
      var total = valid.reduce((sum, item) => sum + Number(item.body_fat || 0), 0)
      return (total / valid.length).toFixed(1) + ' %'
    },
    weightTrendText() {
      if (this.weeklyRecords.length < 2) return '数据不足'
      var first = Number(this.weeklyRecords[0].weight || 0)
      var last = Number(this.weeklyRecords[this.weeklyRecords.length - 1].weight || 0)
      var diff = (last - first).toFixed(1)
      if (Number(diff) < 0) return '下降 ' + Math.abs(Number(diff)).toFixed(1) + ' kg'
      if (Number(diff) > 0) return '上升 ' + Number(diff).toFixed(1) + ' kg'
      return '基本稳定'
    },
    healthJudge() {
      if (!this.latestRecord) return '--'
      var bmi = Number(this.latestRecord.bmi || 0)
      if (!bmi) return '暂无判断'
      if (bmi < 18.5) return '偏瘦'
      if (bmi < 24) return '正常'
      if (bmi < 28) return '超重'
      return '肥胖风险'
    },
    chartRecords() { return this.records.slice(0, 7).reverse() },
    pointNodes() {
      var list = this.chartRecords
      if (list.length < 2) return []
      var values = list.map(this.getChartValue)
      var max = Math.max.apply(null, values)
      var min = Math.min.apply(null, values)
      var gap = max - min || 1
      var startX = 55, endX = 635, startY = 45, endY = 205
      var stepX = (endX - startX) / (list.length - 1)
      return list.map((item, index) => {
        var value = values[index]
        var x = startX + stepX * index
        var y = endY - ((value - min) / gap) * (endY - startY)
        return { x: Number(x.toFixed(2)), y: Number(y.toFixed(2)), label: isNaN(value) ? '--' : value.toFixed(1), dateLabel: item.record_date ? item.record_date.slice(5) : '--' }
      })
    },
    chartPoints() { return this.pointNodes.map(item => item.x + ',' + item.y).join(' ') },
    chartAreaPoints() {
      if (!this.pointNodes.length) return ''
      var first = this.pointNodes[0], last = this.pointNodes[this.pointNodes.length - 1]
      var main = this.pointNodes.map(item => item.x + ',' + item.y).join(' ')
      return first.x + ',220 ' + main + ' ' + last.x + ',220'
    }
  },
  onShow() {
    this.userId = getUserId()
    if (!this.userId) {
      uni.reLaunch({ url: '/pages/login/login' })
      return
    }
    this.loadProfile()
    this.loadRecords()
  },
  methods: {
    getChartValue(item) {
      if (this.chartMode === 'body_fat') return Number(item.body_fat || 0)
      if (this.chartMode === 'bmi') return Number(item.bmi || 0)
      return Number(item.weight || 0)
    },
    loadProfile() {
      var that = this
      getMyProfile(that.userId).then(function(data) { that.profile = data || {} }).catch(function(err) { console.log('profile error =>', err) })
    },
    loadRecords() {
      var that = this
      getRecordList(that.userId).then(function(data) { that.records = Array.isArray(data) ? data : [] }).catch(function(err) { console.log('records error =>', err) })
    },
    submitRecord() {
      var that = this
      if (!that.form.weight) { uni.showToast({ title: '请输入体重', icon: 'none' }); return }
      if (isNaN(Number(that.form.weight))) { uni.showToast({ title: '体重必须是数字', icon: 'none' }); return }
      var weight = Number(that.form.weight)
      if (weight < 30 || weight > 200) { uni.showToast({ title: '体重请输入 30-200kg', icon: 'none' }); return }
      createRecord({ user: that.userId, weight: weight, note: that.form.note || '' }).then(function() {
        uni.showToast({ title: '记录已保存', icon: 'success' })
        that.form = { weight: '', note: '' }
        that.loadRecords()
      }).catch(function(err) {
        uni.showToast({ title: err.message || '保存失败', icon: 'none' })
      })
    }
  }
}
</script>

<style>
.container { padding: 24rpx; background: #f3f6fb; min-height: 100vh; }
.hero-card { background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 55%, #06b6d4 100%); border-radius: 28rpx; padding: 28rpx; color: #fff; box-shadow: 0 18rpx 44rpx rgba(59,130,246,0.16); margin-bottom: 24rpx; }
.hero-tag { display: inline-block; padding: 8rpx 16rpx; background: rgba(255,255,255,0.16); border-radius: 999rpx; font-size: 22rpx; margin-bottom: 14rpx; }
.hero-title { font-size: 42rpx; font-weight: 800; }
.hero-desc { font-size: 24rpx; color: #e0f2fe; line-height: 1.7; margin-top: 10rpx; }
.hero-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin-top: 24rpx; }
.hero-metric { background: rgba(255,255,255,0.14); border-radius: 22rpx; padding: 18rpx; }
.metric-label { font-size: 22rpx; color: #dbeafe; }
.metric-value { font-size: 42rpx; font-weight: 800; margin-top: 10rpx; }
.metric-unit { font-size: 22rpx; color: #dbeafe; }
.two-col { display: flex; gap: 16rpx; margin-bottom: 24rpx; }
.half { flex: 1; }
.section-card { background: #fff; border-radius: 24rpx; padding: 24rpx; box-shadow: 0 10rpx 24rpx rgba(15,23,42,0.05); margin-bottom: 24rpx; }
.section-title { font-size: 34rpx; font-weight: 800; color: #0f172a; margin-bottom: 18rpx; }
.kv-row { display: flex; justify-content: space-between; margin-bottom: 14rpx; font-size: 28rpx; color: #334155; }
.progress-bg { height: 14rpx; border-radius: 999rpx; background: #e2e8f0; overflow: hidden; margin-top: 12rpx; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #34d399 0%, #3b82f6 100%); }
.tips { margin-top: 14rpx; font-size: 24rpx; color: #64748b; line-height: 1.6; }
.section-head { display: flex; justify-content: space-between; align-items: center; }
.tab-row { display: flex; gap: 12rpx; }
.tab { padding: 8rpx 18rpx; border-radius: 999rpx; background: #eef2ff; color: #6366f1; font-size: 22rpx; }
.tab.active { background: linear-gradient(90deg, #4f46e5, #0ea5e9); color: #fff; }
.chart-box { width: 100%; overflow: hidden; }
.chart-svg { width: 100%; height: 260rpx; }
.input, .textarea { width: 100%; box-sizing: border-box; border-radius: 18rpx; border: 1px solid #e2e8f0; background: #f8fafc; padding: 20rpx; font-size: 28rpx; margin-bottom: 18rpx; }
.textarea { min-height: 150rpx; }
.label { font-size: 28rpx; color: #334155; font-weight: 600; margin-bottom: 10rpx; }
.btn { text-align: center; border-radius: 18rpx; padding: 22rpx 0; font-size: 30rpx; font-weight: 700; }
.primary { color: #fff; background: linear-gradient(90deg, #3b82f6, #6366f1); }
.timeline-item { display: flex; position: relative; padding-left: 24rpx; margin-bottom: 20rpx; }
.timeline-dot { width: 14rpx; height: 14rpx; border-radius: 50%; background: #4f46e5; margin-top: 12rpx; margin-right: 16rpx; flex-shrink: 0; }
.timeline-content { flex: 1; background: #f8fafc; border-radius: 18rpx; padding: 16rpx; }
.timeline-title { font-size: 28rpx; font-weight: 700; color: #0f172a; }
.timeline-desc, .timeline-note { font-size: 24rpx; color: #64748b; margin-top: 8rpx; line-height: 1.6; }
.empty-text { text-align: center; color: #94a3b8; padding: 40rpx 0; }
</style>
