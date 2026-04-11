import { request } from '@/utils/request.js'

export function getDashboard() {
  return request({
    url: '/users/me/dashboard/',
    method: 'GET'
  })
}

export function getGrowthSummary() {
  return request({
    url: '/users/me/growth/',
    method: 'GET'
  })
}

export function getCurrentProfile() {
  return request({
    url: '/users/me/profile/',
    method: 'GET'
  })
}
