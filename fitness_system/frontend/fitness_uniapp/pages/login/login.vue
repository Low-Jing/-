<template>
  <view class="container">
    <view class="hero-card" style="margin-top: 20rpx;">
      <view class="page-title">FitLife Pro</view>
      <view class="page-desc">训练计划、饮食推荐、打卡反馈、趋势追踪与内容发现统一到一个系统中。</view>
    </view>

    <view class="card">
      <view class="section-title">欢迎回来</view>
      <view class="label">用户名</view>
      <input class="input" v-model="form.username" placeholder="请输入用户名" />
      <view class="label">密码</view>
      <input class="input" v-model="form.password" password placeholder="请输入密码" />
      <view class="btn" @click="handleLogin">立即登录</view>
      <view class="btn btn-light" @click="fillDemo">填入测试账号</view>
    </view>
  </view>
</template>

<script>
import { request, saveLogin } from '@/utils/request.js'

export default {
  data() {
    return {
      form: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    fillDemo() {
      this.form.username = 'test_mysql'
      this.form.password = '12345678Aa'
    },
    handleLogin() {
      var that = this
      if (!that.form.username || !that.form.password) {
        uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
        return
      }
      request({
        url: '/users/login/',
        method: 'POST',
        data: that.form
      }).then(function(data) {
        saveLogin(data)
        uni.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(function() {
          uni.switchTab({ url: '/pages/index/index' })
        }, 300)
      }).catch(function(err) {
        var msg = '登录失败'
        if (err && err.data && err.data.message) msg = err.data.message
        uni.showToast({ title: msg, icon: 'none' })
      })
    }
  }
}
</script>

<style>
</style>
