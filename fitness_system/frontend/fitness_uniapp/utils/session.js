export function getUserInfo() {
  return uni.getStorageSync('userInfo') || {}
}

export function getUserId() {
  var info = getUserInfo()
  return info.user_id || info.id || ''
}

export function setUserInfo(data) {
  uni.setStorageSync('userInfo', data || {})
}

export function clearSession() {
  uni.removeStorageSync('userInfo')
}