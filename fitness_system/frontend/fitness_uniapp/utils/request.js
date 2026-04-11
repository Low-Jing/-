import { BASE_URL } from '@/common/config.js'

function isEnvelope(payload) {
  return !!(
    payload
    && typeof payload === 'object'
    && Object.prototype.hasOwnProperty.call(payload, 'code')
    && Object.prototype.hasOwnProperty.call(payload, 'message')
    && Object.prototype.hasOwnProperty.call(payload, 'data')
  )
}

function unwrapPayload(payload) {
  return isEnvelope(payload) ? payload.data : payload
}

function normalizeError(res) {
  var payload = res && res.data
  if (isEnvelope(payload)) {
    return {
      statusCode: res.statusCode,
      message: payload.message || '请求失败',
      code: payload.code,
      data: payload.data || {}
    }
  }
  return {
    statusCode: res.statusCode,
    message: (payload && payload.message) || '请求失败',
    data: payload
  }
}

export function request(options) {
  return new Promise(function(resolve, reject) {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: Object.assign({
        'Content-Type': 'application/json'
      }, options.header || {}),
      success: function(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(unwrapPayload(res.data))
        } else {
          reject(normalizeError(res))
        }
      },
      fail: function(err) {
        reject(err)
      }
    })
  })
}

export function requestWithMeta(options) {
  return new Promise(function(resolve, reject) {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: Object.assign({
        'Content-Type': 'application/json'
      }, options.header || {}),
      success: function(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve({
            raw: res,
            data: unwrapPayload(res.data),
            envelope: isEnvelope(res.data) ? res.data : null
          })
        } else {
          reject(normalizeError(res))
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
    request(options).then(function(data) {
      resolve(data)
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
