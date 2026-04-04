<template>
  <view class="container">
    <view class="hero-card">
      <view class="badge" style="background: rgba(255,255,255,0.18); margin-bottom: 16rpx;">内容生态与社区板块</view>
      <view class="page-title">发现</view>
      <view class="page-desc">把挑战、课程、知识与社区做成真正可用的发现页，既能互动，也能服务后续推荐增强。</view>
      <view class="search-wrap">
        <input class="search-input" v-model="searchText" placeholder="搜索挑战、课程、知识或社区内容" confirm-type="search" @confirm="handleSearch" />
        <view class="search-btn" @click="handleSearch">搜索</view>
      </view>
      <view class="row" style="margin-top: 18rpx; align-items: center;">
        <view>
          <view class="section-title" style="color:#fff; margin-bottom: 8rpx;">本周主题</view>
          <view style="color:#fff; font-size: 30rpx; font-weight: 700;">{{ theme.title }}</view>
        </view>
        <view style="color:#fff; font-size: 24rpx; max-width: 360rpx; text-align: right;">{{ theme.desc }}</view>
      </view>
    </view>

    <view class="card" style="padding-bottom: 18rpx;">
      <view class="section-title">主题推荐</view>
      <swiper class="banner-swiper" autoplay circular interval="3200" duration="500">
        <swiper-item v-for="(item, index) in banners" :key="index">
          <view class="banner-card">
            <view class="badge-light">{{ item.badge }}</view>
            <view class="banner-title">{{ item.title }}</view>
            <view class="banner-desc">{{ item.subtitle }}</view>
          </view>
        </swiper-item>
      </swiper>
    </view>

    <view class="card">
      <view class="section-title">功能频道</view>
      <view class="grid-4">
        <view class="grid-item-4" v-for="item in channels" :key="item.text" @click="quickFilter(item.text)">
          <view class="quick-item" :class="{ 'quick-item-active': activeQuickText === item.text }">
            <view class="quick-icon">{{ item.icon }}</view>
            <view class="quick-text">{{ item.text }}</view>
          </view>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="row" style="align-items:center;">
        <view class="section-title">内容分区</view>
        <view class="small muted" @click="resetSearch">重置筛选</view>
      </view>
      <view class="tab-row">
        <view
          v-for="item in tabs"
          :key="item.value"
          class="tab-chip"
          :class="{ 'tab-chip-active': activeTab === item.value }"
          @click="switchTab(item.value)"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <view class="card" v-if="recommendData.keywords && recommendData.keywords.length">
      <view class="row" style="align-items:center;">
        <view class="section-title">个性化发现推荐</view>
        <view class="small badge-light">{{ recommendData.stage || '内容推荐' }}</view>
      </view>
      <view class="tag-row">
        <text class="tag" v-for="item in recommendData.keywords" :key="item">{{ item }}</text>
      </view>
      <view class="recommend-reason" v-for="(item, index) in recommendData.reasons" :key="index">{{ item }}</view>
    </view>

    <view class="card" v-if="showChallenges">
      <view class="row">
        <view class="section-title">热门挑战</view>
        <view class="small muted" @click="loadDiscover">刷新</view>
      </view>
      <view v-if="challenges.length">
        <view class="challenge-card" v-for="item in challenges" :key="item.id" :style="{ background: item.theme_color || 'linear-gradient(135deg,#2563eb 0%,#06b6d4 100%)' }" @click="openDetail('challenge', item)">
          <view class="row" style="align-items:flex-start;">
            <view style="flex:1; padding-right: 20rpx;">
              <view class="course-title">{{ item.title }}</view>
              <view class="course-meta">{{ item.description }}</view>
              <view class="course-meta" style="margin-top:8rpx;">参与人数 {{ item.people_text || item.participant_count }}</view>
            </view>
            <text class="badge-light">{{ item.tag || '挑战' }}</text>
          </view>
          <view class="action-row">
            <view class="action-meta">连续 {{ item.days }} 天</view>
            <view class="action-btn" :class="{ 'action-btn-active': item.joined }" @click.stop="toggleChallenge(item)">{{ item.joined ? '已报名' : '立即报名' }}</view>
          </view>
        </view>
      </view>
      <view v-else class="empty">暂无挑战数据</view>
    </view>

    <view class="card" v-if="showTopics">
      <view class="section-title">专题课程</view>
      <view v-if="topics.length">
        <view class="list-card rich-card" v-for="item in topics" :key="item.id" @click="openDetail('course', item)">
          <view class="row">
            <view class="course-title">{{ item.title }}</view>
            <text class="badge-light">{{ item.level || '课程' }}</text>
          </view>
          <view class="course-meta">{{ item.description }}</view>
          <view class="tag-row" v-if="item.tag_list && item.tag_list.length">
            <text class="tag" v-for="tag in item.tag_list" :key="tag">{{ tag }}</text>
          </view>
          <view class="action-row">
            <view class="action-meta">课程推荐</view>
            <view class="action-btn" :class="{ 'action-btn-active': item.favorited }" @click.stop="toggleCourse(item)">{{ item.favorited ? '已收藏' : '收藏课程' }}</view>
          </view>
        </view>
      </view>
      <view v-else class="empty">暂无课程数据</view>
    </view>

    <view class="grid-2" v-if="showArticles || showFeeds">
      <view class="grid-item-2" v-if="showArticles">
        <view class="card">
          <view class="section-title">营养知识</view>
          <view v-if="articles.length">
            <view class="list-card rich-card" v-for="item in articles" :key="item.id" @click="openDetail('article', item)">
              <view class="row">
                <view class="course-title">{{ item.title }}</view>
                <text class="badge-light">{{ item.category }}</text>
              </view>
              <view class="course-meta">{{ item.summary }}</view>
              <view class="action-row">
                <view class="action-meta">{{ item.read_minutes }} 分钟阅读</view>
                <view class="action-btn" :class="{ 'action-btn-active': item.favorited }" @click.stop="toggleArticle(item)">{{ item.favorited ? '已收藏' : '收藏文章' }}</view>
              </view>
            </view>
          </view>
          <view v-else class="empty">暂无文章数据</view>
        </view>
      </view>
      <view class="grid-item-2" v-if="showFeeds">
        <view class="card">
          <view class="section-title">社区动态</view>
          <view v-if="feeds.length">
            <view class="list-card rich-card" v-for="item in feeds" :key="item.id" @click="openDetail('post', item)">
              <view class="row">
                <view class="course-title">{{ item.nickname }}</view>
                <text class="badge-light">{{ item.time_text }}</text>
              </view>
              <view class="course-meta">{{ item.content }}</view>
              <view class="action-row">
                <view class="action-meta">{{ item.total_likes || item.like_count }} 赞 · {{ item.comment_count }} 评论</view>
                <view class="action-btn" :class="{ 'action-btn-active': item.liked }" @click.stop="togglePost(item)">{{ item.liked ? '已点赞' : '点赞' }}</view>
              </view>
            </view>
          </view>
          <view v-else class="empty">暂无社区动态</view>
        </view>
      </view>
    </view>

    <view class="mask" v-if="showDetail" @click="closeDetail"></view>
    <view class="detail-panel" v-if="showDetail">
      <view class="row" style="align-items:center; margin-bottom: 12rpx;">
        <view class="section-title" style="margin-bottom:0;">{{ detailTitle }}</view>
        <view class="small muted" @click="closeDetail">关闭</view>
      </view>
      <view class="detail-main-title">{{ detailItem.title || detailItem.nickname || '-' }}</view>
      <view class="detail-desc">{{ detailDescription }}</view>
      <view class="tag-row" v-if="detailTags.length">
        <text class="tag" v-for="item in detailTags" :key="item">{{ item }}</text>
      </view>
      <view class="detail-meta">{{ detailMeta }}</view>
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
      searchText: '',
      activeQuickText: '',
      activeTab: 'all',
      tabs: [
        { label: '全部', value: 'all' },
        { label: '挑战', value: 'challenge' },
        { label: '课程', value: 'course' },
        { label: '知识', value: 'article' },
        { label: '社区', value: 'community' }
      ],
      theme: {
        title: '春季轻断食与快走周',
        desc: '挑战、课程、营养知识和社区互动放到一个页面，让系统更像完整产品。'
      },
      banners: [],
      channels: [],
      challenges: [],
      topics: [],
      articles: [],
      feeds: [],
      recommendData: {
        keywords: [],
        reasons: []
      },
      showDetail: false,
      detailType: '',
      detailItem: {}
    }
  },
  computed: {
    showChallenges() {
      return this.activeTab === 'all' || this.activeTab === 'challenge'
    },
    showTopics() {
      return this.activeTab === 'all' || this.activeTab === 'course'
    },
    showArticles() {
      return this.activeTab === 'all' || this.activeTab === 'article'
    },
    showFeeds() {
      return this.activeTab === 'all' || this.activeTab === 'community'
    },
    detailTitle() {
      var map = {
        challenge: '挑战详情',
        course: '课程详情',
        article: '知识详情',
        post: '社区动态'
      }
      return map[this.detailType] || '内容详情'
    },
    detailDescription() {
      return this.detailItem.description || this.detailItem.summary || this.detailItem.content || ''
    },
    detailTags() {
      if (this.detailType === 'course') return this.detailItem.tag_list || []
      if (this.detailType === 'challenge') return [this.detailItem.tag || '挑战', (this.detailItem.days || 7) + '天']
      if (this.detailType === 'article') return [this.detailItem.category || '知识', (this.detailItem.read_minutes || 5) + '分钟']
      if (this.detailType === 'post') return [String(this.detailItem.total_likes || this.detailItem.like_count || 0) + '赞', String(this.detailItem.comment_count || 0) + '评论']
      return []
    },
    detailMeta() {
      if (this.detailType === 'challenge') return '参与人数 ' + (this.detailItem.people_text || this.detailItem.participant_count || 0)
      if (this.detailType === 'course') return '课程等级：' + (this.detailItem.level || '入门')
      if (this.detailType === 'article') return '阅读时长：' + (this.detailItem.read_minutes || 5) + ' 分钟'
      if (this.detailType === 'post') return '发布时间：' + (this.detailItem.time_text || '今天')
      return ''
    }
  },
  onShow() {
    if (!ensureLogin()) return
    this.userId = getUserId()
    this.loadDiscover()
    this.loadRecommend()
  },
  methods: {
    loadDiscover() {
      var that = this
      requestSafe({
        url: '/discover/home/?user_id=' + that.userId,
        method: 'GET'
      }, {}).then(function(data) {
        that.theme = data.theme || that.theme
        that.banners = data.banners || []
        that.channels = data.channels || []
        that.challenges = data.challenges || []
        that.topics = data.topics || []
        that.articles = data.articles || []
        that.feeds = data.feeds || []
      })
    },
    loadRecommend() {
      var that = this
      requestSafe({
        url: '/discover/recommend/?user_id=' + that.userId,
        method: 'GET'
      }, { keywords: [], reasons: [] }).then(function(data) {
        that.recommendData = data || { keywords: [], reasons: [] }
      })
    },
    handleSearch() {
      var that = this
      requestSafe({
        url: '/discover/search/?user_id=' + that.userId + '&tab=' + that.activeTab + '&q=' + encodeURIComponent(that.searchText || ''),
        method: 'GET'
      }, {}).then(function(data) {
        that.challenges = data.challenges || []
        that.topics = data.topics || []
        that.articles = data.articles || []
        that.feeds = data.feeds || []
        uni.showToast({
          title: that.searchText ? '已筛选内容' : '已刷新全部内容',
          icon: 'none'
        })
      })
    },
    resetSearch() {
      this.searchText = ''
      this.activeQuickText = ''
      this.activeTab = 'all'
      this.loadDiscover()
      this.loadRecommend()
    },
    switchTab(tab) {
      this.activeTab = tab
      this.handleSearch()
    },
    quickFilter(text) {
      this.activeQuickText = text
      var map = {
        '挑战赛': 'challenge',
        '课程': 'course',
        '知识': 'article',
        '社区': 'community'
      }
      this.activeTab = map[text] || 'all'
      this.searchText = text
      this.handleSearch()
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
    toggleChallenge(item, silent) {
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
        if (!silent) {
          uni.showToast({ title: data.message || (data.active ? '报名成功' : '已取消报名'), icon: 'none' })
        }
        that.loadRecommend()
      }).catch(function(err) {
        uni.showToast({ title: (err.data && err.data.message) || '操作失败', icon: 'none' })
      })
    },
    toggleCourse(item, silent) {
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
        if (!silent) {
          uni.showToast({ title: data.message || (data.active ? '已收藏课程' : '已取消收藏'), icon: 'none' })
        }
        that.loadRecommend()
      }).catch(function(err) {
        uni.showToast({ title: (err.data && err.data.message) || '操作失败', icon: 'none' })
      })
    },
    toggleArticle(item, silent) {
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
        if (!silent) {
          uni.showToast({ title: data.message || (data.active ? '已收藏文章' : '已取消收藏'), icon: 'none' })
        }
        that.loadRecommend()
      }).catch(function(err) {
        uni.showToast({ title: (err.data && err.data.message) || '操作失败', icon: 'none' })
      })
    },
    togglePost(item, silent) {
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
        if (!silent) {
          uni.showToast({ title: data.message || (data.active ? '已点赞' : '已取消点赞'), icon: 'none' })
        }
        that.loadRecommend()
      }).catch(function(err) {
        uni.showToast({ title: (err.data && err.data.message) || '操作失败', icon: 'none' })
      })
    }
  }
}
</script>

<style>
.search-wrap {
  margin-top: 20rpx;
  display: flex;
  gap: 16rpx;
  align-items: center;
}
.search-input {
  flex: 1;
  height: 76rpx;
  border-radius: 999rpx;
  background: rgba(255,255,255,0.18);
  color: #fff;
  padding: 0 24rpx;
}
.search-btn {
  width: 140rpx;
  height: 76rpx;
  line-height: 76rpx;
  text-align: center;
  border-radius: 999rpx;
  background: rgba(255,255,255,0.22);
  color: #fff;
  font-weight: 700;
}
.banner-swiper {
  height: 220rpx;
}
.banner-card {
  height: 190rpx;
  border-radius: 24rpx;
  padding: 24rpx;
  background: linear-gradient(135deg,#1d4ed8 0%,#06b6d4 100%);
  color: #fff;
}
.banner-title {
  font-size: 34rpx;
  font-weight: 700;
  margin: 18rpx 0 10rpx;
}
.banner-desc {
  font-size: 24rpx;
  line-height: 1.6;
  opacity: 0.95;
}
.tab-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.tab-chip {
  padding: 14rpx 26rpx;
  border-radius: 999rpx;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 24rpx;
}
.tab-chip-active {
  background: linear-gradient(135deg,#4f46e5 0%,#06b6d4 100%);
  color: #fff;
}
.quick-item-active {
  background: linear-gradient(135deg,#eff6ff 0%,#e0f2fe 100%);
  border: 2rpx solid #60a5fa;
}
.challenge-card {
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  color: #fff;
}
.challenge-card .course-title,
.challenge-card .course-meta {
  color: #fff;
}
.rich-card {
  border: 1px solid #eef2ff;
}
.action-row {
  margin-top: 18rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
}
.action-meta {
  color: #64748b;
  font-size: 24rpx;
}
.action-btn {
  padding: 12rpx 22rpx;
  border-radius: 999rpx;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 24rpx;
  font-weight: 700;
}
.action-btn-active {
  background: linear-gradient(135deg,#4f46e5 0%,#06b6d4 100%);
  color: #fff;
}
.recommend-reason {
  margin-top: 12rpx;
  padding: 18rpx 20rpx;
  border-radius: 18rpx;
  background: #f8fafc;
  color: #475569;
  font-size: 24rpx;
}
.mask {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: 99;
}
.detail-panel {
  position: fixed;
  left: 24rpx;
  right: 24rpx;
  bottom: 24rpx;
  z-index: 100;
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx;
  box-shadow: 0 20rpx 48rpx rgba(15, 23, 42, 0.2);
}
.detail-main-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 12rpx;
}
.detail-desc {
  font-size: 26rpx;
  color: #475569;
  line-height: 1.7;
}
.detail-meta {
  margin-top: 16rpx;
  color: #64748b;
  font-size: 24rpx;
}
.detail-actions {
  margin-top: 24rpx;
}
.detail-btn {
  height: 84rpx;
  line-height: 84rpx;
  text-align: center;
  border-radius: 18rpx;
  font-weight: 700;
}
.detail-btn.primary {
  background: linear-gradient(135deg,#4f46e5 0%,#06b6d4 100%);
  color: #fff;
}
</style>
