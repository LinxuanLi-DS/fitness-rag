<template>
  <view class="create-page">
    <!-- 标题 -->
    <input
      v-model="title"
      class="title-input"
      placeholder="起个标题..."
      :maxlength="50"
    />

    <!-- 内容 -->
    <textarea
      v-model="content"
      class="content-input"
      placeholder="分享你的故事、心得、问题..."
      :maxlength="2000"
      :auto-height="false"
    />

    <!-- 图片预览 -->
    <view class="image-list" v-if="images.length > 0">
      <view class="image-item" v-for="(img, i) in images" :key="i">
        <image :src="img" class="preview-img" mode="aspectFill" />
        <view class="remove-btn" @tap="removeImage(i)">
          <text class="remove-icon">×</text>
        </view>
      </view>
    </view>

    <!-- 标签选择 -->
    <view class="tag-section">
      <text class="tag-label">选择话题</text>
      <view class="tag-list">
        <view
          v-for="t in tags"
          :key="t"
          class="tag-item"
          :class="{ active: selectedTag === t }"
          @tap="selectedTag = selectedTag === t ? '' : t"
        >{{ t }}</view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="action-group">
        <view class="tool-btn" @tap="chooseImage">
          <text class="tool-icon">🖼</text>
          <text class="tool-text">图片</text>
        </view>
      </view>
      <button class="publish-btn" :class="{ active: canPublish }" @tap="publish" :disabled="!canPublish">
        发布
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

const title = ref("");
const content = ref("");
const images = ref<string[]>([]);
const selectedTag = ref("");

const tags = ["经期", "健身", "饮食", "护肤", "心情", "好物推荐", "求助"];

const canPublish = computed(() => title.value.trim().length > 0 && content.value.trim().length > 0);

function chooseImage() {
  uni.chooseImage({
    count: 9 - images.value.length,
    sizeType: ["compressed"],
    success: (res) => {
      images.value = [...images.value, ...res.tempFilePaths];
    },
  });
}

function removeImage(index: number) {
  images.value.splice(index, 1);
}

async function publish() {
  if (!canPublish.value) return;

  uni.showLoading({ title: "发布中..." });

  // TODO: 上传图片到服务器
  // TODO: 调API发帖
  try {
    // 模拟发帖
    await new Promise((resolve) => setTimeout(resolve, 1000));
    uni.hideLoading();
    uni.showToast({ title: "发布成功", icon: "success" });
    setTimeout(() => uni.navigateBack(), 1500);
  } catch {
    uni.hideLoading();
    uni.showToast({ title: "发布失败", icon: "none" });
  }
}
</script>

<style scoped>
.create-page {
  min-height: 100vh;
  background: #fff;
  padding-bottom: 140rpx;
}

.title-input {
  padding: 32rpx 32rpx 16rpx;
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
  border-bottom: 1rpx solid #f5f0f0;
}

.content-input {
  padding: 24rpx 32rpx;
  font-size: 28rpx;
  color: #444;
  line-height: 1.8;
  min-height: 400rpx;
  width: 100%;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  padding: 16rpx 24rpx;
  gap: 16rpx;
}

.image-item {
  position: relative;
  width: 200rpx;
  height: 200rpx;
}

.preview-img {
  width: 100%;
  height: 100%;
  border-radius: 12rpx;
}

.remove-btn {
  position: absolute;
  top: -12rpx;
  right: -12rpx;
  width: 40rpx;
  height: 40rpx;
  background: #e8837c;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-icon {
  color: #fff;
  font-size: 28rpx;
  line-height: 1;
}

.tag-section {
  padding: 24rpx 32rpx;
}

.tag-label {
  font-size: 26rpx;
  color: #999;
  display: block;
  margin-bottom: 16rpx;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.tag-item {
  padding: 12rpx 28rpx;
  border-radius: 24rpx;
  font-size: 26rpx;
  background: #f8f0f0;
  color: #999;
}

.tag-item.active {
  background: #fff0ef;
  color: #e8837c;
  font-weight: 500;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #f0e8e8;
}

.action-group {
  display: flex;
  gap: 24rpx;
}

.tool-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.tool-icon {
  font-size: 36rpx;
}

.tool-text {
  font-size: 20rpx;
  color: #999;
}

.publish-btn {
  background: #e0c8c6;
  color: #fff;
  border: none;
  border-radius: 32rpx;
  padding: 18rpx 48rpx;
  font-size: 30rpx;
  font-weight: 500;
}

.publish-btn.active {
  background: linear-gradient(135deg, #e8837c, #d4625a);
}
</style>
