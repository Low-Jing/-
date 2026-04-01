import { BASE_URL } from '@/common/config.js'

export function request(options) {
  return new Promise(function(resolve, reject) {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json'
      },
      success: function(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject({
            statusCode: res.statusCode,
            data: res.data
          })
        }
      },
      fail: function(err) {
        reject(err)
      }
    })
  })
}

export function requestSafe(options, fallback) {
  return new Promise(function(resolve) {
    request(options).then(function(res) {
      resolve(res)
    }).catch(function(err) {
      console.log('requestSafe fallback =>', options.url, err)
      resolve(fallback)
    })
  })
}

export function saveLogin(data) {
  uni.setStorageSync('user_id', data.user_id || '')
  uni.setStorageSync('profile_id', data.profile_id || '')
  uni.setStorageSync('username', data.username || '')
  uni.setStorageSync('userInfo', data || {})
}

export function clearLogin() {
  uni.removeStorageSync('user_id')
  uni.removeStorageSync('profile_id')
  uni.removeStorageSync('username')
  uni.removeStorageSync('userInfo')
}

export function getUserId() {
  return uni.getStorageSync('user_id')
}

export function getProfileId() {
  return uni.getStorageSync('profile_id')
}

export function getUsername() {
  return uni.getStorageSync('username')
}

export function ensureLogin() {
  var userId = getUserId()
  if (!userId) {
    uni.reLaunch({
      url: '/pages/login/login'
    })
    return false
  }
  return true
}
