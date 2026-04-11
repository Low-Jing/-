import { request } from '@/utils/request.js'

export function getPlanList(userId) {
  return request({
    url: '/plans/list/?user_id=' + userId,
    method: 'GET'
  })
}

export function getCheckinList(userId) {
  return request({
    url: '/plans/checkins/list/?user_id=' + userId,
    method: 'GET'
  })
}

export function createCheckin(payload) {
  return request({
    url: '/plans/checkins/',
    method: 'POST',
    data: payload
  })
}
