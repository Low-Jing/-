<template>
  <view class="container">
    <view class="hero-card">
      <view class="hero-tag">内容生态与社区板块</view>
      <view class="hero-title">发现</view>
      <view class="hero-desc">去掉搜索，强化运营位、课程详情、知识正文和社区互动完整度，让发现页更像真正的内容型应用。</view>
    </view>

    <swiper class="banner-swiper" circular autoplay indicator-dots>
      <swiper-item v-for="(item, index) in banners" :key="index">
        <view class="banner-card">
          <view class="banner-badge">{{ item.badge }}</view>
          <view class="banner-title">{{ item.title }}</view>
          <view class="banner-subtitle">{{ item.subtitle }}</view>
        </view>
      </swiper-item>
    </swiper>

    <view class="section-card">
      <view class="section-head"><view class="section-title">为你精选</view><view class="tag-chip">个性化发现</view></view>
      <view class="pick-title">{{ editorPick.title || '本周精选' }}</view>
      <view class="tag-list"><text v-for="(tag, index) in (editorPick.keywords || [])" :key="index" class="tag">{{ tag }}</text></view>
      <view v-for="(item, index) in (editorPick.reasons || [])" :key="index" class="reason-line">{{ item }}</view>
    </view>

    <view class="section-card">
      <view class="section-title">功能频道</view>
      <view class="channel-grid">
        <view class="channel-item" v-for="(item, index) in channels" :key="index" @click="switchTab(item.anchor)">
          <view class="channel-icon">{{ item.icon }}</view>
          <view class="channel-text">{{ item.text }}</view>
        </view>
      </view>
    </view>

    <view class="tab-row">
      <view class="tab" :class="{active: activeTab==='all'}" @click="activeTab='all'">全部</view>
      <view class="tab" :class="{active: activeTab==='challenge'}" @click="activeTab='challenge'">挑战</view>
      <view class="tab" :class="{active: activeTab==='course'}" @click="activeTab='course'">课程</view>
      <view class="tab" :class="{active: activeTab==='article'}" @click="activeTab='article'">知识</view>
      <view class="tab" :class="{active: activeTab==='community'}" @click="activeTab='community'">社区</view>
    </view>

    <view v-if="activeTab==='all' || activeTab==='challenge'" class="section-card">
      <view class="section-head"><view class="section-title">热门挑战</view><view class="refresh-link" @click="loadDiscover">刷新</view></view>
      <view class="challenge-card" v-for="item in challenges" :key="'c'+item.id" @click="openDetail('challenge', item)">
        <view class="challenge-title">{{ item.title }}</view>
        <view class="challenge-desc">{{ item.description }}</view>
        <view class="challenge-meta"><text>{{ item.people_text || item.participant_text }}</text><text>{{ item.days }} 天</text></view>
      </view>
      <view v-if="!challenges.length" class="empty-text">暂无挑战数据</view>
    </view>

    <view v-if="activeTab==='all' || activeTab==='course'" class="section-card">
      <view class="section-title">专题课程</view>
      <view class="content-card" v-for="item in topics" :key="'t'+item.id" @click="openDetail('course', item)">
        <view class="content-title">{{ item.title }}</view>
        <view class="content-desc">{{ item.description }}</view>
      </view>
      <view v-if="!topics.length" class="empty-text">暂无课程数据</view>
    </view>

    <view v-if="activeTab==='all' || activeTab==='article'" class="section-card">
      <view class="section-title">营养知识</view>
      <view class="content-card" v-for="item in articles" :key="'a'+item.id" @click="openDetail('article', item)">
        <view class="content-title">{{ item.title }}</view>
        <view class="content-desc">{{ item.summary }}</view>
      </view>
      <view v-if="!articles.length" class="empty-text">暂无文章数据</view>
    </view>

    <view v-if="activeTab==='all' || activeTab==='community'" class="section-card">
      <view class="section-title">社区动态</view>
      <view class="content-card" v-for="item in feeds" :key="'f'+item.id" @click="openDetail('community', item)">
        <view class="content-title">{{ item.nickname }}</view>
        <view class="content-desc">{{ item.content }}</view>
      </view>
      <view v-if="!feeds.length" class="empty-text">暂无社区动态</view>
    </view>

    <view v-if="detailVisible" class="popup-mask" @click="closeDetail">
      <view class="popup-panel" @click.stop>
        <view class="popup-title">{{ detailItem.title || detailItem.nickname }}</view>
        <scroll-view scroll-y class="popup-scroll">
          <view v-if="detailType==='challenge'">
            <view class="popup-desc">{{ detailItem.detail_intro || detailItem.description }}</view>
            <view v-for="(block, idx) in (detailItem.detail_sections || [])" :key="idx" class="popup-block">
              <view class="popup-block-title">{{ block.title }}</view>
              <view class="popup-block-desc">{{ block.content }}</view>
            </view>
          </view>
          <view v-else-if="detailType==='course'">
            <view class="popup-desc">{{ detailItem.full_content || detailItem.description }}</view>
            <view v-for="(point, idx) in (detailItem.lesson_points || [])" :key="idx" class="popup-block-desc">• {{ point }}</view>
          </view>
          <view v-else-if="detailType==='article'">
            <view v-for="(block, idx) in (detailItem.article_blocks || [])" :key="idx" class="popup-block-desc">{{ block }}</view>
          </view>
          <view v-else>
            <view class="popup-desc">{{ detailItem.content }}</view>
            <view v-for="(comment, idx) in (detailItem.comments_preview || [])" :key="idx" class="popup-block-desc">{{ comment.nickname }}：{{ comment.text }}</view>
          </view>
        </scroll-view>
        <view class="btn-row">
          <view v-if="detailType==='challenge'" class="btn primary" @click="doToggleChallenge(detailItem)">{{ detailItem.joined ? '取消报名' : '立即报名' }}</view>
          <view v-if="detailType==='course'" class="btn primary" @click="doToggleCourse(detailItem)">{{ detailItem.favorited ? '取消收藏' : '收藏课程' }}</view>
          <view v-if="detailType==='article'" class="btn primary" @click="doToggleArticle(detailItem)">{{ detailItem.favorited ? '取消收藏' : '收藏文章' }}</view>
          <view v-if="detailType==='community'" class="btn primary" @click="doTogglePost(detailItem)">{{ detailItem.liked ? '取消点赞' : '点赞动态' }}</view>
          <view class="btn light" @click="closeDetail">关闭</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { request } from '@/utils/request.js'
import { getUserId } from '@/utils/session.js'
import { getDiscoverHome, toggleChallengeJoin, toggleCourseFavorite, toggleArticleFavorite, togglePostLike } from '@/api/discover.js'

export default {
  data() {
    return {
      userId: '', banners: [], channels: [], editorPick: {}, challenges: [], topics: [], articles: [], feeds: [], activeTab: 'all',
      detailVisible: false, detailType: '', detailItem: {}
    }
  },
  onShow() {
    this.userId = getUserId() || ''
    this.loadDiscover()
  },
  methods: {
    loadDiscover() {
      var that = this
      getDiscoverHome(that.userId).then(function(data) {
        that.banners = data.banners || []
        that.channels = data.channels || []
        that.editorPick = data.editor_pick || {}
        that.challenges = data.challenges || []
        that.topics = data.topics || []
        that.articles = data.articles || []
        that.feeds = data.feeds || []
      }).catch(function(err) {
        console.log('discover error =>', err)
        uni.showToast({ title: '发现页加载失败', icon: 'none' })
      })
    },
    switchTab(anchor) {
      this.activeTab = anchor || 'all'
    },
    openDetail(type, item) {
      this.detailType = type
      this.detailItem = Object.assign({}, item)
      this.detailVisible = true
    },
    closeDetail() {
      this.detailVisible = false
    },
    doToggleChallenge(item) {
      var that = this
      toggleChallengeJoin(that.userId, item.id).then(function(data) {
        uni.showToast({ title: data.active ? '报名成功' : '已取消报名', icon: 'none' })
        that.loadDiscover()
        that.detailItem.joined = !!data.active
      })
    },
    doToggleCourse(item) {
      var that = this
      toggleCourseFavorite(that.userId, item.id).then(function(data) {
        uni.showToast({ title: data.active ? '收藏成功' : '已取消收藏', icon: 'none' })
        that.loadDiscover()
        that.detailItem.favorited = !!data.active
      })
    },
    doToggleArticle(item) {
      var that = this
      toggleArticleFavorite(that.userId, item.id).then(function(data) {
        uni.showToast({ title: data.active ? '收藏成功' : '已取消收藏', icon: 'none' })
        that.loadDiscover()
        that.detailItem.favorited = !!data.active
      })
    },
    doTogglePost(item) {
      var that = this
      togglePostLike(that.userId, item.id).then(function(data) {
        uni.showToast({ title: data.active ? '点赞成功' : '已取消点赞', icon: 'none' })
        that.loadDiscover()
        that.detailItem.liked = !!data.active
      })
    }
  }
}
</script>

<style>
.container { padding: 24rpx; background: #f3f6fb; min-height: 100vh; }
.hero-card, .banner-card { background: linear-gradient(135deg, #4f46e5, #22c1dc); border-radius: 28rpx; padding: 28rpx; color: #fff; }
.hero-card { margin-bottom: 24rpx; }
.hero-tag { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: rgba(255,255,255,0.18); font-size: 22rpx; margin-bottom: 14rpx; }
.hero-title { font-size: 42rpx; font-weight: 700; }
.hero-desc { font-size: 24rpx; margin-top: 10rpx; line-height: 1.7; }
.banner-swiper { height: 220rpx; margin-bottom: 24rpx; }
.banner-badge { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: rgba(255,255,255,0.18); font-size: 22rpx; margin-bottom: 18rpx; }
.banner-title { font-size: 40rpx; font-weight: 700; }
.banner-subtitle { margin-top: 10rpx; font-size: 24rpx; color: #e0f2fe; }
.section-card { background: #fff; border-radius: 24rpx; padding: 24rpx; margin-bottom: 24rpx; box-shadow: 0 10rpx 24rpx rgba(15,23,42,0.05); }
.section-head { display: flex; justify-content: space-between; align-items: center; }
.section-title { font-size: 34rpx; font-weight: 700; margin-bottom: 16rpx; }
.tag-chip { padding: 8rpx 16rpx; border-radius: 999rpx; background: #eef2ff; color: #4f46e5; font-size: 22rpx; }
.pick-title { font-size: 30rpx; font-weight: 700; color: #0f172a; }
.tag-list { margin-top: 12rpx; }
.tag { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: #eef2ff; color: #4f46e5; font-size: 22rpx; margin-right: 10rpx; margin-bottom: 10rpx; }
.reason-line { font-size: 24rpx; color: #475569; margin-top: 10rpx; }
.channel-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16rpx; }
.channel-item { background: #f8fafc; border-radius: 20rpx; padding: 24rpx 0; text-align: center; }
.channel-icon { font-size: 34rpx; margin-bottom: 8rpx; }
.channel-text { font-size: 24rpx; color: #334155; }
.tab-row { display: flex; gap: 12rpx; margin-bottom: 20rpx; }
.tab { padding: 10rpx 20rpx; border-radius: 999rpx; background: #fff; color: #475569; font-size: 24rpx; }
.tab.active { background: linear-gradient(90deg, #3b82f6, #6366f1); color: #fff; }
.refresh-link { color: #64748b; font-size: 24rpx; }
.challenge-card { background: linear-gradient(90deg, #2563eb, #06b6d4); border-radius: 20rpx; padding: 22rpx; color: #fff; margin-bottom: 14rpx; }
.challenge-title, .content-title { font-size: 30rpx; font-weight: 700; }
.challenge-desc, .content-desc { font-size: 24rpx; margin-top: 8rpx; line-height: 1.6; }
.challenge-meta { display: flex; justify-content: space-between; font-size: 22rpx; margin-top: 12rpx; opacity: 0.95; }
.content-card { background: #f8fafc; border-radius: 20rpx; padding: 20rpx; margin-bottom: 12rpx; }
.empty-text { text-align: center; color: #94a3b8; padding: 30rpx 0; }
.popup-mask { position: fixed; left: 0; top: 0; right: 0; bottom: 0; background: rgba(15,23,42,0.42); display: flex; align-items: center; justify-content: center; z-index: 99; }
.popup-panel { width: 86%; max-height: 78vh; background: #fff; border-radius: 24rpx; padding: 24rpx; }
.popup-title { font-size: 34rpx; font-weight: 700; color: #0f172a; margin-bottom: 14rpx; }
.popup-scroll { max-height: 52vh; }
.popup-desc { font-size: 26rpx; color: #334155; line-height: 1.8; margin-bottom: 12rpx; }
.popup-block { margin-bottom: 14rpx; }
.popup-block-title { font-size: 28rpx; font-weight: 700; color: #0f172a; margin-bottom: 8rpx; }
.popup-block-desc { font-size: 24rpx; color: #475569; line-height: 1.7; margin-bottom: 8rpx; }
.btn-row { display: flex; gap: 16rpx; margin-top: 20rpx; }
.btn { flex: 1; text-align: center; border-radius: 18rpx; padding: 20rpx 0; font-size: 28rpx; font-weight: 700; }
.btn.primary { color: #fff; background: linear-gradient(90deg, #3b82f6, #6366f1); }
.btn.light { color: #334155; background: #f1f5f9; }
</style>
