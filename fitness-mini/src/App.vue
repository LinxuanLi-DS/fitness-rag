<script setup lang="ts">
import { onLaunch } from "@dcloudio/uni-app";

onLaunch(() => {
  console.log("App Launch");
  // Check login status
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.redirectTo({ url: "/pages/login/login" });
  }
});
</script>

<style>
page {
  background-color: #fff5f5;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.container {
  padding: 24rpx;
}

.card {
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(232, 131, 124, 0.08);
}

.btn-primary {
  background: linear-gradient(135deg, #e8837c, #d4625a);
  color: #fff;
  border: none;
  border-radius: 16rpx;
  padding: 24rpx 48rpx;
  font-size: 30rpx;
  font-weight: 500;
}

.btn-primary:active {
  opacity: 0.8;
}

.text-muted {
  color: #999;
  font-size: 26rpx;
}
</style>
