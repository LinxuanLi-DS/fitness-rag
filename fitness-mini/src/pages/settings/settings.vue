<template>
  <view class="settings-page">
    <view class="card">
      <text class="card-title">外观</text>
      <view class="setting-row">
        <text class="setting-label">主题颜色</text>
        <view class="theme-options">
          <view v-for="t in themes" :key="t.id" class="theme-dot" :class="{ active: currentTheme === t.id, [t.id]: true }" @tap="setTheme(t.id)"></view>
        </view>
      </view>
      <view class="setting-row">
        <text class="setting-label">字体大小</text>
        <picker :range="fontSizes" @change="onFontChange" :value="fontIndex">
          <text class="setting-value">{{ fontSizes[fontIndex] }} ▾</text>
        </picker>
      </view>
      <view class="setting-row">
        <text class="setting-label">深色模式</text>
        <switch :checked="darkMode" @change="toggleDark" color="#e8837c" />
      </view>
    </view>

    <view class="card">
      <text class="card-title">语言</text>
      <view class="setting-row">
        <text class="setting-label">界面语言</text>
        <picker :range="languages" @change="onLangChange" :value="langIndex">
          <text class="setting-value">{{ languages[langIndex] }} ▾</text>
        </picker>
      </view>
    </view>

    <view class="card">
      <text class="card-title">声音</text>
      <view class="setting-row">
        <text class="setting-label">消息提示音</text>
        <switch :checked="soundEnabled" @change="toggleSound" color="#e8837c" />
      </view>
      <view class="setting-row">
        <text class="setting-label">振动反馈</text>
        <switch :checked="vibrationEnabled" @change="toggleVibration" color="#e8837c" />
      </view>
    </view>

    <view class="card">
      <text class="card-title">通知</text>
      <view class="setting-row">
        <text class="setting-label">经期提醒</text>
        <switch :checked="periodRemind" @change="togglePeriodRemind" color="#e8837c" />
      </view>
      <view class="setting-row">
        <text class="setting-label">喝水提醒</text>
        <switch :checked="waterRemind" @change="toggleWaterRemind" color="#e8837c" />
      </view>
      <view class="setting-row">
        <text class="setting-label">互动消息通知</text>
        <switch :checked="interactNotif" @change="toggleInteractNotif" color="#e8837c" />
      </view>
      <view class="setting-row">
        <text class="setting-label">提前提醒天数</text>
        <picker :range="remindDays" @change="onRemindDaysChange" :value="remindDaysIndex">
          <text class="setting-value">{{ remindDays[remindDaysIndex] }} ▾</text>
        </picker>
      </view>
    </view>

    <view class="card">
      <text class="card-title">隐私</text>
      <view class="setting-row">
        <text class="setting-label">谁可以看我的动态</text>
        <picker :range="privacyOptions" @change="onPrivacyChange" :value="privacyIndex">
          <text class="setting-value">{{ privacyOptions[privacyIndex] }} ▾</text>
        </picker>
      </view>
      <view class="setting-row">
        <text class="setting-label">允许陌生人私信</text>
        <switch :checked="allowStranger" @change="toggleStranger" color="#e8837c" />
      </view>
      <view class="setting-row">
        <text class="setting-label">显示在线状态</text>
        <switch :checked="showOnline" @change="toggleOnline" color="#e8837c" />
      </view>
    </view>

    <view class="card">
      <text class="card-title">数据</text>
      <view class="setting-row" @tap="exportData">
        <text class="setting-label">导出数据</text>
        <text class="setting-arrow">›</text>
      </view>
      <view class="setting-row" @tap="clearCache">
        <text class="setting-label">清除缓存</text>
        <text class="setting-arrow">›</text>
      </view>
    </view>

    <view class="card">
      <text class="card-title">账号</text>
      <view class="setting-row" @tap="changePassword">
        <text class="setting-label">修改密码</text>
        <text class="setting-arrow">›</text>
      </view>
      <view class="setting-row" @tap="deleteAccount">
        <text class="setting-label" style="color: #e55;">注销账号</text>
        <text class="setting-arrow">›</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";

const themes = [
  { id: "pink", color: "#e8837c" },
  { id: "purple", color: "#9c27b0" },
  { id: "blue", color: "#42a5f5" },
  { id: "green", color: "#66bb6a" },
  { id: "orange", color: "#ff9800" },
];

const fontSizes = ["小", "中", "大"];
const languages = ["简体中文", "English", "日本語"];
const remindDays = ["1天", "2天", "3天", "5天", "7天"];
const privacyOptions = ["所有人", "好友", "仅自己"];

const currentTheme = ref("pink");
const fontIndex = ref(1);
const langIndex = ref(0);
const remindDaysIndex = ref(2);
const privacyIndex = ref(0);
const darkMode = ref(false);
const soundEnabled = ref(true);
const vibrationEnabled = ref(true);
const periodRemind = ref(true);
const waterRemind = ref(true);
const interactNotif = ref(true);
const allowStranger = ref(false);
const showOnline = ref(true);

onShow(() => {
  const saved = uni.getStorageSync("app_settings");
  if (saved) {
    try {
      const s = JSON.parse(saved);
      currentTheme.value = s.theme || "pink";
      fontIndex.value = s.fontIndex ?? 1;
      langIndex.value = s.langIndex ?? 0;
      remindDaysIndex.value = s.remindDaysIndex ?? 2;
      privacyIndex.value = s.privacyIndex ?? 0;
      darkMode.value = s.darkMode || false;
      soundEnabled.value = s.soundEnabled !== false;
      vibrationEnabled.value = s.vibrationEnabled !== false;
      periodRemind.value = s.periodRemind !== false;
      waterRemind.value = s.waterRemind !== false;
      interactNotif.value = s.interactNotif !== false;
      allowStranger.value = s.allowStranger || false;
      showOnline.value = s.showOnline !== false;
    } catch {}
  }
});

function save() {
  uni.setStorageSync("app_settings", JSON.stringify({
    theme: currentTheme.value, fontIndex: fontIndex.value, langIndex: langIndex.value,
    remindDaysIndex: remindDaysIndex.value, privacyIndex: privacyIndex.value,
    darkMode: darkMode.value, soundEnabled: soundEnabled.value, vibrationEnabled: vibrationEnabled.value,
    periodRemind: periodRemind.value, waterRemind: waterRemind.value, interactNotif: interactNotif.value,
    allowStranger: allowStranger.value, showOnline: showOnline.value,
  }));
}

function setTheme(id: string) { currentTheme.value = id; save(); uni.showToast({ title: "主题已切换", icon: "none" }); }
function onFontChange(e: any) { fontIndex.value = e.detail.value; save(); }
function onLangChange(e: any) { langIndex.value = e.detail.value; save(); uni.showToast({ title: "语言设置已保存（开发中）", icon: "none" }); }
function onRemindDaysChange(e: any) { remindDaysIndex.value = e.detail.value; save(); }
function onPrivacyChange(e: any) { privacyIndex.value = e.detail.value; save(); }
function toggleDark(e: any) { darkMode.value = e.detail.value; save(); uni.showToast({ title: "深色模式（开发中）", icon: "none" }); }
function toggleSound(e: any) { soundEnabled.value = e.detail.value; save(); }
function toggleVibration(e: any) { vibrationEnabled.value = e.detail.value; save(); }
function togglePeriodRemind(e: any) { periodRemind.value = e.detail.value; save(); }
function toggleWaterRemind(e: any) { waterRemind.value = e.detail.value; save(); }
function toggleInteractNotif(e: any) { interactNotif.value = e.detail.value; save(); }
function toggleStranger(e: any) { allowStranger.value = e.detail.value; save(); }
function toggleOnline(e: any) { showOnline.value = e.detail.value; save(); }
function exportData() { uni.showToast({ title: "导出数据（开发中）", icon: "none" }); }
function clearCache() {
  uni.showModal({ title: "确认", content: "清除所有缓存数据？", success: (res) => {
    if (res.confirm) { uni.clearStorageSync(); uni.showToast({ title: "已清除", icon: "success" }); }
  }});
}
function changePassword() { uni.showToast({ title: "修改密码（开发中）", icon: "none" }); }
function deleteAccount() {
  uni.showModal({ title: "注销账号", content: "注销后所有数据将被删除，确定要注销吗？", success: (res) => {
    if (res.confirm) { uni.showToast({ title: "账号注销功能开发中", icon: "none" }); }
  }});
}
</script>

<style scoped>
.settings-page { min-height: 100vh; background: #fff5f5; padding: 20rpx 0; padding-bottom: 60rpx; }
.card { background: #fff; border-radius: 24rpx; padding: 28rpx 32rpx; margin: 0 24rpx 20rpx; box-shadow: 0 2rpx 12rpx rgba(232,131,124,0.05); }
.card-title { font-size: 30rpx; font-weight: 600; color: #333; display: block; margin-bottom: 16rpx; }
.setting-row { display: flex; justify-content: space-between; align-items: center; padding: 18rpx 0; border-bottom: 1rpx solid #f8f0f0; }
.setting-row:last-child { border-bottom: none; }
.setting-label { font-size: 28rpx; color: #333; }
.setting-value { font-size: 28rpx; color: #999; }
.setting-arrow { font-size: 28rpx; color: #ccc; }
.theme-options { display: flex; gap: 16rpx; }
.theme-dot { width: 48rpx; height: 48rpx; border-radius: 50%; border: 3rpx solid transparent; }
.theme-dot.pink { background: #e8837c; }
.theme-dot.purple { background: #9c27b0; }
.theme-dot.blue { background: #42a5f5; }
.theme-dot.green { background: #66bb6a; }
.theme-dot.orange { background: #ff9800; }
.theme-dot.active { border-color: #333; transform: scale(1.1); }
</style>
