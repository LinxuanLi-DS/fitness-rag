<template>
  <view class="login-page">
    <view class="logo-area">
      <image src="/static/logo.png" class="logo" mode="aspectFit" />
      <text class="app-name">FitHer</text>
      <text class="app-desc">你的私人健康AI助手</text>
    </view>

    <view class="form-area">
      <!-- 微信一键登录 -->
      <button class="wx-login-btn" @tap="wxLogin" :loading="loading">
        <text class="wx-icon">💬</text>
        <text class="wx-text">微信一键登录</text>
      </button>

      <view class="divider">
        <view class="divider-line"></view>
        <text class="divider-text">或者</text>
        <view class="divider-line"></view>
      </view>

      <!-- 账号密码登录 -->
      <view class="input-group">
        <input
          v-model="username"
          placeholder="用户名"
          class="input-field"
          :maxlength="20"
        />
      </view>
      <view class="input-group">
        <input
          v-model="password"
          placeholder="密码"
          type="password"
          class="input-field"
          :maxlength="30"
        />
      </view>

      <button class="btn-primary login-btn" @tap="handleLogin" :loading="loading">
        登录
      </button>

      <view class="register-row" @tap="handleRegister">
        <text class="register-text">没有账号？立即注册</text>
      </view>
    </view>

    <view class="footer">
      <text class="footer-text">登录即表示同意用户协议和隐私政策</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { login, register, api } from "@/utils/api";

const username = ref("");
const password = ref("");
const loading = ref(false);

async function wxLogin() {
  loading.value = true;
  try {
    const loginRes = await new Promise<UniApp.LoginRes>((resolve, reject) => {
      uni.login({
        provider: "weixin",
        success: resolve,
        fail: reject,
      });
    });

    // Send code to backend
    const res = await api<{ access_token: string; username: string }>({
      url: "/users/wx-login",
      method: "POST",
      data: { code: loginRes.code },
    });

    uni.setStorageSync("token", res.access_token);
    uni.setStorageSync("username", res.username || "用户");
    uni.switchTab({ url: "/pages/index/index" });
  } catch (e: any) {
    console.error("wx login failed:", e);
    uni.showToast({ title: "微信登录失败，请重试", icon: "none" });
  }
  loading.value = false;
}

async function handleLogin() {
  if (!username.value || !password.value) {
    uni.showToast({ title: "请输入用户名和密码", icon: "none" });
    return;
  }
  loading.value = true;
  try {
    console.log("Attempting login with:", username.value);
    await login(username.value, password.value);
    uni.setStorageSync("username", username.value);
    console.log("Login successful, switching to index");
    uni.switchTab({ url: "/pages/index/index" });
  } catch (e: any) {
    console.error("Login failed:", e);
    const errMsg = e?.errMsg || e?.message || "登录失败";
    uni.showToast({ title: errMsg, icon: "none", duration: 3000 });
  }
  loading.value = false;
}

async function handleRegister() {
  if (!username.value || !password.value) {
    uni.showToast({ title: "请输入用户名和密码", icon: "none" });
    return;
  }
  loading.value = true;
  try {
    await register(username.value, password.value);
    uni.showToast({ title: "注册成功，请登录", icon: "success" });
  } catch (e: any) {
    uni.showToast({ title: "注册失败", icon: "none" });
  }
  loading.value = false;
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 60rpx 48rpx;
  background: linear-gradient(180deg, #fff5f5 0%, #ffe8e6 100%);
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;
}

.logo {
  width: 160rpx;
  height: 160rpx;
  margin-bottom: 24rpx;
  border-radius: 32rpx;
}

.app-name {
  font-size: 52rpx;
  font-weight: 700;
  color: #d4625a;
  margin-bottom: 12rpx;
}

.app-desc {
  font-size: 28rpx;
  color: #b08080;
}

.form-area {
  width: 100%;
}

.wx-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  background: #07c160;
  color: #fff;
  border: none;
  border-radius: 16rpx;
  padding: 28rpx;
  font-size: 32rpx;
  font-weight: 500;
  margin-bottom: 32rpx;
}

.wx-login-btn:active {
  opacity: 0.85;
}

.wx-icon {
  font-size: 36rpx;
}

.wx-text {
  color: #fff;
}

.divider {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 32rpx;
}

.divider-line {
  flex: 1;
  height: 1rpx;
  background: #e8c8c6;
}

.divider-text {
  font-size: 24rpx;
  color: #c0a0a0;
}

.input-group {
  margin-bottom: 20rpx;
}

.input-field {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx 32rpx;
  font-size: 30rpx;
  border: 2rpx solid #f0d0ce;
}

.login-btn {
  width: 100%;
  margin-top: 16rpx;
  margin-bottom: 20rpx;
}

.btn-primary {
  background: linear-gradient(135deg, #e8837c, #d4625a);
  color: #fff;
  border: none;
  border-radius: 16rpx;
  padding: 28rpx;
  font-size: 30rpx;
  font-weight: 500;
}

.btn-primary:active {
  opacity: 0.85;
}

.register-row {
  text-align: center;
  padding: 16rpx;
}

.register-text {
  font-size: 26rpx;
  color: #e8837c;
}

.footer {
  position: fixed;
  bottom: 60rpx;
  left: 0;
  right: 0;
  text-align: center;
}

.footer-text {
  font-size: 22rpx;
  color: #cbb;
}
</style>
