<template>
  <view class="training-page">
    <view class="card">
      <text class="card-title">今日训练</text>
      <view class="type-tabs">
        <view
          v-for="t in types"
          :key="t.id"
          class="type-tab"
          :class="{ active: selectedType === t.id }"
          @tap="selectedType = t.id"
        >
          <text>{{ t.emoji }} {{ t.name }}</text>
        </view>
      </view>

      <view class="exercise-list" v-if="exercises[selectedType]">
        <view
          v-for="ex in exercises[selectedType]"
          :key="ex"
          class="exercise-item"
          :class="{ done: isDone(ex) }"
          @tap="toggleExercise(ex)"
        >
          <text>{{ ex }}</text>
          <text v-if="isDone(ex)" class="check">✓</text>
        </view>
      </view>
    </view>

    <view class="card">
      <text class="card-title">训练记录</text>
      <view v-if="records.length === 0" class="empty">
        <text class="text-muted">还没有记录，开始训练吧</text>
      </view>
      <view v-for="(r, i) in records" :key="i" class="record-item">
        <text class="record-type">{{ r.type }}</text>
        <text class="record-detail">{{ r.detail }}</text>
        <text class="record-time">{{ r.time }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { onShow } from "@dcloudio/uni-app";

const types = [
  { id: "strength", name: "力量", emoji: "💪" },
  { id: "cardio", name: "有氧", emoji: "🏃" },
  { id: "stretch", name: "拉伸", emoji: "🧘" },
];

const exercises: Record<string, string[]> = {
  strength: ["深蹲 4x12", "硬拉 4x8", "卧推 4x10", "引体向上 3x8", "肩推 3x12", "弯举 3x15"],
  cardio: ["跑步 30min", "跳绳 20min", "椭圆机 25min", "游泳 30min", "骑车 40min"],
  stretch: ["猫牛式 2min", "下犬式 2min", "鸽子式 各2min", "婴儿式 3min", "脊柱扭转 各1min"],
};

const selectedType = ref("strength");
const doneExercises = ref<Set<string>>(new Set());
const records = ref<any[]>([]);

const storageKey = `training_${new Date().toISOString().split("T")[0]}`;

onShow(() => {
  loadRecords();
});

function loadRecords() {
  const saved = uni.getStorageSync(storageKey);
  if (saved) {
    const data = JSON.parse(saved);
    doneExercises.value = new Set(data.done || []);
    records.value = data.records || [];
  }
}

function isDone(ex: string) {
  return doneExercises.value.has(ex);
}

function toggleExercise(ex: string) {
  const newDone = new Set(doneExercises.value);
  if (newDone.has(ex)) {
    newDone.delete(ex);
  } else {
    newDone.add(ex);
    records.value.unshift({
      type: types.find((t) => t.id === selectedType.value)?.name || "",
      detail: ex,
      time: new Date().toLocaleTimeString().slice(0, 5),
    });
  }
  doneExercises.value = newDone;
  saveRecords();
}

function saveRecords() {
  uni.setStorageSync(
    storageKey,
    JSON.stringify({ done: Array.from(doneExercises.value), records: records.value })
  );
}
</script>

<style scoped>
.training-page {
  padding: 24rpx;
  padding-bottom: 120rpx;
}

.card {
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(232, 131, 124, 0.08);
}

.card-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 24rpx;
}

.type-tabs {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.type-tab {
  flex: 1;
  text-align: center;
  padding: 16rpx;
  border-radius: 12rpx;
  background: #f5f5f5;
  font-size: 28rpx;
}

.type-tab.active {
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 500;
}

.exercise-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 16rpx;
  border-bottom: 1rpx solid #f0f0f0;
  font-size: 28rpx;
}

.exercise-item.done {
  color: var(--primary);
  text-decoration: line-through;
}

.check {
  color: var(--primary);
  font-weight: 700;
}

.empty {
  text-align: center;
  padding: 40rpx;
}

.record-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
  font-size: 26rpx;
}

.record-type {
  color: var(--primary);
  font-weight: 500;
}

.record-detail {
  color: #666;
  flex: 1;
  margin: 0 16rpx;
}

.record-time {
  color: #bbb;
}
</style>
