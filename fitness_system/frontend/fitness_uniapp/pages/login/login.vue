<template>
  <view class="page">
    <view class="hero">
      <view class="hero-badge">FitLife</view>
      <view class="hero-title">健康体重管理健身系统</view>
      <view class="hero-subtitle">
        {{ isRegister ? '创建账号并完善健康档案，开启个性化管理' : '登录后查看个性化训练计划、健康记录与成长分析' }}
      </view>
    </view>

    <view class="card">
      <view class="tabs">
        <view
          class="tab"
          :class="{ active: !isRegister }"
          @click="switchMode(false)"
        >
          登录
        </view>
        <view
          class="tab"
          :class="{ active: isRegister }"
          @click="switchMode(true)"
        >
          注册
        </view>
      </view>

      <view class="section-title">
        {{ isRegister ? '注册账号' : '账号登录' }}
      </view>

      <view class="form-item">
        <text class="label">用户名</text>
        <input v-model="form.username" class="input" placeholder="请输入用户名" />
      </view>

      <view class="form-item">
        <text class="label">密码</text>
        <input v-model="form.password" class="input" password placeholder="请输入密码" />
      </view>

      <template v-if="isRegister">
        <view class="form-item">
          <text class="label">年龄</text>
          <input v-model="form.age" class="input" type="number" placeholder="如：22" />
        </view>

        <view class="form-item">
          <text class="label">性别</text>
          <picker :range="genderOptions" range-key="label" @change="onGenderChange">
            <view class="picker-value">
              {{ getGenderLabel(form.gender) || '请选择性别' }}
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="label">身高（cm）</text>
          <input v-model="form.height" class="input" type="digit" placeholder="如：170" />
        </view>

        <view class="form-item">
          <text class="label">当前体重（kg）</text>
          <input v-model="form.current_weight" class="input" type="digit" placeholder="如：65" />
        </view>

        <view class="form-item">
          <text class="label">目标体重（kg）</text>
          <input v-model="form.target_weight" class="input" type="digit" placeholder="如：60" />
        </view>

        <view class="form-item">
          <text class="label">目标类型</text>
          <picker :range="goalOptions" range-key="label" @change="onGoalChange">
            <view class="picker-value">
              {{ getGoalLabel(form.goal_type) || '请选择目标类型' }}
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="label">运动偏好</text>
          <input
            v-model="form.exercise_preference"
            class="input"
            placeholder="如：跑步,快走"
          />
        </view>

        <view class="form-item">
          <text class="label">饮食偏好</text>
          <input
            v-model="form.diet_preference"
            class="input"
            placeholder="如：高蛋白,清淡"
          />
        </view>

        <view class="form-item">
          <text class="label">厌恶项</text>
          <input
            v-model="form.dislike_items"
            class="input"
            placeholder="如：油炸食品"
          />
        </view>

        <view class="form-item">
          <text class="label">可用时间</text>
          <input
            v-model="form.available_time"
            class="input"
            placeholder="如：晚上30分钟"
          />
        </view>
      </template>

      <view class="btn btn-primary" @click="handleSubmit">
        {{ isRegister ? '注册' : '登录' }}
      </view>
    </view>
  </view>
</template>

<script>
import { request } from '@/utils/request.js'
import { setUserInfo } from '@/utils/session.js'

export default {
  data() {
    return {
      isRegister: false,
      genderOptions: [
        { label: '男', value: 'male' },
        { label: '女', value: 'female' }
      ],
      goalOptions: [
        { label: '减脂', value: 'lose_weight' },
        { label: '增肌', value: 'gain_muscle' },
        { label: '保持健康', value: 'maintain' }
      ],
      form: this.getDefaultForm()
    }
  },
  methods: {
    getDefaultForm() {
      return {
        username: '',
        password: '',
        age: '18',
        gender: 'male',
        height: '170',
        current_weight: '60',
        target_weight: '55',
        goal_type: 'lose_weight',
        exercise_preference: '跑步,快走',
        diet_preference: '高蛋白,清淡',
        dislike_items: '油炸食品',
        available_time: '晚上30分钟'
      }
    },

    switchMode(registerMode) {
      this.isRegister = registerMode
      this.form = this.getDefaultForm()
    },

    getGenderLabel(value) {
      const item = this.genderOptions.find(v => v.value === value)
      return item ? item.label : ''
    },

    getGoalLabel(value) {
      const item = this.goalOptions.find(v => v.value === value)
      return item ? item.label : ''
    },

    onGenderChange(e) {
      const index = Number(e.detail.value)
      this.form.gender = this.genderOptions[index].value
    },

    onGoalChange(e) {
      const index = Number(e.detail.value)
      this.form.goal_type = this.goalOptions[index].value
    },

    validateLoginForm() {
      if (!this.form.username) {
        uni.showToast({ title: '请输入用户名', icon: 'none' })
        return false
      }
      if (!this.form.password) {
        uni.showToast({ title: '请输入密码', icon: 'none' })
        return false
      }
      return true
    },

    validateRegisterForm() {
      if (!this.validateLoginForm()) return false

      if (!this.form.age) {
        uni.showToast({ title: '请输入年龄', icon: 'none' })
        return false
      }
      if (!this.form.height) {
        uni.showToast({ title: '请输入身高', icon: 'none' })
        return false
      }
      if (!this.form.current_weight) {
        uni.showToast({ title: '请输入当前体重', icon: 'none' })
        return false
      }
      if (!this.form.target_weight) {
        uni.showToast({ title: '请输入目标体重', icon: 'none' })
        return false
      }
      if (!this.form.goal_type) {
        uni.showToast({ title: '请选择目标类型', icon: 'none' })
        return false
      }
      return true
    },

    async handleSubmit() {
      if (this.isRegister) {
        await this.handleRegister()
      } else {
        await this.handleLogin()
      }
    },

    async handleLogin() {
      if (!this.validateLoginForm()) return

      try {
        const data = await request({
          url: '/users/login/',
          method: 'POST',
          data: {
            username: this.form.username,
            password: this.form.password
          }
        })

        setUserInfo(data)
        uni.showToast({ title: '登录成功', icon: 'success' })

        setTimeout(() => {
          uni.switchTab({
            url: '/pages/index/index'
          })
        }, 300)
      } catch (err) {
        uni.showToast({
          title: err?.data?.message || err?.data?.detail || '登录失败',
          icon: 'none'
        })
      }
    },

    async handleRegister() {
      if (!this.validateRegisterForm()) return

      try {
        await request({
          url: '/users/register/',
          method: 'POST',
          data: {
            username: this.form.username,
            password: this.form.password,
            age: Number(this.form.age),
            gender: this.form.gender,
            height: Number(this.form.height),
            current_weight: Number(this.form.current_weight),
            target_weight: Number(this.form.target_weight),
            goal_type: this.form.goal_type,
            exercise_preference: this.form.exercise_preference,
            diet_preference: this.form.diet_preference,
            dislike_items: this.form.dislike_items,
            available_time: this.form.available_time
          }
        })

        uni.showToast({
          title: '注册成功，请登录',
          icon: 'success'
        })

        const username = this.form.username
        this.switchMode(false)
        this.form.username = username
      } catch (err) {
        uni.showToast({
          title: err?.data?.message || err?.data?.detail || '注册失败',
          icon: 'none'
        })
      }
    }
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef4ff 0%, #f8fafc 100%);
  padding: 48rpx 28rpx;
  box-sizing: border-box;
}

.hero {
  padding: 24rpx 8rpx 40rpx;
}

.hero-badge {
  display: inline-block;
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: rgba(79, 70, 229, 0.12);
  color: #4f46e5;
  font-size: 24rpx;
  margin-bottom: 18rpx;
}

.hero-title {
  font-size: 44rpx;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.4;
}

.hero-subtitle {
  margin-top: 14rpx;
  font-size: 26rpx;
  color: #64748b;
  line-height: 1.7;
}

.card {
  background: #ffffff;
  border-radius: 28rpx;
  padding: 36rpx 28rpx;
  box-shadow: 0 16rpx 50rpx rgba(15, 23, 42, 0.08);
}

.tabs {
  display: flex;
  background: #f1f5f9;
  border-radius: 999rpx;
  padding: 8rpx;
  margin-bottom: 28rpx;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 18rpx 0;
  border-radius: 999rpx;
  color: #64748b;
  font-size: 28rpx;
}

.tab.active {
  background: #4f46e5;
  color: #ffffff;
  font-weight: 600;
}

.section-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 28rpx;
}

.form-item {
  margin-bottom: 22rpx;
}

.label {
  display: block;
  font-size: 26rpx;
  color: #334155;
  margin-bottom: 12rpx;
}

.input,
.picker-value {
  width: 100%;
  min-height: 88rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  border-radius: 20rpx;
  padding: 0 24rpx;
  box-sizing: border-box;
  font-size: 28rpx;
  color: #0f172a;
  display: flex;
  align-items: center;
}

.btn {
  height: 92rpx;
  border-radius: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 600;
  margin-top: 20rpx;
}

.btn-primary {
  background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
  color: #ffffff;
}
</style>