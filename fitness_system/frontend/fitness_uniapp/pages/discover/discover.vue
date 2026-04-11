<template>
  <view class="container">
    <view class="hero-card">
      <view class="hero-tag">内容生态与社区模块</view>
      <view class="hero-title">发现</view>
      <view class="hero-desc">去掉搜索，把运营位、课程详情、知识正文和社区互动做完整，让发现页更像真正的内容型应用。</view>
    </view>

    <view class="card banner-card">
      <swiper class="banner-swiper" autoplay circular interval="3500" indicator-dots>
        <swiper-item v-for="(item, index) in banners" :key="index">
          <view class="banner-item" :style="{ backgroundImage: 'url(' + getBannerImage(item.image_key) + ')' }">
            <view class="banner-mask">
              <view class="banner-badge">{{ item.badge }}</view>
              <view class="banner-title">{{ item.title }}</view>
              <view class="banner-subtitle">{{ item.subtitle }}</view>
            </view>
          </view>
        </swiper-item>
      </swiper>
    </view>

    <view class="card" v-if="editorPick.keywords && editorPick.keywords.length">
      <view class="row align-center">
        <view class="section-title">为你精选</view>
        <view class="small-pill">个性化发现</view>
      </view>
      <view class="pick-title">{{ editorPick.title }}</view>
      <view class="tag-row">
        <text class="tag" v-for="(item, index) in editorPick.keywords" :key="index">{{ item }}</text>
      </view>
      <view class="pick-reason" v-for="(item, index) in editorPick.reasons" :key="index">{{ item }}</view>
    </view>

    <view class="card">
      <view class="section-title">功能频道</view>
      <view class="grid-4">
        <view class="grid-item" v-for="item in channels" :key="item.text" @click="switchTab(item.anchor)">
          <view class="channel-box" :class="{ active: activeTab === item.anchor }">
            <view class="channel-icon">{{ item.icon }}</view>
            <view class="channel-text">{{ item.text }}</view>
          </view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="tab-row">
        <view class="tab-chip" :class="{ active: activeTab === 'all' }" @click="switchTab('all')">全部</view>
        <view class="tab-chip" :class="{ active: activeTab === 'challenge' }" @click="switchTab('challenge')">挑战</view>
        <view class="tab-chip" :class="{ active: activeTab === 'course' }" @click="switchTab('course')">课程</view>
        <view class="tab-chip" :class="{ active: activeTab === 'article' }" @click="switchTab('article')">知识</view>
        <view class="tab-chip" :class="{ active: activeTab === 'community' }" @click="switchTab('community')">社区</view>
      </view>
    </view>

    <view class="card" v-if="showChallenges">
      <view class="row align-center">
        <view class="section-title">热门挑战</view>
        <view class="muted small" @click="loadDiscover">刷新</view>
      </view>
      <view v-if="challenges.length">
        <view class="challenge-card" v-for="item in challenges" :key="item.id" :style="{ background: item.theme_color || 'linear-gradient(135deg,#2563eb 0%,#06b6d4 100%)' }" @click="openDetail('challenge', item)">
          <view class="row align-start">
            <view class="flex-1 pr16">
              <view class="card-title white">{{ item.title }}</view>
              <view class="card-desc white opacity">{{ item.description }}</view>
              <view class="meta-line white opacity">参与人数 {{ item.people_text || item.participant_count }} · 连续 {{ item.days }} 天</view>
            </view>
            <view class="badge-light">{{ item.tag || '挑战' }}</view>
          </view>
          <view class="action-row">
            <view class="action-meta white opacity">点击查看详情与任务安排</view>
            <view class="action-btn" :class="{ active: item.joined }" @click.stop="toggleChallenge(item)">{{ item.joined ? '已报名' : '立即报名' }}</view>
          </view>
        </view>
      </view>
      <view v-else class="empty">暂无挑战数据</view>
    </view>

    <view class="card" v-if="showTopics">
      <view class="section-title">专题课程</view>
      <view v-if="topics.length">
        <view class="list-card rich-card" v-for="item in topics" :key="item.id" @click="openDetail('course', item)">
          <view class="row align-center">
            <view class="card-title">{{ item.title }}</view>
            <view class="badge-light">{{ item.level || '课程' }}</view>
          </view>
          <view class="card-desc">{{ item.description }}</view>
          <view class="tag-row">
            <text class="tag" v-for="tag in (item.tag_list || [])" :key="tag">{{ tag }}</text>
          </view>
          <view class="meta-line">{{ item.coach_name }} · {{ item.duration_text }}</view>
          <view class="action-row border-top">
            <view class="action-meta">点进卡片查看完整课程大纲</view>
            <view class="action-btn outline" :class="{ active: item.favorited }" @click.stop="toggleCourse(item)">{{ item.favorited ? '已收藏' : '收藏课程' }}</view>
          </view>
        </view>
      </view>
      <view v-else class="empty">暂无课程数据</view>
    </view>

    <view class="grid-2" v-if="showArticles || showFeeds">
      <view class="grid-item-2" v-if="showArticles">
        <view class="card full-height">
          <view class="section-title">知识文章</view>
          <view v-if="articles.length">
            <view class="list-card rich-card" v-for="item in articles" :key="item.id" @click="openDetail('article', item)">
              <view class="row align-center">
                <view class="card-title">{{ item.title }}</view>
                <view class="badge-light">{{ item.category }}</view>
              </view>
              <view class="card-desc">{{ item.summary }}</view>
              <view class="meta-line">{{ item.author }} · {{ item.read_minutes }} 分钟阅读</view>
              <view class="action-row border-top">
                <view class="action-meta">点进卡片查看正文与要点</view>
                <view class="action-btn outline" :class="{ active: item.favorited }" @click.stop="toggleArticle(item)">{{ item.favorited ? '已收藏' : '收藏文章' }}</view>
              </view>
            </view>
          </view>
          <view v-else class="empty">暂无文章数据</view>
        </view>
      </view>

      <view class="grid-item-2" v-if="showFeeds">
        <view class="card full-height">
          <view class="section-title">社区动态</view>
          <view v-if="feeds.length">
            <view class="list-card rich-card" v-for="item in feeds" :key="item.id" @click="openDetail('post', item)">
              <view class="row align-center">
                <view class="card-title">{{ item.nickname }}</view>
                <view class="badge-light">{{ item.time_text }}</view>
              </view>
              <view class="card-desc">{{ item.content }}</view>
              <view class="meta-line">{{ item.total_likes || item.like_count }} 赞 · {{ item.comment_count }} 评论 · {{ item.topic_label }}</view>
              <view class="action-row border-top">
                <view class="action-meta">点进卡片查看互动详情</view>
                <view class="action-btn outline" :class="{ active: item.liked }" @click.stop="togglePost(item)">{{ item.liked ? '已点赞' : '点赞' }}</view>
              </view>
            </view>
          </view>
          <view v-else class="empty">暂无社区动态</view>
        </view>
      </view>
    </view>

    <view class="mask" v-if="showDetail" @click="closeDetail"></view>
    <view class="detail-panel" v-if="showDetail">
      <view class="row align-center mb16">
        <view class="section-title no-margin">{{ detailTitle }}</view>
        <view class="muted small" @click="closeDetail">关闭</view>
      </view>
      <view class="detail-main-title">{{ detailMainTitle }}</view>
      <view class="detail-subtitle" v-if="detailSubtitle">{{ detailSubtitle }}</view>
      <view class="tag-row" v-if="detailTags.length">
        <text class="tag" v-for="item in detailTags" :key="item">{{ item }}</text>
      </view>
      <view class="detail-body" v-if="detailDescription">{{ detailDescription }}</view>

      <view v-if="detailType === 'challenge'">
        <view class="detail-block" v-for="(item, index) in (detailItem.detail_sections || [])" :key="index">
          <view class="detail-block-title">{{ item.title }}</view>
          <view class="detail-body">{{ item.content }}</view>
        </view>
        <view class="detail-block" v-if="detailItem.task_list && detailItem.task_list.length">
          <view class="detail-block-title">挑战任务</view>
          <view class="bullet-row" v-for="(task, index) in detailItem.task_list" :key="index">• {{ task }}</view>
        </view>
      </view>

      <view v-if="detailType === 'course'">
        <view class="detail-block" v-if="detailItem.full_content">
          <view class="detail-block-title">课程介绍</view>
          <view class="detail-body multiline">{{ detailItem.full_content }}</view>
        </view>
        <view class="detail-block" v-if="detailItem.lesson_points && detailItem.lesson_points.length">
          <view class="detail-block-title">课程大纲</view>
          <view class="bullet-row" v-for="(lesson, index) in detailItem.lesson_points" :key="index">• {{ lesson }}</view>
        </view>
      </view>

      <view v-if="detailType === 'article'">
        <view class="detail-block">
          <view class="detail-block-title">正文内容</view>
          <view class="detail-body multiline" v-for="(block, index) in (detailItem.article_blocks || [])" :key="index">{{ block }}</view>
        </view>
        <view class="detail-block" v-if="detailItem.takeaways && detailItem.takeaways.length">
          <view class="detail-block-title">阅读要点</view>
          <view class="bullet-row" v-for="(point, index) in detailItem.takeaways" :key="index">• {{ point }}</view>
        </view>
      </view>

      <view v-if="detailType === 'post'">
        <view class="detail-block" v-if="detailItem.comments_preview && detailItem.comments_preview.length">
          <view class="detail-block-title">评论预览</view>
          <view class="comment-box" v-for="(c, index) in detailItem.comments_preview" :key="index">
            <view class="comment-name">{{ c.nickname }}</view>
            <view class="comment-text">{{ c.text }}</view>
          </view>
        </view>
      </view>

      <view class="detail-actions">
        <view v-if="detailType === 'challenge'" class="detail-btn primary" @click="toggleChallenge(detailItem, true)">{{ detailItem.joined ? '取消报名' : '立即报名' }}</view>
        <view v-if="detailType === 'course'" class="detail-btn primary" @click="toggleCourse(detailItem, true)">{{ detailItem.favorited ? '取消收藏' : '收藏课程' }}</view>
        <view v-if="detailType === 'article'" class="detail-btn primary" @click="toggleArticle(detailItem, true)">{{ detailItem.favorited ? '取消收藏' : '收藏文章' }}</view>
        <view v-if="detailType === 'post'" class="detail-btn primary" @click="togglePost(detailItem, true)">{{ detailItem.liked ? '取消点赞' : '点赞动态' }}</view>
      </view>
    </view>
  </view>
</template>

<script>
import { request, requestSafe, ensureLogin, getUserId } from '@/utils/request.js'

export default {
  data() {
    return {
      userId: '',
      activeTab: 'all',
      theme: { title: '发现', desc: '内容型应用入口' },
      banners: [],
      channels: [],
      editorPick: { keywords: [], reasons: [] },
      challenges: [],
      topics: [],
      articles: [],
      feeds: [],
      showDetail: false,
      detailType: '',
      detailItem: {}
    }
  },
  computed: {
    showChallenges() { return this.activeTab === 'all' || this.activeTab === 'challenge' },
    showTopics() { return this.activeTab === 'all' || this.activeTab === 'course' },
    showArticles() { return this.activeTab === 'all' || this.activeTab === 'article' },
    showFeeds() { return this.activeTab === 'all' || this.activeTab === 'community' },
    detailTitle() {
      var map = { challenge: '挑战详情', course: '课程详情', article: '知识正文', post: '社区动态' }
      return map[this.detailType] || '内容详情'
    },
    detailMainTitle() {
      return this.detailItem.cover_title || this.detailItem.headline || this.detailItem.title || this.detailItem.nickname || '-'
    },
    detailSubtitle() {
      if (this.detailType === 'challenge') return '挑战详情与任务说明'
      if (this.detailType === 'course') return this.detailItem.duration_text || ''
      if (this.detailType === 'article') return (this.detailItem.author || '') + ' · ' + (this.detailItem.read_minutes || 5) + ' 分钟阅读'
      if (this.detailType === 'post') return this.detailItem.time_text || ''
      return ''
    },
    detailTags() {
      if (this.detailType === 'course') return this.detailItem.tag_list || []
      if (this.detailType === 'challenge') return [this.detailItem.tag || '挑战', (this.detailItem.days || 7) + '天']
      if (this.detailType === 'article') return [this.detailItem.category || '知识']
      if (this.detailType === 'post') return [String(this.detailItem.total_likes || this.detailItem.like_count || 0) + '赞', String(this.detailItem.comment_count || 0) + '评论']
      return []
    },
    detailDescription() {
      return this.detailItem.detail_intro || this.detailItem.description || this.detailItem.summary || this.detailItem.content || ''
    }
  },
  onShow() {
    if (!ensureLogin()) return
    this.userId = getUserId()
    this.loadDiscover()
  },
  methods: {
    getBannerImage(key) {
      var map = {
        banner1: '/static/discover/banner1.svg',
        banner2: '/static/discover/banner2.svg',
        banner3: '/static/discover/banner3.svg'
      }
      return map[key] || '/static/discover/banner1.svg'
    },
    switchTab(value) {
      this.activeTab = value
    },
    loadDiscover() {
      var that = this
      requestSafe({
        url: '/discover/home/?user_id=' + that.userId,
        method: 'GET'
      }, {}).then(function(data) {
        that.theme = data.theme || that.theme
        that.banners = data.banners || []
        that.channels = data.channels || []
        that.editorPick = data.editor_pick || { keywords: [], reasons: [] }
        that.challenges = data.challenges || []
        that.topics = data.topics || []
        that.articles = data.articles || []
        that.feeds = data.feeds || []
      })
    },
    openDetail(type, item) {
      this.detailType = type
      this.detailItem = item
      this.showDetail = true
    },
    closeDetail() {
      this.showDetail = false
      this.detailType = ''
      this.detailItem = {}
    },
    toggleChallenge(item, fromDetail) {
      var that = this
      request({
        url: '/discover/challenge/toggle-join/',
        method: 'POST',
        data: { user_id: that.userId, challenge_id: item.id }
      }).then(function(data) {
        item.joined = data.active
        item.people_text = data.people_text || item.people_text
        if (fromDetail) that.detailItem = item
        uni.showToast({ title: data.active ? '报名成功' : '已取消', icon: 'none' })
      }).catch(function() {
        uni.showToast({ title: '操作失败', icon: 'none' })
      })
    },
    toggleCourse(item, fromDetail) {
      var that = this
      request({
        url: '/discover/course/toggle-favorite/',
        method: 'POST',
        data: { user_id: that.userId, course_id: item.id }
      }).then(function(data) {
        item.favorited = data.active
        if (fromDetail) that.detailItem = item
        uni.showToast({ title: data.active ? '已收藏' : '已取消', icon: 'none' })
      }).catch(function() {
        uni.showToast({ title: '操作失败', icon: 'none' })
      })
    },
    toggleArticle(item, fromDetail) {
      var that = this
      request({
        url: '/discover/article/toggle-favorite/',
        method: 'POST',
        data: { user_id: that.userId, article_id: item.id }
      }).then(function(data) {
        item.favorited = data.active
        if (fromDetail) that.detailItem = item
        uni.showToast({ title: data.active ? '已收藏' : '已取消', icon: 'none' })
      }).catch(function() {
        uni.showToast({ title: '操作失败', icon: 'none' })
      })
    },
    togglePost(item, fromDetail) {
      var that = this
      request({
        url: '/discover/post/toggle-like/',
        method: 'POST',
        data: { user_id: that.userId, post_id: item.id }
      }).then(function(data) {
        item.liked = data.active
        item.total_likes = data.count || item.total_likes
        if (fromDetail) that.detailItem = item
        uni.showToast({ title: data.active ? '已点赞' : '已取消', icon: 'none' })
      }).catch(function() {
        uni.showToast({ title: '操作失败', icon: 'none' })
      })
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
.card { background: #fff; border-radius: 24rpx; padding: 24rpx; margin-bottom: 24rpx; box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05); }
.banner-card { padding: 0; overflow: hidden; }
.banner-swiper { height: 280rpx; }
.banner-item { width: 100%; height: 100%; background-size: cover; background-position: center; }
.banner-mask { width: 100%; height: 100%; background: linear-gradient(90deg, rgba(15,23,42,.25), rgba(15,23,42,.05)); padding: 28rpx; box-sizing: border-box; color: #fff; }
.banner-badge { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: rgba(255,255,255,0.18); font-size: 22rpx; margin-bottom: 14rpx; }
.banner-title { font-size: 38rpx; font-weight: 700; margin-bottom: 10rpx; }
.banner-subtitle { font-size: 24rpx; line-height: 1.7; width: 78%; }
.row { display: flex; justify-content: space-between; }
.align-center { align-items: center; }
.align-start { align-items: flex-start; }
.flex-1 { flex: 1; }
.pr16 { padding-right: 16rpx; }
.mb16 { margin-bottom: 16rpx; }
.section-title { font-size: 34rpx; font-weight: 700; margin-bottom: 18rpx; }
.no-margin { margin-bottom: 0; }
.small { font-size: 24rpx; }
.muted { color: #94a3b8; }
.small-pill { padding: 8rpx 16rpx; border-radius: 999rpx; background: #eef2ff; color: #4f46e5; font-size: 22rpx; }
.pick-title { font-size: 30rpx; font-weight: 700; margin-bottom: 12rpx; }
.pick-reason { font-size: 24rpx; color: #475569; line-height: 1.7; margin-bottom: 10rpx; }
.grid-4 { display: flex; flex-wrap: wrap; margin: 0 -8rpx; }
.grid-item { width: 25%; padding: 8rpx; box-sizing: border-box; }
.channel-box { background: #f8fafc; border-radius: 18rpx; padding: 20rpx 10rpx; text-align: center; border: 2rpx solid transparent; }
.channel-box.active { border-color: #4f46e5; background: #eef2ff; }
.channel-icon { font-size: 34rpx; margin-bottom: 10rpx; }
.channel-text { font-size: 24rpx; color: #334155; }
.tab-row { display: flex; gap: 12rpx; flex-wrap: wrap; }
.tab-chip { padding: 10rpx 18rpx; border-radius: 999rpx; background: #f1f5f9; color: #475569; font-size: 24rpx; }
.tab-chip.active { background: linear-gradient(90deg, #3b82f6, #6366f1); color: #fff; }
.challenge-card { border-radius: 24rpx; padding: 24rpx; color: #fff; margin-bottom: 18rpx; }
.card-title { font-size: 30rpx; font-weight: 700; }
.card-desc { font-size: 24rpx; color: #475569; line-height: 1.7; margin-top: 8rpx; }
.white { color: #fff; }
.opacity { opacity: 0.92; }
.meta-line { font-size: 22rpx; margin-top: 12rpx; color: #64748b; }
.badge-light { padding: 8rpx 16rpx; border-radius: 999rpx; background: rgba(255,255,255,.2); font-size: 22rpx; color: #fff; }
.rich-card { border: 1px solid #eef2ff; }
.list-card { background: #fff; border-radius: 20rpx; padding: 18rpx; margin-bottom: 16rpx; }
.tag-row { margin-top: 12rpx; }
.tag { display: inline-block; padding: 8rpx 16rpx; border-radius: 999rpx; background: #eef2ff; color: #4f46e5; font-size: 22rpx; margin-right: 10rpx; margin-bottom: 10rpx; }
.action-row { display: flex; justify-content: space-between; align-items: center; margin-top: 18rpx; }
.action-meta { font-size: 22rpx; color: #94a3b8; }
.action-btn { padding: 10rpx 18rpx; border-radius: 999rpx; background: rgba(255,255,255,.92); color: #2563eb; font-size: 22rpx; }
.action-btn.outline { background: #eef2ff; color: #4f46e5; }
.action-btn.active { background: #10b981; color: #fff; }
.border-top { border-top: 1px solid #f1f5f9; padding-top: 14rpx; }
.grid-2 { display: flex; gap: 20rpx; margin-bottom: 24rpx; }
.grid-item-2 { flex: 1; }
.full-height { height: 100%; }
.empty { text-align: center; color: #94a3b8; padding: 36rpx 0; }
.mask { position: fixed; left: 0; top: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.45); z-index: 99; }
.detail-panel { position: fixed; left: 24rpx; right: 24rpx; top: 80rpx; bottom: 30rpx; background: #fff; border-radius: 28rpx; padding: 24rpx; z-index: 100; overflow-y: auto; box-shadow: 0 24rpx 60rpx rgba(15, 23, 42, 0.18); }
.detail-main-title { font-size: 34rpx; font-weight: 700; margin-bottom: 10rpx; }
.detail-subtitle { font-size: 24rpx; color: #64748b; margin-bottom: 12rpx; }
.detail-body { font-size: 26rpx; color: #334155; line-height: 1.8; margin-top: 10rpx; }
.multiline { margin-bottom: 12rpx; }
.detail-block { background: #f8fafc; border-radius: 18rpx; padding: 18rpx; margin-top: 14rpx; }
.detail-block-title { font-size: 28rpx; font-weight: 700; margin-bottom: 8rpx; }
.bullet-row { font-size: 24rpx; color: #475569; line-height: 1.8; margin-top: 6rpx; }
.comment-box { background: #fff; border-radius: 16rpx; padding: 16rpx; margin-top: 10rpx; border: 1px solid #e2e8f0; }
.comment-name { font-size: 24rpx; font-weight: 700; margin-bottom: 6rpx; }
.comment-text { font-size: 24rpx; color: #475569; line-height: 1.7; }
.detail-actions { margin-top: 22rpx; }
.detail-btn { text-align: center; border-radius: 18rpx; padding: 22rpx 0; font-size: 28rpx; font-weight: 700; }
.detail-btn.primary { color: #fff; background: linear-gradient(90deg, #3b82f6, #6366f1); }
@media screen and (max-width: 768px) { .grid-item { width: 50%; } .grid-2 { display:block; } .grid-item-2 { margin-bottom: 20rpx; } }
</style>
