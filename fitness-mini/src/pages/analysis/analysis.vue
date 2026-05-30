<template>
  <view class="analysis-page">
    <!-- 顶部 -->
    <view class="header">
      <text class="header-title">健康分析</text>
      <text class="header-sub">了解你的身体变化</text>
    </view>

    <!-- 健康评分 -->
    <view class="score-card">
      <view class="score-circle">
        <text class="score-num">{{ healthScore }}</text>
        <text class="score-label">健康分</text>
      </view>
      <view class="score-desc">
        <text class="score-status">{{ scoreStatus }}</text>
        <text class="score-tip">{{ scoreTip }}</text>
      </view>
    </view>

    <!-- 周期变化 -->
    <view class="card">
      <view class="card-header">
        <text class="card-title">周期变化</text>
        <text class="card-sub">近6个月</text>
      </view>
      <view class="chart-area">
        <view class="chart-bars">
          <view v-for="(d, i) in cycleData" :key="i" class="bar-item">
            <text class="bar-val">{{ d.days }}天</text>
            <view class="bar" :style="{ height: (d.days / 35) * 200 + 'rpx' }"></view>
            <text class="bar-label">{{ d.month }}</text>
          </view>
        </view>
      </view>
      <view class="chart-summary">
        <view class="summary-item">
          <text class="summary-label">平均周期</text>
          <text class="summary-val">{{ avgCycle }}天</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">平均经期</text>
          <text class="summary-val">{{ avgPeriod }}天</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">规律度</text>
          <text class="summary-val">{{ regularity }}%</text>
        </view>
      </view>
    </view>

    <!-- 经期变化 -->
    <view class="card">
      <view class="card-header">
        <text class="card-title">经期变化</text>
        <text class="card-sub">症状趋势</text>
      </view>
      <view class="symptom-list">
        <view v-for="s in symptomTrends" :key="s.name" class="symptom-item">
          <text class="symptom-name">{{ s.name }}</text>
          <view class="symptom-bar-bg">
            <view class="symptom-bar-fill" :style="{ width: s.percent + '%' }" :class="s.level"></view>
          </view>
          <text class="symptom-val">{{ s.trend }}</text>
        </view>
      </view>
    </view>

    <!-- 健康建议 -->
    <view class="card">
      <view class="card-header">
        <text class="card-title">AI健康建议</text>
      </view>
      <view class="advice-list">
        <view v-for="(a, i) in advices" :key="i" class="advice-item">
          <view class="advice-icon">{{ a.icon }}</view>
          <view class="advice-content">
            <text class="advice-title">{{ a.title }}</text>
            <text class="advice-text">{{ a.text }}</text>
          </view>
        </view>
      </view>
      <button class="ask-btn" @tap="askAI">让AI详细分析</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { onShow } from "@dcloudio/uni-app";

// 模拟数据（后面接真实API）
const cycleData = ref([
  { month: "1月", days: 28 },
  { month: "2月", days: 30 },
  { month: "3月", days: 27 },
  { month: "4月", days: 29 },
  { month: "5月", days: 28 },
  { month: "6月", days: 29 },
]);

const avgCycle = computed(() => {
  const total = cycleData.value.reduce((s, d) => s + d.days, 0);
  return Math.round(total / cycleData.value.length);
});

const avgPeriod = ref(5);
const regularity = ref(85);

const healthScore = computed(() => {
  let score = 70;
  if (regularity.value > 80) score += 15;
  if (avgCycle.value >= 26 && avgCycle.value <= 32) score += 10;
  if (avgPeriod.value >= 3 && avgPeriod.value <= 7) score += 5;
  return Math.min(score, 100);
});

const scoreStatus = computed(() => {
  const s = healthScore.value;
  if (s >= 90) return "优秀";
  if (s >= 75) return "良好";
  if (s >= 60) return "一般";
  return "需关注";
});

const scoreTip = computed(() => {
  const s = healthScore.value;
  if (s >= 90) return "你的身体状态很好，继续保持！";
  if (s >= 75) return "整体不错，注意规律作息";
  if (s >= 60) return "建议多关注身体信号，适当调整";
  return "建议去医院做个检查";
});

const symptomTrends = ref([
  { name: "痛经", percent: 40, level: "low", trend: "↓ 减轻" },
  { name: "情绪波动", percent: 60, level: "mid", trend: "→ 持平" },
  { name: "乳房胀痛", percent: 30, level: "low", trend: "↓ 减轻" },
  { name: "疲劳感", percent: 70, level: "high", trend: "↑ 加重" },
  { name: "头痛", percent: 20, level: "low", trend: "→ 持平" },
]);

const advices = ref([
  { icon: "🌙", title: "睡眠建议", text: "你的疲劳感呈上升趋势，建议经期前一周早睡，保证7-8小时睡眠" },
  { icon: "🥗", title: "饮食建议", text: "经前多补充镁和B族维生素，减少咖啡因摄入" },
  { icon: "🧘", title: "运动建议", text: "你的周期规律度不错，卵泡期可以尝试增加运动强度" },
]);

function askAI() {
  uni.navigateTo({ url: "/pages/chat/chat?assistant=shiqing" });
}

onShow(() => {
  // TODO: 从API加载真实数据
});
</script>

<style scoped>
.analysis-page {
  min-height: 100vh;
  background: #fff5f5;
  padding-bottom: 160rpx;
}

.header {
  padding: 88rpx 32rpx 28rpx;
  background: linear-gradient(135deg, #e8837c, #d4625a);
}

.header-title {
  font-size: 38rpx;
  font-weight: 600;
  color: #fff;
  display: block;
}

.header-sub {
  font-size: 24rpx;
  color: rgba(255,255,255,0.8);
  margin-top: 6rpx;
}

.score-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 24rpx;
  padding: 36rpx 32rpx;
  margin: -20rpx 24rpx 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(232, 131, 124, 0.12);
}

.score-circle {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #fce4ec, #f8bbd0);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-right: 28rpx;
}

.score-num {
  font-size: 48rpx;
  font-weight: 700;
  color: #d4625a;
  line-height: 1;
}

.score-label {
  font-size: 20rpx;
  color: #e8837c;
  margin-top: 4rpx;
}

.score-desc {
  flex: 1;
}

.score-status {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}

.score-tip {
  font-size: 24rpx;
  color: #999;
  line-height: 1.5;
}

.card {
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin: 0 24rpx 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(232, 131, 124, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.card-sub {
  font-size: 24rpx;
  color: #bbb;
}

.chart-area {
  padding: 20rpx 0;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 260rpx;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.bar-val {
  font-size: 20rpx;
  color: #999;
}

.bar {
  width: 40rpx;
  background: linear-gradient(180deg, #e8837c, #f8bbd0);
  border-radius: 8rpx 8rpx 0 0;
  min-height: 20rpx;
}

.bar-label {
  font-size: 20rpx;
  color: #bbb;
}

.chart-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f8f0f0;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
}

.summary-label {
  font-size: 22rpx;
  color: #999;
}

.summary-val {
  font-size: 28rpx;
  font-weight: 600;
  color: #e8837c;
}

.symptom-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.symptom-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.symptom-name {
  font-size: 26rpx;
  color: #666;
  width: 140rpx;
  flex-shrink: 0;
}

.symptom-bar-bg {
  flex: 1;
  height: 16rpx;
  background: #f5f0f0;
  border-radius: 8rpx;
  overflow: hidden;
}

.symptom-bar-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.3s;
}

.symptom-bar-fill.low { background: #81c784; }
.symptom-bar-fill.mid { background: #ffb74d; }
.symptom-bar-fill.high { background: #e57373; }

.symptom-val {
  font-size: 22rpx;
  color: #999;
  width: 120rpx;
  text-align: right;
  flex-shrink: 0;
}

.advice-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.advice-item {
  display: flex;
  gap: 16rpx;
  padding: 16rpx;
  background: #fef7f6;
  border-radius: 16rpx;
}

.advice-icon {
  font-size: 36rpx;
  flex-shrink: 0;
}

.advice-content {
  flex: 1;
}

.advice-title {
  font-size: 26rpx;
  font-weight: 500;
  color: #333;
  display: block;
  margin-bottom: 6rpx;
}

.advice-text {
  font-size: 24rpx;
  color: #666;
  line-height: 1.5;
}

.ask-btn {
  margin-top: 24rpx;
  background: linear-gradient(135deg, #e8837c, #d4625a);
  color: #fff;
  border: none;
  border-radius: 20rpx;
  padding: 22rpx;
  font-size: 28rpx;
}
</style>
