import { request } from '@/utils/request.js'

export function getRecordList(userId) {
  return request({ url: '/health/records/list/?user_id=' + userId, method: 'GET' })
}

export function createRecord(payload) {
  return request({ url: '/health/records/', method: 'POST', data: payload })
}
