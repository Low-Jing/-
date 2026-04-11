import { request } from '@/utils/request.js'

export function getDiscoverGrowthSummary(userId) {
  return request({
    url: '/discover/user-summary/?user_id=' + userId,
    method: 'GET'
  })
}
