export function formatGoal(goal) {
  var map = {
    lose_weight: '减脂塑形',
    gain_muscle: '增肌提升',
    maintain: '健康保持'
  }
  return map[goal] || goal || '-'
}

export function calcProgress(currentWeight, targetWeight) {
  var current = Number(currentWeight || 0)
  var target = Number(targetWeight || 0)
  if (!current || !target) return 0
  var diff = Math.abs(current - target)
  var denominator = Math.max(current, target)
  var value = Math.round((1 - diff / denominator) * 100)
  if (value < 0) value = 0
  if (value > 100) value = 100
  return value
}

export function calcStreak(checkins) {
  if (!checkins || !checkins.length) return 0
  var map = {}
  for (var i = 0; i < checkins.length; i++) {
    var created = checkins[i].created_at || ''
    var d = created.slice(0, 10)
    if (d) map[d] = true
  }
  var count = 0
  var day = new Date()
  for (var j = 0; j < 30; j++) {
    var y = day.getFullYear()
    var m = String(day.getMonth() + 1).padStart(2, '0')
    var d2 = String(day.getDate()).padStart(2, '0')
    var key = y + '-' + m + '-' + d2
    if (map[key]) {
      count += 1
      day.setDate(day.getDate() - 1)
    } else {
      break
    }
  }
  return count
}

export function latestRecord(records) {
  if (records && records.length) return records[0]
  return {}
}
