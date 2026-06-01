<template>
  <view class="user-profile-page">
    <view class="user-header">
      <!-- 背景图 -->
      <view class="header-bg" @tap="isMe && changeBg()">
        <image v-if="headerBg" :src="headerBg" class="bg-img" mode="aspectFill" />
        <view v-else class="bg-default"></view>
        <view v-if="isMe" class="bg-edit-hint">
          <text>换背景</text>
        </view>
      </view>

      <image :src="user.avatar || '/static/default-avatar.png'" class="user-avatar" mode="aspectFill" />
      <text class="user-name">{{ userName }}</text>

      <!-- 简介 (自己的可以编辑) -->
      <view class="bio-row" @tap="isMe && editBio()">
        <text class="user-bio">{{ bio || (isMe ? '点击编辑个人简介...' : '这个用户很懒，还没写简介') }}</text>
        <text v-if="isMe" class="bio-edit-icon">✏️</text>
      </view>

      <view class="follow-btn" v-if="!isMe" @tap="followUser">
        <text class="follow-text">{{ followed ? '已关注' : '+ 关注' }}</text>
      </view>
      <view class="follow-btn" v-if="isMe" @tap="editProfile">
        <text class="follow-text">编辑资料</text>
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
        <text class="empty-text">{{ isMe ? '你还没有发过帖子' : 'TA还没有发过帖子' }}</text>
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
const bio = ref("");
const headerBg = ref("");
const isMe = ref(false);

onLoad(() => {
  const name = uni.getStorageSync("view_user") || "";
  const currentUser = uni.getStorageSync("username") || "";
  userName.value = name;
  isMe.value = name === currentUser;

  // 加载头像和简介
  user.value.avatar = uni.getStorageSync("avatar") || "";
  bio.value = uni.getStorageSync("user_bio") || "";
  headerBg.value = uni.getStorageSync("user_header_bg") || "";

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

function editProfile() {
  uni.switchTab({ url: "/pages/profile/profile" });
}

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
  padding: 0;
  padding-bottom: 40rpx;
  position: relative;
  overflow: hidden;
}

.header-bg {
  width: 100%;
  height: 300rpx;
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

.bg-edit-hint {
  position: absolute;
  bottom: 12rpx;
  right: 20rpx;
  background: rgba(0,0,0,0.4);
  padding: 6rpx 16rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
  color: #fff;
}

.user-avatar {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  border: 6rpx solid rgba(255,255,255,0.6);
  margin-top: -70rpx;
  margin-bottom: 16rpx;
  position: relative;
  z-index: 2;
}

.user-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
}

.bio-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 24rpx;
  padding: 0 40rpx;
}

.user-bio {
  font-size: 24rpx;
  color: #999;
  text-align: center;
}

.bio-edit-icon {
  font-size: 20rpx;
}

.follow-btn {
  background: rgba(232,131,124,0.1);
  border: 2rpx solid var(--primary);
  padding: 12rpx 48rpx;
  border-radius: 28rpx;
}

.follow-text {
  color: var(--primary);
  font-size: 28rpx;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  background: #fff;
  margin: 0 24rpx 24rpx;
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
  color: var(--primary);
  background: var(--primary-light);
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
