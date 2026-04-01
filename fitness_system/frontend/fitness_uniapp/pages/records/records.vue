<template>
  <view class="container">
    <view class="hero-card">
      <view class="badge" style="background: rgba(255,255,255,0.18); margin-bottom: 16rpx;">数据驱动健康中心</view>
      <view class="page-title">健康记录与趋势分析</view>
      <view class="page-desc">把体重、BMI 和体脂估算串成一条可视化轨迹，让“记录”更像产品，而不是只显示一行表格。</view>
      <view class="grid-3" style="margin-top: 24rpx;">
        <view class="grid-item-3"><view class="kpi-card purple"><view class="kpi-title">最新体重</view><view class="kpi-value">{{ latestRecord ? latestRecord.weight : '--' }}</view><view class="kpi-sub">kg</view></view></view>
        <view class="grid-item-3"><view class="kpi-card blue"><view class="kpi-title">最新 BMI</view><view class="kpi-value">{{ latestRecord ? latestRecord.bmi : '--' }}</view><view class="kpi-sub">指数</view></view></view>
        <view class="grid-item-3"><view class="kpi-card cyan"><view class="kpi-title">近7天记录</view><view class="kpi-value">{{ recentCount }}</view><view class="kpi-sub">条</view></view></view>
      </view>
    </view>

    <view class="grid-2">
      <view class="grid-item-2">
        <view class="card">
          <view class="section-title">体型目标进度</view>
          <view class="row"><text class="muted">当前体重</text><text class="value-strong">{{ profile.current_weight || '--' }} kg</text></view>
          <view class="row"><text class="muted">目标体重</text><text class="value-strong">{{ profile.target_weight || '--' }} kg</text></view>
          <view class="row"><text class="muted">达成度</text><text class="value-strong">{{ goalProgress }}%</text></view>
          <view class="progress-track"><view class="progress-fill" :style="{ width: goalProgress + '%' }"></view></view>
          <view class="small muted" style="margin-top: 12rpx;">可以作为答辩时的“可视化反馈”展示。</view>
        </view>
      </view>
      <view class="grid-item-2">
        <view class="card">
          <view class="section-title">一周状态摘要</view>
          <view class="row"><text class="muted">平均体重</text><text class="value-strong">{{ weeklyAvgWeight }}</text></view>
          <view class="row"><text class="muted">平均体脂估算</text><text class="value-strong">{{ weeklyAvgFat }}</text></view>
          <view class="row"><text class="muted">趋势变化</text><text class="value-strong">{{ weightTrendText }}</text></view>
          <view class="row"><text class="muted">健康判断</text><text class="value-strong">{{ healthJudge }}</text></view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="row" style="margin-bottom: 16rpx;">
        <view class="section-title">趋势图</view>
        <view class="chip-group">
          <view class="chip" :class="{ active: chartMode === 'weight' }" @click="chartMode = 'weight'">体重</view>
          <view class="chip" :class="{ active: chartMode === 'body_fat' }" @click="chartMode = 'body_fat'">体脂估算</view>
          <view class="chip" :class="{ active: chartMode === 'bmi' }" @click="chartMode = 'bmi'">BMI</view>
        </view>
      </view>
      <view v-if="chartRecords.length >= 2" class="chart-box">
        <svg class="chart-svg" viewBox="0 0 700 240" preserveAspectRatio="none">
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#4f46e5" />
              <stop offset="100%" stop-color="#06b6d4" />
            </linearGradient>
          </defs>
          <line x1="50" y1="220" x2="650" y2="220" stroke="#dbeafe" stroke-width="2" />
          <line x1="50" y1="30" x2="50" y2="220" stroke="#e5e7eb" stroke-width="2" />
          <polygon :points="chartAreaPoints" fill="rgba(79,70,229,0.08)"></polygon>
          <polyline :points="chartPoints" fill="none" stroke="url(#lineGradient)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
          <g v-for="(p, index) in pointNodes" :key="index">
            <circle :cx="p.x" :cy="p.y" r="5" fill="#fff" stroke="#4f46e5" stroke-width="3"></circle>
            <text :x="p.x" :y="p.y - 10" text-anchor="middle" font-size="12" fill="#475569">{{ p.label }}</text>
            <text :x="p.x" y="236" text-anchor="middle" font-size="11" fill="#94a3b8">{{ p.dateLabel }}</text>
          </g>
        </svg>
      </view>
      <view v-else class="empty">暂无足够数据绘制趋势图，请先添加 2 条以上健康记录。</view>
    </view>

    <view class="card">
      <view class="section-title">新增健康记录</view>
      <view class="small muted" style="margin-bottom: 16rpx;">只需输入体重和当天状态。体脂率不再手填，系统会结合 BMI、年龄和性别自动估算。</view>
      <view class="label">体重（kg）</view>
      <input class="input" v-model="form.weight" placeholder="例如 59.5" type="digit" />
      <view class="label">训练/状态备注</view>
      <textarea class="input textarea" v-model="form.note" placeholder="例如：今天完成快走 40 分钟，状态不错"></textarea>
      <view class="btn" @click="submitRecord">保存健康记录</view>
    </view>

    <view class="card">
      <view class="section-title">记录时间线</view>
      <view v-if="records.length">
        <view class="timeline-item" v-for="item in records" :key="item.id">
          <view class="timeline-dot"></view>
          <view class="timeline-content">
            <view class="row">
              <view class="value-strong">{{ item.record_date }}</view>
              <view class="small muted">{{ item.created_at }}</view>
            </view>
            <view class="course-meta">体重：{{ item.weight }} kg ｜ BMI：{{ item.bmi }} ｜ 体脂估算：{{ item.body_fat }}%</view>
            <view class="small muted" v-if="item.note">备注：{{ item.note }}</view>
          </view>
        </view>
      </view>
      <view v-else class="empty">暂无健康记录</view>
    </view>
  </view>
</template>

<script>
import { request, getUserId, ensureLogin } from '@/utils/request.js'

export default {
  data() {
    return {
      userId: '',
      profile: {},
      records: [],
      chartMode: 'weight',
      form: {
        weight: '',
        note: ''
      }
    }
  },
  computed: {
    latestRecord() {
      return this.records.length ? this.records[0] : null
    },
    recentCount() {
      return this.records.slice(0, 7).length
    },
    goalProgress() {
      var current = Number(this.profile.current_weight || 0)
      var target = Number(this.profile.target_weight || 0)
      if (!current || !target) return 0
      if (current === target) return 100
      var diff = Math.abs(current - target)
      var baseline = Math.max(current, target)
      if (!baseline) return 0
      var progress = Math.round((1 - diff / baseline) * 100)
      if (progress < 0) progress = 0
      if (progress > 100) progress = 100
      return progress
    },
    weeklyRecords() {
      return this.records.slice(0, 7).reverse()
    },
    weeklyAvgWeight() {
      if (!this.weeklyRecords.length) return '--'
      var total = this.weeklyRecords.reduce(function(sum, item) {
        return sum + Number(item.weight || 0)
      }, 0)
      return (total / this.weeklyRecords.length).toFixed(1) + ' kg'
    },
    weeklyAvgFat() {
      var valid = this.weeklyRecords.filter(function(item) {
        return item.body_fat !== null && item.body_fat !== '' && !isNaN(Number(item.body_fat))
      })
      if (!valid.length) return '--'
      var total = valid.reduce(function(sum, item) {
        return sum + Number(item.body_fat || 0)
      }, 0)
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
    chartRecords() {
      return this.records.slice(0, 7).reverse()
    },
    pointNodes() {
      var list = this.chartRecords
      if (list.length < 2) return []

      var values = list.map(this.getChartValue)
      var max = Math.max.apply(null, values)
      var min = Math.min.apply(null, values)
      var gap = max - min || 1
      var startX = 55
      var endX = 635
      var startY = 45
      var endY = 205
      var stepX = (endX - startX) / (list.length - 1)

      return list.map(function(item, index) {
        var value = values[index]
        var x = startX + stepX * index
        var y = endY - ((value - min) / gap) * (endY - startY)
        return {
          x: Number(x.toFixed(2)),
          y: Number(y.toFixed(2)),
          label: isNaN(value) ? '--' : value.toFixed(1),
          dateLabel: item.record_date ? item.record_date.slice(5) : '--'
        }
      })
    },
    chartPoints() {
      return this.pointNodes.map(function(item) {
        return item.x + ',' + item.y
      }).join(' ')
    },
    chartAreaPoints() {
      if (!this.pointNodes.length) return ''
      var first = this.pointNodes[0]
      var last = this.pointNodes[this.pointNodes.length - 1]
      var main = this.pointNodes.map(function(item) {
        return item.x + ',' + item.y
      }).join(' ')
      return first.x + ',220 ' + main + ' ' + last.x + ',220'
    }
  },
  onShow() {
    this.userId = getUserId()
    if (!ensureLogin()) return
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
      request({
        url: '/users/profile/?user_id=' + that.userId,
        method: 'GET'
      }).then(function(data) {
        that.profile = data || {}
      }).catch(function(err) {
        console.log('加载档案失败 =>', err)
        uni.showToast({ title: '档案加载失败', icon: 'none' })
      })
    },
    loadRecords() {
      var that = this
      request({
        url: '/health/records/list/?user_id=' + that.userId,
        method: 'GET'
      }).then(function(data) {
        if (typeof data === 'string') {
          try {
            data = JSON.parse(data)
          } catch (e) {
            data = []
          }
        }
        that.records = Array.isArray(data) ? data : []
      }).catch(function(err) {
        console.log('加载记录失败 =>', err)
        uni.showToast({ title: '记录加载失败', icon: 'none' })
      })
    },
    submitRecord() {
      var that = this
      if (!that.form.weight) {
        uni.showToast({ title: '请输入体重', icon: 'none' })
        return
      }
      if (isNaN(Number(that.form.weight))) {
        uni.showToast({ title: '体重必须是数字', icon: 'none' })
        return
      }
      var weight = Number(that.form.weight)
      if (weight < 30 || weight > 200) {
        uni.showToast({ title: '体重请输入 30-200kg', icon: 'none' })
        return
      }
      request({
        url: '/health/records/',
        method: 'POST',
        data: {
          user: that.userId,
          weight: weight,
          note: that.form.note || ''
        }
      }).then(function() {
        uni.showToast({ title: '记录已保存', icon: 'success' })
        that.form = { weight: '', note: '' }
        that.loadRecords()
      }).catch(function(err) {
        console.log('保存健康记录失败 =>', err)
        var msg = '保存失败'
        if (err && err.data) {
          if (typeof err.data === 'string') {
            msg = err.data
          } else if (err.data.weight && err.data.weight[0]) {
            msg = err.data.weight[0]
          } else if (err.data.user && err.data.user[0]) {
            msg = err.data.user[0]
          }
        }
        uni.showToast({ title: msg, icon: 'none' })
      })
    }
  }
}
</script>

<style>
.progress-track {
  height: 12rpx;
  background: #dbeafe;
  border-radius: 999rpx;
  overflow: hidden;
  margin-top: 16rpx;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg,#14b8a6 0%,#3b82f6 100%);
  border-radius: 999rpx;
}
.chip-group {
  display: flex;
  gap: 12rpx;
}
.chip {
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 24rpx;
}
.chip.active {
  background: linear-gradient(90deg,#4f46e5 0%,#06b6d4 100%);
  color: #fff;
}
.chart-box {
  height: 320rpx;
}
.chart-svg {
  width: 100%;
  height: 100%;
}
.textarea {
  height: 160rpx;
  padding-top: 20rpx;
}
.timeline-item {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.timeline-dot {
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
  background: #4f46e5;
  margin-top: 14rpx;
  flex-shrink: 0;
}
.timeline-content {
  flex: 1;
  padding-bottom: 16rpx;
  border-bottom: 1px solid #eef2ff;
}
</style>
