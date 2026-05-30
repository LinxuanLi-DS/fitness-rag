<template>
  <view class="user-profile-page">
    <view class="user-header">
      <image :src="user.avatar || '/static/default-avatar.png'" class="user-avatar" mode="aspectFill" />
      <text class="user-name">{{ userName }}</text>
      <text class="user-bio">这个用户很懒，还没写简介</text>
      <view class="follow-btn" @tap="followUser">
        <text class="follow-text">{{ followed ? '已关注' : '+ 关注' }}</text>
      </view>
    </view>

    <!-- 统计 -->
    <view class="stats-row">
      <view class="stat-item" @tap="showList('posts')">
        <text class="stat-num">{{ postCount }}</text>
        <text class="stat-label">帖子</text>
      </view>
      <view class="stat-item" @tap="showList('followers')">
        <text class="stat-num">{{ followerCount }}</text>
        <text class="stat-label">粉丝</text>
      </view>
      <view class="stat-item" @tap="showList('following')">
        <text class="stat-num">{{ followingCount }}</text>
        <text class="stat-label">关注</text>
      </view>
    </view>

    <!-- 帖子列表 -->
    <view class="section-header">
      <text class="section-title">TA的动态</text>
    </view>

    <view class="post-list">
      <view v-if="posts.length === 0" class="empty">
        <text class="empty-text">TA还没有发过帖子</text>
      </view>
      <view v-for="post in posts" :key="post.id" class="post-item" @tap="goDetail(post)">
        <text class="post-title">{{ post.title }}</text>
        <view class="post-meta">
          <text class="post-tag" v-if="post.tag">{{ post.tag }}</text>
          <text class="post-time">{{ post.time }}</text>
          <text class="post-likes">♡ {{ post.likes }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";

const userName = ref("");
const user = ref<any>({});
const followed = ref(false);
const postCount = ref(0);
const followerCount = ref(0);
const followingCount = ref(0);
const posts = ref<any[]>([]);

onLoad(() => {
  const name = uni.getStorageSync("view_user") || "";
  userName.value = name;

  // 从论坛帖子里找这个用户的帖子
  const allPosts = uni.getStorageSync("forum_posts");
  if (allPosts) {
    try {
      const arr = JSON.parse(allPosts);
      posts.value = arr.filter((p: any) => p.author === name);
      postCount.value = posts.value.length;
    } catch {}
  }

  // 模拟数据
  followerCount.value = Math.floor(Math.random() * 200) + 10;
  followingCount.value = Math.floor(Math.random() * 50) + 5;
});

function followUser() {
  followed.value = !followed.value;
  if (followed.value) {
    followerCount.value++;
    uni.showToast({ title: "已关注", icon: "success" });
  } else {
    followerCount.value--;
    uni.showToast({ title: "已取消关注", icon: "none" });
  }
}

function goDetail(post: any) {
  uni.setStorageSync("current_post", JSON.stringify(post));
  uni.navigateTo({ url: "/pages/post/detail" });
}

function showList(type: string) {
  const labels: Record<string, string> = { posts: "帖子", followers: "粉丝", following: "关注" };
  // 模拟用户列表
  const mockUsers = [
    { name: "小甜甜", bio: "热爱生活的女孩" },
    { name: "健身少女Amy", bio: "每天都在变强" },
    { name: "月亮姐姐", bio: "温柔且坚强" },
  ];
  const names = mockUsers.map((u) => u.name).join("、");
  uni.showModal({
    title: `${labels[type]}列表`,
    content: names || "暂无数据",
    showCancel: false,
  });
}
</script>

<style scoped>
.user-profile-page {
  min-height: 100vh;
  background: #fff5f5;
}

.user-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 32rpx 40rpx;
  background: linear-gradient(135deg, #e8837c, #d4625a);
}

.user-avatar {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  border: 6rpx solid rgba(255,255,255,0.6);
  margin-bottom: 16rpx;
}

.user-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.user-bio {
  font-size: 24rpx;
  color: rgba(255,255,255,0.7);
  margin-bottom: 24rpx;
}

.follow-btn {
  background: rgba(255,255,255,0.2);
  border: 2rpx solid rgba(255,255,255,0.5);
  padding: 12rpx 48rpx;
  border-radius: 28rpx;
}

.follow-text {
  color: #fff;
  font-size: 28rpx;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  background: #fff;
  margin: -20rpx 24rpx 24rpx;
  padding: 28rpx;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(232,131,124,0.08);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
}

.stat-num {
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 24rpx;
  color: #999;
}

.section-header {
  padding: 16rpx 28rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.post-list {
  padding: 0 24rpx;
}

.empty {
  text-align: center;
  padding: 80rpx 0;
}

.empty-text {
  color: #ccc;
  font-size: 26rpx;
}

.post-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 12rpx;
}

.post-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.post-tag {
  font-size: 22rpx;
  color: #e8837c;
  background: #fff0ef;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}

.post-time {
  font-size: 22rpx;
  color: #ccc;
}

.post-likes {
  font-size: 22rpx;
  color: #ccc;
  margin-left: auto;
}
</style>
