<template>
  <view class="settings-page">
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
          <text class="setting-value">{{ remindDays[remindDaysIndex] }}</text>
        </picker>
      </view>
    </view>

    <view class="card">
      <text class="card-title">隐私</text>
      <view class="setting-row">
        <text class="setting-label">谁可以看我的动态</text>
        <picker :range="privacyOptions" @change="onPrivacyChange" :value="privacyIndex">
          <text class="setting-value">{{ privacyOptions[privacyIndex] }}</text>
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
      <view class="setting-row" @tap="clearCache">
        <text class="setting-label">清除缓存</text>
        <text class="setting-arrow">></text>
      </view>
    </view>

    <view class="card">
      <text class="card-title">账号</text>
      <view class="setting-row" @tap="changePassword">
        <text class="setting-label">修改密码</text>
        <text class="setting-arrow">></text>
      </view>
      <view class="setting-row" @tap="deleteAccount">
        <text class="setting-label" style="color: #e55;">注销账号</text>
        <text class="setting-arrow">></text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";

const remindDays = ["1天", "2天", "3天", "5天", "7天"];
const privacyOptions = ["所有人", "好友", "仅自己"];

const remindDaysIndex = ref(2);
const privacyIndex = ref(0);
const soundEnabled = ref(true);
const vibrationEnabled = ref(true);
const periodRemind = ref(true);
const waterRemind = ref(true);
const interactNotif = ref(true);
const allowStranger = ref(false);
const showOnline = ref(true);

function save() {
  uni.setStorageSync("settings", JSON.stringify({
    remindDaysIndex: remindDaysIndex.value,
    privacyIndex: privacyIndex.value,
    soundEnabled: soundEnabled.value,
    vibrationEnabled: vibrationEnabled.value,
    periodRemind: periodRemind.value,
    waterRemind: waterRemind.value,
    interactNotif: interactNotif.value,
    allowStranger: allowStranger.value,
    showOnline: showOnline.value,
  }));
}

onShow(() => {
  const saved = uni.getStorageSync("settings");
  if (saved) {
    try {
      const s = JSON.parse(saved);
      remindDaysIndex.value = s.remindDaysIndex ?? 2;
      privacyIndex.value = s.privacyIndex ?? 0;
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

function onRemindDaysChange(e: any) { remindDaysIndex.value = e.detail.value; save(); }
function onPrivacyChange(e: any) { privacyIndex.value = e.detail.value; save(); }
function toggleSound(e: any) { soundEnabled.value = e.detail.value; save(); }
function toggleVibration(e: any) { vibrationEnabled.value = e.detail.value; save(); }
function togglePeriodRemind(e: any) { periodRemind.value = e.detail.value; save(); }
function toggleWaterRemind(e: any) { waterRemind.value = e.detail.value; save(); }
function toggleInteractNotif(e: any) { interactNotif.value = e.detail.value; save(); }
function toggleStranger(e: any) { allowStranger.value = e.detail.value; save(); }
function toggleOnline(e: any) { showOnline.value = e.detail.value; save(); }

function clearCache() {
  uni.showModal({
    title: "清除缓存",
    content: "确定要清除所有本地缓存数据吗？",
    success: (res) => {
      if (res.confirm) {
        uni.clearStorageSync();
        uni.showToast({ title: "已清除", icon: "success" });
      }
    }
  });
}

function changePassword() {
  uni.showModal({
    title: "修改密码",
    editable: true,
    placeholderText: "输入原密码",
    success: (res1) => {
      if (!res1.confirm || !res1.content) return;
      const oldPassword = res1.content;
      uni.showModal({
        title: "修改密码",
        editable: true,
        placeholderText: "输入新密码（至少6位）",
        success: async (res2) => {
          if (!res2.confirm || !res2.content) return;
          const newPassword = res2.content;
          if (newPassword.length < 6) {
            uni.showToast({ title: "新密码至少6位", icon: "none" });
            return;
          }
          try {
            const token = uni.getStorageSync("token");
            const resp = await new Promise<any>((resolve, reject) => {
              uni.request({
                url: "http://127.0.0.1:8000/users/change-password",
                method: "POST",
                header: {
                  "Content-Type": "application/json",
                  "Authorization": `Bearer ${token}`,
                },
                data: { old_password: oldPassword, new_password: newPassword },
                success: (res) => resolve(res),
                fail: reject,
              });
            });
            if (resp.statusCode === 200) {
              uni.showToast({ title: "密码修改成功", icon: "success" });
            } else {
              const msg = resp.data?.detail || "修改失败";
              uni.showToast({ title: msg, icon: "none" });
            }
          } catch (e) {
            uni.showToast({ title: "网络错误", icon: "none" });
          }
        },
      });
    },
  });
}

function deleteAccount() {
  uni.showModal({
    title: "注销账号",
    content: "注销后所有数据将被删除，确定要注销吗？",
    success: (res) => {
      if (res.confirm) {
        uni.showToast({ title: "账号注销功能开发中", icon: "none" });
      }
    }
  });
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20rpx 0;
}

.card {
  background: #fff;
  margin: 20rpx 24rpx;
  border-radius: 16rpx;
  padding: 8rpx 24rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  padding: 20rpx 0 12rpx;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.setting-row:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 28rpx;
  color: #333;
}

.setting-value {
  font-size: 28rpx;
  color: #666;
}

.setting-arrow {
  font-size: 28rpx;
  color: #ccc;
}
</style>
