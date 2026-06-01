<template>
  <view class="profile-page">
    <!-- 顶部 -->
    <view class="user-header">
      <view class="header-bg" @tap="changeBg">
        <image v-if="headerBg" :src="headerBg" class="bg-img" mode="aspectFill" />
        <view v-else class="bg-default"></view>
      </view>
      <view class="header-actions">
        <view class="settings-btn" @tap="goSettings">
          <text class="settings-icon">⚙</text>
        </view>
      </view>
      <image
        :src="avatar || '/static/default-avatar.png'"
        class="user-avatar"
        mode="aspectFill"
        @tap="chooseAvatar"
      />
      <text class="user-name">{{ username }}</text>
      <view class="bio-row" @tap="editBio">
        <text class="user-bio">{{ bio || '点击编辑个人简介...' }}</text>
        <text class="bio-edit">✏️</text>
      </view>
      <view class="mode-badge">
        <text class="mode-text">{{ currentModeName }}</text>
      </view>
    </view>

    <!-- BMI -->
    <view class="bmi-card" v-if="profile.height && profile.weight">
      <view class="bmi-left">
        <text class="bmi-num">{{ bmi }}</text>
        <text class="bmi-label">BMI</text>
      </view>
      <view class="bmi-right">
        <text class="bmi-status">{{ bmiStatus }}</text>
        <view class="bmi-bar">
          <view class="bmi-fill" :style="{ width: bmiPercent + '%' }"></view>
        </view>
      </view>
    </view>

    <!-- 个人主页入口 -->
    <view class="card menu-card">
      <view class="menu-item" @tap="goMyProfile">
        <text class="menu-icon">👤</text>
        <text class="menu-text">我的主页</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- 基本信息 -->
    <view class="card">
      <view class="card-header">
        <text class="card-title">基本信息</text>
        <text class="edit-link" @tap="editMode = !editMode">{{ editMode ? '完成' : '编辑' }}</text>
      </view>
      <view class="field-row">
        <text class="field-label">性别</text>
        <picker :range="genders" @change="onGenderChange" :value="genderIndex" :disabled="!editMode">
          <text class="field-value">{{ profile.gender === 'male' ? '男' : '女' }} {{ editMode ? '▾' : '' }}</text>
        </picker>
      </view>
      <view class="field-row">
        <text class="field-label">年龄</text>
        <input v-if="editMode" v-model="profile.age" type="number" class="field-input" placeholder="25" />
        <text v-else class="field-value">{{ profile.age || '未设置' }}</text>
      </view>
      <view class="field-row">
        <text class="field-label">身高(cm)</text>
        <input v-if="editMode" v-model="profile.height" type="digit" class="field-input" placeholder="165" />
        <text v-else class="field-value">{{ profile.height || '未设置' }}</text>
      </view>
      <view class="field-row">
        <text class="field-label">体重(kg)</text>
        <input v-if="editMode" v-model="profile.weight" type="digit" class="field-input" placeholder="55" />
        <text v-else class="field-value">{{ profile.weight || '未设置' }}</text>
      </view>
      <view class="field-row">
        <text class="field-label">目标体重</text>
        <input v-if="editMode" v-model="profile.targetWeight" type="digit" class="field-input" placeholder="50" />
        <text v-else class="field-value">{{ profile.targetWeight || '未设置' }} kg</text>
      </view>
    </view>

    <!-- 模式切换 -->
    <view class="card">
      <text class="card-title">当前模式</text>
      <view class="mode-grid">
        <view
          v-for="m in modeOptions"
          :key="m.id"
          class="mode-item"
          :class="{ active: appMode === m.id }"
          @tap="switchMode(m.id)"
        >
          <text class="mode-emoji">{{ m.icon }}</text>
          <text class="mode-name">{{ m.name }}</text>
        </view>
      </view>
    </view>

    <!-- 健康目标 -->
    <view class="card">
      <text class="card-title">健康目标</text>
      <view class="field-row">
        <text class="field-label">健身目标</text>
        <picker :range="goals" @change="onGoalChange" :disabled="!editMode">
          <text class="field-value">{{ profile.goal || '选择' }} {{ editMode ? '▾' : '' }}</text>
        </picker>
      </view>
      <view class="field-row">
        <text class="field-label">饮食偏好</text>
        <input v-if="editMode" v-model="profile.dietary" class="field-input" placeholder="如: 素食" />
        <text v-else class="field-value">{{ profile.dietary || '未设置' }}</text>
      </view>
    </view>

    <!-- 设置菜单 -->
    <view class="card menu-card">
      <view class="menu-item" @tap="clearHistory">
        <text class="menu-icon">🗑</text>
        <text class="menu-text">清除对话记录</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="showAbout">
        <text class="menu-icon">ℹ️</text>
        <text class="menu-text">关于 FitHer</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="logout">
        <text class="menu-icon">🚪</text>
        <text class="menu-text" style="color: #e55;">退出登录</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- 保存按钮 -->
    <button v-if="editMode" class="save-btn" @tap="saveProfile" :loading="saving">
      保存信息
    </button>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { api } from "@/utils/api";

const username = ref("");
const avatar = ref("");
const bio = ref("");
const headerBg = ref("");
const saving = ref(false);
const editMode = ref(false);
const genders = ["女", "男"];
const goals = ["减脂", "塑形", "增肌", "保持", "康复"];
const genderIndex = ref(0);

const modeOptions = [
  { id: "period", name: "经期", icon: "🌸" },
  { id: "pregnancy", name: "备孕", icon: "🤰" },
  { id: "baby", name: "怀孕", icon: "👶" },
  { id: "parenting", name: "育儿", icon: "🍼" },
];

const appMode = ref("period");

const currentModeName = computed(() => {
  return modeOptions.find((m) => m.id === appMode.value)?.name || "经期";
});

const profile = ref({
  gender: "female",
  age: "",
  height: "",
  weight: "",
  targetWeight: "",
  goal: "",
  dietary: "",
});

const bmi = computed(() => {
  const h = parseFloat(profile.value.height as string) / 100;
  const w = parseFloat(profile.value.weight as string);
  if (!h || !w) return "0";
  return (w / (h * h)).toFixed(1);
});

const bmiStatus = computed(() => {
  const v = parseFloat(bmi.value);
  if (v < 18.5) return "偏瘦";
  if (v < 24) return "正常";
  if (v < 28) return "偏重";
  return "肥胖";
});

const bmiPercent = computed(() => {
  const v = parseFloat(bmi.value);
  return Math.min(Math.max((v / 35) * 100, 5), 100);
});

onShow(() => {
  username.value = uni.getStorageSync("username") || "";
  avatar.value = uni.getStorageSync("avatar") || "";
  bio.value = uni.getStorageSync("user_bio") || "";
  headerBg.value = uni.getStorageSync("user_header_bg") || "";
  appMode.value = uni.getStorageSync("appMode") || "period";
  loadProfile();
});

function loadProfile() {
  const key = `profile_${username.value}`;
  const saved = uni.getStorageSync(key);
  if (saved) {
    try {
      const p = JSON.parse(saved);
      profile.value = { ...profile.value, ...p };
      genderIndex.value = p.gender === "male" ? 1 : 0;
    } catch {}
  }
}

function onGenderChange(e: any) {
  genderIndex.value = e.detail.value;
  profile.value.gender = e.detail.value === 1 ? "male" : "female";
}

function onGoalChange(e: any) {
  profile.value.goal = goals[e.detail.value];
}

function switchMode(id: string) {
  appMode.value = id;
  uni.setStorageSync("appMode", id);
  uni.showToast({ title: `已切换到${modeOptions.find(m => m.id === id)?.name}模式`, icon: "none" });
}

function chooseAvatar() {
  uni.chooseImage({
    count: 1,
    sizeType: ["compressed"],
    success: (res) => {
      avatar.value = res.tempFilePaths[0];
      uni.setStorageSync("avatar", avatar.value);
    },
  });
}

function editBio() {
  uni.showModal({
    title: "编辑个人简介",
    editable: true,
    placeholderText: "介绍一下自己吧...",
    content: bio.value,
    success: (res) => {
      if (res.confirm) {
        bio.value = res.content || "";
        uni.setStorageSync("user_bio", bio.value);
        uni.showToast({ title: "已保存", icon: "success" });
      }
    },
  });
}

function changeBg() {
  uni.showActionSheet({
    itemList: ["选择图片", "恢复默认"],
    success: (res) => {
      if (res.tapIndex === 0) {
        uni.chooseImage({
          count: 1,
          sizeType: ["compressed"],
          success: (imgRes) => {
            headerBg.value = imgRes.tempFilePaths[0];
            uni.setStorageSync("user_header_bg", headerBg.value);
          },
        });
      } else {
        headerBg.value = "";
        uni.removeStorageSync("user_header_bg");
        uni.showToast({ title: "已恢复默认", icon: "none" });
      }
    },
  });
}

function goMyProfile() {
  uni.setStorageSync("view_user", username.value);
  uni.navigateTo({ url: "/pages/profile/user-profile" });
}

function goSettings() {
  uni.navigateTo({ url: "/pages/settings/settings" });
}

async function saveProfile() {
  saving.value = true;
  const key = `profile_${username.value}`;
  uni.setStorageSync(key, JSON.stringify(profile.value));
  try {
    await api({
      url: "/users/save-profile",
      method: "PUT",
      data: profile.value,
    });
  } catch {}
  editMode.value = false;
  uni.showToast({ title: "已保存", icon: "success" });
  saving.value = false;
}

function clearHistory() {
  uni.showModal({
    title: "确认",
    content: "清除所有AI对话记录？",
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync(`fitherHistories_${username.value}`);
        uni.showToast({ title: "已清除", icon: "success" });
      }
    },
  });
}

function showAbout() {
  uni.showModal({
    title: "FitHer",
    content: "你的私人健康AI助手\n版本 1.0.0\n\n专注女性健康，陪你度过每一天\n\n© 2026 FitHer Team",
    showCancel: false,
  });
}

function logout() {
  uni.showModal({
    title: "确认退出？",
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync("token");
        uni.removeStorageSync("username");
        uni.reLaunch({ url: "/pages/login/login" });
      }
    },
  });
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #fff5f5;
  padding-bottom: 160rpx;
}

.user-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0;
  padding-bottom: 32rpx;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  position: relative;
  overflow: hidden;
}

.header-bg {
  width: 100%;
  height: 280rpx;
  position: relative;
}

.bg-img {
  width: 100%;
  height: 100%;
}

.bg-default {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
}

.header-actions {
  position: absolute;
  top: 88rpx;
  right: 32rpx;
  z-index: 2;
}

.settings-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.settings-icon {
  font-size: 36rpx;
}

.user-avatar {
  width: 130rpx;
  height: 130rpx;
  border-radius: 50%;
  border: 6rpx solid rgba(255,255,255,0.5);
  margin-bottom: 16rpx;
}

.user-name {
  font-size: 38rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.user-bio {
  font-size: 24rpx;
  color: rgba(255,255,255,0.8);
}

.bio-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.bio-edit {
  font-size: 20rpx;
}

.mode-badge {
  background: rgba(255,255,255,0.2);
  padding: 8rpx 24rpx;
  border-radius: 20rpx;
}

.mode-text {
  color: #fff;
  font-size: 24rpx;
}

.bmi-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx 32rpx;
  margin: -16rpx 24rpx 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(232, 131, 124, 0.1);
}

.bmi-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 28rpx;
}

.bmi-num {
  font-size: 48rpx;
  font-weight: 700;
  color: var(--primary);
  line-height: 1;
}

.bmi-label {
  font-size: 22rpx;
  color: #999;
  margin-top: 4rpx;
}

.bmi-right { flex: 1; }

.bmi-status {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  display: block;
  margin-bottom: 12rpx;
}

.bmi-bar {
  height: 12rpx;
  background: #f5e8e7;
  border-radius: 6rpx;
  overflow: hidden;
}

.bmi-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #ff9800, #f44336);
  border-radius: 6rpx;
  transition: width 0.3s;
}

.card {
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx 32rpx;
  margin: 0 24rpx 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(232, 131, 124, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.edit-link {
  font-size: 26rpx;
  color: var(--primary);
}

.field-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #f8f0f0;
}

.field-row:last-child { border-bottom: none; }
.field-label { font-size: 28rpx; color: #666; }
.field-value { font-size: 28rpx; color: #333; }
.field-input { width: 200rpx; text-align: right; font-size: 28rpx; color: #333; }

.mode-grid {
  display: flex;
  gap: 16rpx;
}

.mode-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 20rpx 8rpx;
  border-radius: 16rpx;
  background: #f8f0f0;
}

.mode-item.active {
  background: var(--primary-light);
  border: 2rpx solid var(--primary-border);
}

.mode-emoji { font-size: 36rpx; }
.mode-name { font-size: 24rpx; color: #666; }
.mode-item.active .mode-name { color: var(--primary); font-weight: 500; }

.menu-card { padding: 0 32rpx; }

.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 0;
  border-bottom: 1rpx solid #f8f0f0;
}

.menu-item:last-child { border-bottom: none; }
.menu-icon { font-size: 32rpx; margin-right: 16rpx; }
.menu-text { flex: 1; font-size: 28rpx; color: #333; }
.menu-arrow { font-size: 28rpx; color: #ccc; }

.save-btn {
  margin: 24rpx;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
  border: none;
  border-radius: 20rpx;
  padding: 26rpx;
  font-size: 30rpx;
  font-weight: 500;
}
</style>
