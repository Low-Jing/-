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
import { request } from '@/utils/request.js'
import { setUserInfo, clearSession } from '@/utils/session.js'

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
    fillTestAccount() {
      this.form.username = 'test_mysql'
      this.form.password = '12345678Aa'
    },
    handleLogin() {
      var that = this

      if (!that.form.username) {
        uni.showToast({
          title: '请输入用户名',
          icon: 'none'
        })
        return
      }

      if (!that.form.password) {
        uni.showToast({
          title: '请输入密码',
          icon: 'none'
        })
        return
      }

      // 先清掉旧会话，防止旧 user_id 干扰
      clearSession()

      request({
        url: '/users/login/',
        method: 'POST',
        data: {
          username: that.form.username,
          password: that.form.password
        }
      }).then(function(data) {
        console.log('login success =>', data)

        if (data && data.user_id) {
          setUserInfo(data)

          uni.showToast({
            title: '登录成功',
            icon: 'success'
          })

          setTimeout(function() {
            uni.switchTab({
              url: '/pages/index/index'
            })
          }, 500)
        } else {
          uni.showToast({
            title: (data && data.message) || '登录失败',
            icon: 'none'
          })
        }
      }).catch(function(err) {
        console.log('login error =>', err)

        var msg = '登录失败'
        if (err && err.data) {
          if (typeof err.data === 'string') {
            msg = err.data
          } else if (err.data.message) {
            msg = err.data.message
          } else if (err.data.detail) {
            msg = err.data.detail
          }
        }

        uni.showToast({
          title: msg,
          icon: 'none'
        })
      })
    }
  }
}
</script>

<style>
</style>
