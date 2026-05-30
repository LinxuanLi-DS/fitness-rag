<template>
  <view class="analysis-page">
    <!-- 顶部 -->
    <view class="header">
      <text class="header-title">健康分析</text>
      <text class="header-sub">了解你的身体变化</text>
    </view>

    <!-- 无数据状态 -->
    <view v-if="!hasData" class="no-data">
      <view class="no-data-icon">📊</view>
      <text class="no-data-title">暂无分析数据</text>
      <text class="no-data-desc">记录至少2次完整经期后\n即可查看健康分析报告</text>
      <button class="go-record-btn" @tap="goRecord">去记录经期</button>
    </view>

    <!-- 有数据 -->
    <view v-else>
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
          <text class="card-sub">近{{ cycleData.length }}次</text>
        </view>
        <view class="chart-area">
          <view class="chart-bars">
            <view v-for="(d, i) in cycleData" :key="i" class="bar-item">
              <text class="bar-val">{{ d.days }}天</text>
              <view class="bar" :style="{ height: barHeight(d.days) }"></view>
              <text class="bar-label">{{ d.label }}</text>
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
          <text class="card-title">症状趋势</text>
          <text class="card-sub">近期记录</text>
        </view>
        <view v-if="symptomTrends.length === 0" class="empty-section">
          <text class="empty-text">记录经期症状后可查看趋势</text>
        </view>
        <view v-else class="symptom-list">
          <view v-for="s in symptomTrends" :key="s.name" class="symptom-item">
            <text class="symptom-name">{{ s.name }}</text>
            <view class="symptom-bar-bg">
              <view class="symptom-bar-fill" :style="{ width: s.percent + '%' }" :class="s.level"></view>
            </view>
            <text class="symptom-val">{{ s.trend }}</text>
          </view>
        </view>
      </view>

      <!-- 体重趋势 -->
      <view class="card" v-if="weightHistory.length >= 2">
        <view class="card-header">
          <text class="card-title">体重趋势</text>
          <text class="card-sub">近期记录</text>
        </view>
        <view class="weight-trend">
          <text class="weight-change">{{ weightChange }}</text>
          <text class="weight-detail">最近: {{ latestWeight }}kg · 最早: {{ earliestWeight }}kg</text>
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
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onShow } from "@dcloudio/uni-app";

const history = ref<any[]>([]);
const weightHistory = ref<{ date: string; weight: number }[]>([]);

const hasData = computed(() => {
  // 至少2条完整记录（有start_date和end_date）
  const complete = history.value.filter((h: any) => h.start_date && h.end_date);
  return complete.length >= 2;
});

// 从历史记录计算周期数据
const cycleData = computed(() => {
  const complete = history.value.filter((h: any) => h.start_date && h.end_date);
  if (complete.length < 2) return [];

  const result: { label: string; days: number }[] = [];
  for (let i = 0; i < complete.length - 1 && result.length < 6; i++) {
    const start1 = new Date(complete[i].start_date);
    const start2 = new Date(complete[i + 1].start_date);
    const cycleDays = Math.round((start1.getTime() - start2.getTime()) / (1000 * 60 * 60 * 24));
    if (cycleDays > 0 && cycleDays < 60) {
      const month = start1.getMonth() + 1;
      result.push({ label: `${month}月`, days: cycleDays });
    }
  }
  return result.reverse();
});

const avgCycle = computed(() => {
  if (cycleData.value.length === 0) return "--";
  const total = cycleData.value.reduce((s, d) => s + d.days, 0);
  return String(Math.round(total / cycleData.value.length));
});

const avgPeriod = computed(() => {
  const complete = history.value.filter((h: any) => h.duration);
  if (complete.length === 0) return "--";
  const total = complete.reduce((s, h: any) => s + (h.duration || 0), 0);
  return String(Math.round(total / complete.length));
});

const regularity = computed(() => {
  if (cycleData.value.length < 2) return 0;
  const avg = cycleData.value.reduce((s, d) => s + d.days, 0) / cycleData.value.length;
  const deviations = cycleData.value.map(d => Math.abs(d.days - avg));
  const avgDev = deviations.reduce((s, d) => s + d, 0) / deviations.length;
  // 平均偏差越小越规律，偏差0=100%，偏差7天=0%
  return Math.max(0, Math.round(100 - (avgDev / 7) * 100));
});

const healthScore = computed(() => {
  let score = 50; // 基础分
  // 周期规律度 (0-25分)
  score += Math.round(regularity.value * 0.25);
  // 周期长度正常 21-35天 (0-15分)
  const avg = parseInt(avgCycle.value as string);
  if (avg >= 21 && avg <= 35) score += 15;
  else if (avg >= 18 && avg <= 40) score += 8;
  // 经期长度正常 3-7天 (0-10分)
  const period = parseInt(avgPeriod.value as string);
  if (period >= 3 && period <= 7) score += 10;
  else if (period >= 2 && period <= 8) score += 5;
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
  const avg = parseInt(avgCycle.value as string);
  if (s >= 90) return "你的身体状态很好，继续保持！";
  if (s >= 75) return "整体不错，注意规律作息";
  if (avg < 21 || avg > 35) return `平均周期${avg}天，偏${avg < 21 ? '短' : '长'}，建议关注`;
  return "建议多关注身体信号，适当调整";
});

// 症状趋势 - 从每日记录统计
const symptomTrends = computed(() => {
  const username = uni.getStorageSync("username") || "";
  const symptomCount: Record<string, number> = {};
  let totalDays = 0;

  // 扫描最近30天
  for (let i = 0; i < 30; i++) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().split("T")[0];
    const key = `daily_${username}_${dateStr}_symptoms`;
    const saved = uni.getStorageSync(key);
    if (saved) {
      totalDays++;
      try {
        const arr: string[] = JSON.parse(saved);
        arr.forEach((s) => { symptomCount[s] = (symptomCount[s] || 0) + 1; });
      } catch {}
    }
  }

  if (totalDays === 0) return [];

  return Object.entries(symptomCount)
    .map(([name, count]) => {
      const percent = Math.round((count / totalDays) * 100);
      let level = "low";
      if (percent > 60) level = "high";
      else if (percent > 30) level = "mid";
      let trend = "→ 持平";
      if (percent > 50) trend = "↑ 频繁";
      else if (percent < 20) trend = "↓ 偶尔";
      return { name, percent, level, trend };
    })
    .sort((a, b) => b.percent - a.percent)
    .slice(0, 6);
});

// 体重趋势
const latestWeight = computed(() => {
  if (weightHistory.value.length === 0) return "--";
  return String(weightHistory.value[weightHistory.value.length - 1].weight);
});

const earliestWeight = computed(() => {
  if (weightHistory.value.length === 0) return "--";
  return String(weightHistory.value[0].weight);
});

const weightChange = computed(() => {
  if (weightHistory.value.length < 2) return "";
  const diff = weightHistory.value[weightHistory.value.length - 1].weight - weightHistory.value[0].weight;
  const sign = diff > 0 ? "+" : "";
  return `${sign}${diff.toFixed(1)}kg`;
});

// AI建议 - 基于真实数据生成
const advices = computed(() => {
  const result: { icon: string; title: string; text: string }[] = [];
  const avg = parseInt(avgCycle.value as string);
  const period = parseInt(avgPeriod.value as string);
  const reg = regularity.value;

  if (!isNaN(avg)) {
    if (avg < 21) {
      result.push({ icon: "⚠️", title: "周期偏短", text: `你的平均周期只有${avg}天，低于正常范围(21-35天)。建议就医检查激素水平。` });
    } else if (avg > 35) {
      result.push({ icon: "⚠️", title: "周期偏长", text: `你的平均周期${avg}天，高于正常范围。可能与压力、体重变化有关，建议关注。` });
    } else {
      result.push({ icon: "✅", title: "周期正常", text: `平均周期${avg}天，在正常范围内。` });
    }
  }

  if (!isNaN(period)) {
    if (period < 3) {
      result.push({ icon: "🩸", title: "经期偏短", text: `平均经期${period}天，偏短。注意是否有气血不足的情况。` });
    } else if (period > 7) {
      result.push({ icon: "🩸", title: "经期偏长", text: `平均经期${period}天，超过7天建议就医排查。` });
    }
  }

  if (reg < 60) {
    result.push({ icon: "📅", title: "规律度待提升", text: "周期波动较大，建议保持规律作息、减少压力，适当运动。" });
  } else {
    result.push({ icon: "🌙", title: "作息建议", text: "保持规律的作息习惯，卵泡期适当增加运动强度。" });
  }

  result.push({ icon: "🥗", title: "饮食建议", text: "经前多补充镁和B族维生素，经期注意补铁，黄体期少吃甜食。" });

  return result;
});

function barHeight(days: number): string {
  return Math.round((days / 40) * 200) + "rpx";
}

function askAI() {
  uni.navigateTo({ url: "/pages/chat/chat?assistant=shiqing" });
}

function goRecord() {
  uni.switchTab({ url: "/pages/period/period" });
}

onShow(() => {
  // 加载经期历史
  const saved = uni.getStorageSync("period_history");
  if (saved) {
    try { history.value = JSON.parse(saved); } catch {}
  }

  // 加载体重历史
  const username = uni.getStorageSync("username") || "";
  const weights: { date: string; weight: number }[] = [];
  for (let i = 0; i < 60; i++) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().split("T")[0];
    const w = uni.getStorageSync(`daily_${username}_${dateStr}_weight`);
    if (w) {
      const num = parseFloat(w);
      if (!isNaN(num)) weights.unshift({ date: dateStr, weight: num });
    }
  }
  weightHistory.value = weights;
});
</script>

<style scoped>
.analysis-page { min-height: 100vh; background: #fff5f5; padding-bottom: 160rpx; }
.header { padding: 88rpx 32rpx 28rpx; background: linear-gradient(135deg, #e8837c, #d4625a); }
.header-title { font-size: 38rpx; font-weight: 600; color: #fff; display: block; }
.header-sub { font-size: 24rpx; color: rgba(255,255,255,0.8); margin-top: 6rpx; }

/* No data state */
.no-data { display: flex; flex-direction: column; align-items: center; padding: 120rpx 60rpx; }
.no-data-icon { font-size: 120rpx; margin-bottom: 24rpx; }
.no-data-title { font-size: 36rpx; font-weight: 600; color: #333; margin-bottom: 16rpx; }
.no-data-desc { font-size: 26rpx; color: #999; text-align: center; line-height: 1.6; margin-bottom: 40rpx; }
.go-record-btn { background: linear-gradient(135deg, #e8837c, #d4625a); color: #fff; border: none; border-radius: 32rpx; padding: 24rpx 60rpx; font-size: 30rpx; }

.score-card { display: flex; align-items: center; background: #fff; border-radius: 24rpx; padding: 36rpx 32rpx; margin: -20rpx 24rpx 24rpx; box-shadow: 0 8rpx 32rpx rgba(232,131,124,0.12); }
.score-circle { width: 140rpx; height: 140rpx; border-radius: 50%; background: linear-gradient(135deg, #fce4ec, #f8bbd0); display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 28rpx; }
.score-num { font-size: 48rpx; font-weight: 700; color: #d4625a; line-height: 1; }
.score-label { font-size: 20rpx; color: #e8837c; margin-top: 4rpx; }
.score-desc { flex: 1; }
.score-status { font-size: 34rpx; font-weight: 600; color: #333; display: block; margin-bottom: 8rpx; }
.score-tip { font-size: 24rpx; color: #999; line-height: 1.5; }

.card { background: #fff; border-radius: 24rpx; padding: 28rpx; margin: 0 24rpx 20rpx; box-shadow: 0 2rpx 12rpx rgba(232,131,124,0.05); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24rpx; }
.card-title { font-size: 30rpx; font-weight: 600; color: #333; }
.card-sub { font-size: 24rpx; color: #bbb; }

.chart-area { padding: 20rpx 0; }
.chart-bars { display: flex; justify-content: space-around; align-items: flex-end; height: 260rpx; }
.bar-item { display: flex; flex-direction: column; align-items: center; gap: 8rpx; }
.bar-val { font-size: 20rpx; color: #999; }
.bar { width: 40rpx; background: linear-gradient(180deg, #e8837c, #f8bbd0); border-radius: 8rpx 8rpx 0 0; min-height: 20rpx; }
.bar-label { font-size: 20rpx; color: #bbb; }

.chart-summary { display: flex; justify-content: space-around; margin-top: 20rpx; padding-top: 20rpx; border-top: 1rpx solid #f8f0f0; }
.summary-item { display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.summary-label { font-size: 22rpx; color: #999; }
.summary-val { font-size: 28rpx; font-weight: 600; color: #e8837c; }

.empty-section { text-align: center; padding: 32rpx 0; }
.empty-text { font-size: 26rpx; color: #ccc; }

.symptom-list { display: flex; flex-direction: column; gap: 20rpx; }
.symptom-item { display: flex; align-items: center; gap: 16rpx; }
.symptom-name { font-size: 26rpx; color: #666; width: 140rpx; flex-shrink: 0; }
.symptom-bar-bg { flex: 1; height: 16rpx; background: #f5f0f0; border-radius: 8rpx; overflow: hidden; }
.symptom-bar-fill { height: 100%; border-radius: 8rpx; transition: width 0.3s; }
.symptom-bar-fill.low { background: #81c784; }
.symptom-bar-fill.mid { background: #ffb74d; }
.symptom-bar-fill.high { background: #e57373; }
.symptom-val { font-size: 22rpx; color: #999; width: 120rpx; text-align: right; flex-shrink: 0; }

.weight-trend { text-align: center; padding: 20rpx 0; }
.weight-change { font-size: 48rpx; font-weight: 700; color: #e8837c; display: block; margin-bottom: 8rpx; }
.weight-detail { font-size: 24rpx; color: #999; }

.advice-list { display: flex; flex-direction: column; gap: 20rpx; }
.advice-item { display: flex; gap: 16rpx; padding: 16rpx; background: #fef7f6; border-radius: 16rpx; }
.advice-icon { font-size: 36rpx; flex-shrink: 0; }
.advice-content { flex: 1; }
.advice-title { font-size: 26rpx; font-weight: 500; color: #333; display: block; margin-bottom: 6rpx; }
.advice-text { font-size: 24rpx; color: #666; line-height: 1.5; }

.ask-btn { margin-top: 24rpx; background: linear-gradient(135deg, #e8837c, #d4625a); color: #fff; border: none; border-radius: 20rpx; padding: 22rpx; font-size: 28rpx; }
</style>
