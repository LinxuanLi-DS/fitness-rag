<script setup lang="ts">
import { onLaunch, onShow } from "@dcloudio/uni-app";

onLaunch(() => {
  console.log("App Launch");
  
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.redirectTo({ url: "/pages/login/login" });
  }
});
</script>

<style>
page {
  --primary: #e8837c;
  --primary-dark: #d4625a;
  --primary-light: #fff0ef;
  --primary-border: #f0d0ce;
  --bg: #fff5f5;
  --font-base: 28rpx;
  --font-small: 24rpx;
  --font-large: 32rpx;

  background-color: var(--bg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: var(--font-base);
}

.container {
  padding: 24rpx;
}

.card {
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
  border: none;
  border-radius: 16rpx;
  padding: 24rpx 48rpx;
  font-size: var(--font-base);
  font-weight: 500;
}

.btn-primary:active {
  opacity: 0.8;
}

.text-muted {
  color: #999;
  font-size: var(--font-small);
}
</style>
