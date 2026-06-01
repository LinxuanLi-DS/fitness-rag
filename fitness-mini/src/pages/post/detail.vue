<template>
  <view class="detail-page">
    <!-- 帖子内容 -->
    <view class="post-card" v-if="post.id">
      <view class="post-header">
        <image :src="post.avatar || '/static/default-avatar.png'" class="post-avatar" mode="aspectFill" @tap="goUserProfile" />
        <view class="post-meta" @tap="goUserProfile">
          <text class="post-author">{{ post.author }}</text>
          <text class="post-time">{{ post.time }}</text>
        </view>
        <view class="post-tag" v-if="post.tag">{{ post.tag }}</view>
      </view>
      <text class="post-title">{{ post.title }}</text>
      <text class="post-content">{{ post.content }}</text>
      <image
        v-if="post.image"
        :src="post.image"
        class="post-image"
        mode="widthFix"
      />
      <view class="post-stats">
        <text class="stat-text">{{ post.likes || 0 }} 赞 · {{ post.comments || 0 }} 评论</text>
      </view>
    </view>

    <!-- 评论区 -->
    <view class="comment-section">
      <text class="section-title">评论 ({{ comments.length }})</text>

      <view v-if="comments.length === 0" class="empty-comments">
        <text class="empty-text">还没有评论，来说两句吧</text>
      </view>

      <view v-for="c in comments" :key="c.id" class="comment-item">
        <image :src="c.avatar || '/static/default-avatar.png'" class="comment-avatar" mode="aspectFill" />
        <view class="comment-body">
          <text class="comment-author">{{ c.author }}</text>
          <text class="comment-content">{{ c.content }}</text>
          <text class="comment-time">{{ c.time }}</text>
        </view>
        <view class="comment-like" @tap="c.liked = !c.liked">
          <text>{{ c.liked ? '❤️' : '♡' }}</text>
        </view>
      </view>
    </view>

    <!-- 底部评论输入 -->
    <view class="comment-bar">
      <view class="like-btn" @tap="toggleLike">
        <text class="like-icon">{{ liked ? '❤️' : '♡' }}</text>
      </view>
      <input
        v-model="commentText"
        class="comment-input"
        placeholder="说点什么..."
        confirm-type="send"
        @confirm="sendComment"
      />
      <view class="send-btn" @tap="sendComment">
        <text class="send-text">发送</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";

const post = ref<any>({});
const comments = ref<any[]>([]);
const commentText = ref("");
const liked = ref(false);

onLoad(() => {
  const saved = uni.getStorageSync("current_post");
  if (saved) {
    try {
      post.value = JSON.parse(saved);
      liked.value = post.value.liked || false;
    } catch {}
  }
  loadComments();
});

function loadComments() {
  const key = `comments_${post.value.id}`;
  const saved = uni.getStorageSync(key);
  if (saved) {
    try { comments.value = JSON.parse(saved); return; } catch {}
  }
  // 默认评论
  comments.value = [
    { id: 1, author: "小美", avatar: "", content: "太有用了！收藏了", time: "1小时前", liked: false },
    { id: 2, author: "Lily", avatar: "", content: "同感，我也是这样的", time: "3小时前", liked: false },
    { id: 3, author: "元气少女", avatar: "", content: "坚持就是胜利！加油", time: "昨天", liked: false },
  ];
}

function toggleLike() {
  liked.value = !liked.value;
  post.value.likes += liked.value ? 1 : -1;
  post.value.liked = liked.value;
  uni.setStorageSync("current_post", JSON.stringify(post.value));
  // 更新帖子列表
  const posts = uni.getStorageSync("forum_posts");
  if (posts) {
    try {
      const arr = JSON.parse(posts);
      const idx = arr.findIndex((p: any) => p.id === post.value.id);
      if (idx >= 0) {
        arr[idx] = post.value;
        uni.setStorageSync("forum_posts", JSON.stringify(arr));
      }
    } catch {}
  }
}

function sendComment() {
  if (!commentText.value.trim()) return;
  const c = {
    id: Date.now(),
    author: uni.getStorageSync("username") || "我",
    avatar: uni.getStorageSync("avatar") || "",
    content: commentText.value,
    time: "刚刚",
    liked: false,
  };
  comments.value.push(c);
  commentText.value = "";
  post.value.comments = comments.value.length;
  uni.setStorageSync(`comments_${post.value.id}`, JSON.stringify(comments.value));
}

function goUserProfile() {
  uni.setStorageSync("view_user", post.value.author);
  uni.navigateTo({ url: "/pages/profile/user-profile" });
}
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #fff5f5;
  padding-bottom: 120rpx;
}

.post-card {
  background: #fff;
  padding: 32rpx;
  margin-bottom: 16rpx;
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.post-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  margin-right: 16rpx;
}

.post-meta {
  flex: 1;
}

.post-author {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
  display: block;
}

.post-time {
  font-size: 24rpx;
  color: #bbb;
}

.post-tag {
  background: var(--primary-light);
  color: var(--primary);
  font-size: 24rpx;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
}

.post-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}

.post-content {
  font-size: 28rpx;
  color: #555;
  line-height: 1.8;
  display: block;
  margin-bottom: 20rpx;
}

.post-image {
  width: 100%;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
}

.post-stats {
  padding-top: 16rpx;
  border-top: 1rpx solid #f5f0f0;
}

.stat-text {
  font-size: 24rpx;
  color: #bbb;
}

.comment-section {
  background: #fff;
  padding: 28rpx 32rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.empty-comments {
  text-align: center;
  padding: 60rpx 0;
}

.empty-text {
  font-size: 26rpx;
  color: #ccc;
}

.comment-item {
  display: flex;
  align-items: flex-start;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f8f0f0;
}

.comment-avatar {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.comment-body {
  flex: 1;
}

.comment-author {
  font-size: 26rpx;
  font-weight: 500;
  color: #333;
  display: block;
  margin-bottom: 6rpx;
}

.comment-content {
  font-size: 26rpx;
  color: #555;
  line-height: 1.5;
  display: block;
  margin-bottom: 8rpx;
}

.comment-time {
  font-size: 22rpx;
  color: #ccc;
}

.comment-like {
  padding: 8rpx;
  font-size: 28rpx;
}

.comment-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #f0e8e8;
  gap: 16rpx;
  z-index: 100;
}

.like-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.like-icon {
  font-size: 36rpx;
}

.comment-input {
  flex: 1;
  background: #f8f0f0;
  border-radius: 32rpx;
  padding: 18rpx 24rpx;
  font-size: 28rpx;
}

.send-btn {
  padding: 14rpx 24rpx;
}

.send-text {
  color: var(--primary);
  font-size: 28rpx;
  font-weight: 500;
}
</style>
