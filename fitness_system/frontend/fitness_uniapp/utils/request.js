import { BASE_URL } from '@/common/config.js'
import { getUserId } from '@/utils/session.js'

function isPublicUrl(url) {
  return (
    url.indexOf('/users/login/') !== -1 ||
    url.indexOf('/users/register/') !== -1
  )
}

export function request(options) {
  return new Promise(function(resolve, reject) {
    var headers = {
      'Content-Type': 'application/json'
    }

    var userId = getUserId()

    if (userId && !isPublicUrl(options.url || '')) {
      headers['X-User-Id'] = String(userId)
    }

    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: headers,
      success: function(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          // 新旧两种响应格式都兼容
          if (
            res.data &&
            typeof res.data === 'object' &&
            res.data.hasOwnProperty('code') &&
            res.data.hasOwnProperty('data')
          ) {
            resolve(res.data.data)
          } else {
            resolve(res.data)
          }
        } else {
          reject(res)
        }
      },
      fail: function(err) {
        reject(err)
      }
    })
  })
}