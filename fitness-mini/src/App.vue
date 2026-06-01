<script setup lang="ts">
import { onLaunch, onShow } from "@dcloudio/uni-app";

const themes = {
  pink: { primary: "#e8837c", primaryDark: "#d4625a", bg: "#fff5f5" },
  purple: { primary: "#a855f7", primaryDark: "#9333ea", bg: "#faf5ff" },
  blue: { primary: "#3b82f6", primaryDark: "#2563eb", bg: "#eff6ff" },
  green: { primary: "#10b981", primaryDark: "#059669", bg: "#ecfdf5" },
  orange: { primary: "#f59e0b", primaryDark: "#d97706", bg: "#fffbeb" },
};

const fontSizes = {
  小: { base: 24, small: 22, large: 28 },
  中: { base: 28, small: 24, large: 32 },
  大: { base: 32, small: 28, large: 36 },
};

function applyTheme() {
  const saved = uni.getStorageSync("settings_theme") || "pink";
  const fontIndex = uni.getStorageSync("settings_fontIndex");
  const fontName = ["小", "中", "大"][fontIndex || 1];
  
  const theme = themes[saved as keyof typeof themes] || themes.pink;
  const font = fontSizes[fontName as keyof typeof fontSizes] || fontSizes.中;
  
  const root = document.documentElement;
  root.style.setProperty("--primary", theme.primary);
  root.style.setProperty("--primary-dark", theme.primaryDark);
  root.style.setProperty("--bg", theme.bg);
  root.style.setProperty("--font-base", `${font.base}rpx`);
  root.style.setProperty("--font-small", `${font.small}rpx`);
  root.style.setProperty("--font-large", `${font.large}rpx`);
}

onLaunch(() => {
  console.log("App Launch");
  applyTheme();
  
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.redirectTo({ url: "/pages/login/login" });
  }
});

onShow(() => {
  applyTheme();
});
</script>

<style>
:root {
  --primary: #e8837c;
  --primary-dark: #d4625a;
  --bg: #fff5f5;
  --font-base: 28rpx;
  --font-small: 24rpx;
  --font-large: 32rpx;
}

page {
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

/* 通用主题色类 */
.theme-text {
  color: var(--primary);
}

.theme-bg {
  background: var(--primary);
}

.theme-gradient {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
}

.theme-border {
  border-color: var(--primary);
}

/* 字体大小类 */
.text-small {
  font-size: var(--font-small);
}

.text-base {
  font-size: var(--font-base);
}

.text-large {
  font-size: var(--font-large);
}
</style>
