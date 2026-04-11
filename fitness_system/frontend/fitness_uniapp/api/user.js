import { request } from '@/utils/request.js'

export function loginUser(payload) {
  return request({
    url: '/users/login/',
    method: 'POST',
    data: payload
  })
}

export function registerUser(payload) {
  return request({
    url: '/users/register/',
    method: 'POST',
    data: payload
  })
}

export function getMyProfile(userId) {
  return request({
    url: '/users/profile/?user_id=' + userId,
    method: 'GET'
  })
}
