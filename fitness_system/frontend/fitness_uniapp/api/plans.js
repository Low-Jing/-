import { request } from '@/utils/request.js'

export function getPlanEngine(userId) {
  return request({ url: '/plans/engine/?user_id=' + userId, method: 'GET' })
}

export function getPlanList(userId) {
  return request({ url: '/plans/list/?user_id=' + userId, method: 'GET' })
}

export function generatePlan(userId) {
  return request({ url: '/plans/recommend/', method: 'POST', data: { user_id: userId } })
}

export function getPlanDashboard(userId) {
  return request({ url: '/plans/dashboard/?user_id=' + userId, method: 'GET' })
}

export function getCheckinList(userId) {
  return request({ url: '/plans/checkins/list/?user_id=' + userId, method: 'GET' })
}

export function createCheckin(payload) {
  return request({ url: '/plans/checkins/', method: 'POST', data: payload })
}
