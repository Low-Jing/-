import { request } from '@/utils/request.js'

export function getDiscoverHome(userId) {
  return request({ url: '/discover/home/?user_id=' + userId, method: 'GET' })
}

export function getDiscoverGrowthSummary(userId) {
  return request({ url: '/discover/user-summary/?user_id=' + userId, method: 'GET' })
}

export function toggleChallengeJoin(userId, challengeId) {
  return request({ url: '/discover/challenge/toggle-join/', method: 'POST', data: { user_id: userId, challenge_id: challengeId } })
}

export function toggleCourseFavorite(userId, courseId) {
  return request({ url: '/discover/course/toggle-favorite/', method: 'POST', data: { user_id: userId, course_id: courseId } })
}

export function toggleArticleFavorite(userId, articleId) {
  return request({ url: '/discover/article/toggle-favorite/', method: 'POST', data: { user_id: userId, article_id: articleId } })
}

export function togglePostLike(userId, postId) {
  return request({ url: '/discover/post/toggle-like/', method: 'POST', data: { user_id: userId, post_id: postId } })
}
