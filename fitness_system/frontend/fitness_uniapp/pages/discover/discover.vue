<template>
  <view class="container">
    <view class="hero-card">
      <view class="badge" style="background: rgba(255,255,255,0.18); margin-bottom: 16rpx;">内容生态与互动模块</view>
      <view class="page-title">发现</view>
      <view class="page-desc">这页不只是展示内容，还加入了报名、收藏、点赞这些互动入口，后面可以接协同过滤增强。</view>
      <view class="row" style="margin-top: 24rpx; align-items: center;">
        <view>
          <view class="section-title" style="color:#fff; margin-bottom: 8rpx;">本周主题</view>
          <view style="color:#fff; font-weight: 700;">{{ theme.title }}</view>
        </view>
        <view style="color:#fff; max-width: 360rpx; text-align: right;">{{ theme.desc }}</view>
      </view>
    </view>

    <view class="card">
      <view class="section-title">功能频道</view>
      <view class="grid-4">
        <view class="grid-item-4" v-for="item in channels" :key="item.text">
          <view class="quick-item">
            <view class="quick-icon">{{ item.icon }}</view>
            <view class="quick-text">{{ item.text }}</view>
          </view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="row" style="margin-bottom: 12rpx;">
        <view class="section-title">热门挑战</view>
        <view class="small muted" @click="loadDiscover">刷新</view>
      </view>
      <view v-if="challenges.length">
        <view class="challenge-card" v-for="item in challenges" :key="item.id" :style="{ background: item.theme_color || defaultChallengeBg }">
          <view class="row" style="align-items:flex-start; margin-bottom: 12rpx;">
            <view style="flex:1;">
              <view class="course-title white">{{ item.title }}</view>
              <view class="course-meta white">{{ item.description }}</view>
            </view>
            <text class="badge-light">{{ item.tag || '挑战' }}</text>
          </view>
          <view class="row challenge-meta-row">
            <view class="course-meta white">参与人数 {{ item.people_text || item.total_participants || item.participant_count }}</view>
            <view class="course-meta white">连续 {{ item.days }} 天</view>
          </view>
          <view class="row" style="margin-top: 16rpx;">
            <view class="action-ghost">活动赛道</view>
            <view class="action-btn" :class="item.joined ? 'action-btn-active' : ''" @click="toggleChallenge(item)">
              {{ item.joined ? '已报名' : '立即报名' }}
            </view>
          </view>
        </view>
      </view>
      <view v-else class="empty">暂无挑战数据</view>
    </view>

    <view class="card">
      <view class="section-title">专题课程</view>
      <view v-if="topics.length">
        <view class="list-card" v-for="item in topics" :key="item.id">
          <view class="row" style="margin-bottom: 12rpx;">
            <view class="course-title">{{ item.title }}</view>
            <view class="action-mini" :class="item.favorited ? 'action-mini-active' : ''" @click="toggleCourseFavorite(item)">
              {{ item.favorited ? '已收藏' : '收藏' }}
            </view>
          </view>
          <view class="course-meta">{{ item.description }}</view>
          <view style="margin-top: 12rpx;">
            <text class="tag" v-for="tag in item.tag_list" :key="tag">{{ tag }}</text>
          </view>
        </view>
      </view>
      <view v-else class="empty">暂无课程数据</view>
    </view>

    <view class="grid-2">
      <view class="grid-item-2">
        <view class="card" style="height: 100%;">
          <view class="section-title">营养知识</view>
          <view v-if="articles.length">
            <view class="list-card" v-for="item in articles" :key="item.id">
              <view class="row" style="margin-bottom: 8rpx; align-items:flex-start;">
                <view class="course-title" style="flex:1;">{{ item.title }}</view>
                <view class="action-mini" :class="item.favorited ? 'action-mini-active' : ''" @click="toggleArticleFavorite(item)">
                  {{ item.favorited ? '已收藏' : '收藏' }}
                </view>
              </view>
              <view class="course-meta">{{ item.summary }}</view>
              <view class="small muted" style="margin-top: 8rpx;">{{ item.category }} ｜ {{ item.read_minutes }} 分钟</view>
            </view>
          </view>
          <view v-else class="empty">暂无文章数据</view>
        </view>
      </view>
      <view class="grid-item-2">
        <view class="card" style="height: 100%;">
          <view class="section-title">社区动态</view>
          <view v-if="feeds.length">
            <view class="list-card" v-for="item in feeds" :key="item.id">
              <view class="row" style="margin-bottom: 8rpx;">
                <view class="course-title">{{ item.nickname }}</view>
                <view class="small muted">{{ item.time_text }}</view>
              </view>
              <view class="course-meta">{{ item.content }}</view>
              <view class="row" style="margin-top: 12rpx;">
                <view class="small muted">评论 {{ item.comment_count }}</view>
                <view class="action-mini" :class="item.liked ? 'action-mini-active' : ''" @click="togglePostLike(item)">
                  {{ item.liked ? '已点赞' : '点赞' }} {{ item.total_likes || item.like_count || 0 }}
                </view>
              </view>
            </view>
          </view>
          <view v-else class="empty">暂无社区动态</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { request, requestSafe, getUserId, ensureLogin } from '@/utils/request.js'

export default {
  data() {
    return {
      userId: '',
      theme: {
        title: '春季轻断食与快走周',
        desc: '挑战、课程、营养知识和社区互动放到一个页面，让系统更像完整产品。'
      },
      channels: [],
      challenges: [],
      topics: [],
      articles: [],
      feeds: [],
      defaultChallengeBg: 'linear-gradient(135deg,#2563eb 0%,#06b6d4 100%)'
    }
  },
  onShow() {
    if (!ensureLogin()) return
    this.userId = getUserId()
    this.loadDiscover()
  },
  methods: {
    loadDiscover() {
      var that = this
      requestSafe({
        url: '/discover/home/?format=json&user_id=' + that.userId,
        method: 'GET'
      }, {}).then(function(data) {
        that.theme = data.theme || that.theme
        that.channels = data.channels || []
        that.challenges = data.challenges || []
        that.topics = data.topics || []
        that.articles = data.articles || []
        that.feeds = data.feeds || []
      })
    },
    toggleChallenge(item) {
      var that = this
      request({
        url: '/discover/challenge/toggle-join/',
        method: 'POST',
        data: {
          user_id: that.userId,
          challenge_id: item.id
        }
      }).then(function(data) {
        item.joined = data.active
        item.people_text = data.people_text
        item.total_participants = data.count
        uni.showToast({ title: data.active ? '报名成功' : '已取消报名', icon: 'none' })
      }).catch(function(err) {
        console.log('toggle challenge error =>', err)
        uni.showToast({ title: '操作失败', icon: 'none' })
      })
    },
    toggleCourseFavorite(item) {
      var that = this
      request({
        url: '/discover/course/toggle-favorite/',
        method: 'POST',
        data: {
          user_id: that.userId,
          course_id: item.id
        }
      }).then(function(data) {
        item.favorited = data.active
        uni.showToast({ title: data.active ? '已收藏课程' : '已取消收藏', icon: 'none' })
      }).catch(function(err) {
        console.log('toggle course favorite error =>', err)
        uni.showToast({ title: '操作失败', icon: 'none' })
      })
    },
    toggleArticleFavorite(item) {
      var that = this
      request({
        url: '/discover/article/toggle-favorite/',
        method: 'POST',
        data: {
          user_id: that.userId,
          article_id: item.id
        }
      }).then(function(data) {
        item.favorited = data.active
        uni.showToast({ title: data.active ? '已收藏文章' : '已取消收藏', icon: 'none' })
      }).catch(function(err) {
        console.log('toggle article favorite error =>', err)
        uni.showToast({ title: '操作失败', icon: 'none' })
      })
    },
    togglePostLike(item) {
      var that = this
      request({
        url: '/discover/post/toggle-like/',
        method: 'POST',
        data: {
          user_id: that.userId,
          post_id: item.id
        }
      }).then(function(data) {
        item.liked = data.active
        item.total_likes = data.count
      }).catch(function(err) {
        console.log('toggle post like error =>', err)
        uni.showToast({ title: '操作失败', icon: 'none' })
      })
    }
  }
}
</script>

<style>
.challenge-card {
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  color: #fff;
  box-shadow: 0 16rpx 32rpx rgba(37,99,235,0.18);
}
.white,
.challenge-card .white {
  color: #fff;
}
.challenge-meta-row {
  opacity: 0.92;
}
.action-btn {
  padding: 12rpx 24rpx;
  border-radius: 999rpx;
  background: rgba(255,255,255,0.16);
  color: #fff;
  font-size: 24rpx;
}
.action-btn-active {
  background: #ffffff;
  color: #2563eb;
  font-weight: 700;
}
.action-ghost {
  padding: 12rpx 24rpx;
  border-radius: 999rpx;
  background: rgba(255,255,255,0.10);
  color: #fff;
  font-size: 24rpx;
}
.action-mini {
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 22rpx;
}
.action-mini-active {
  background: #4f46e5;
  color: #fff;
}
</style>
