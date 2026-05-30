<template>
  <view class="forum-page">
    <!-- 顶部 -->
    <view class="header">
      <view class="header-left">
        <text class="header-title">FitHer</text>
        <text class="header-sub">分享你的健康生活</text>
      </view>
      <view class="header-right">
        <image :src="myAvatar || '/static/default-avatar.png'" class="header-avatar" mode="aspectFill" />
      </view>
    </view>

    <!-- 分类标签 -->
    <scroll-view class="tabs-scroll" scroll-x>
      <view class="tabs-row">
        <view
          v-for="t in tabs"
          :key="t.id"
          class="tab-item"
          :class="{ active: currentTab === t.id }"
          @tap="switchTab(t.id)"
        >{{ t.name }}</view>
      </view>
    </scroll-view>

    <!-- 帖子列表 -->
    <scroll-view class="post-list" scroll-y @scrolltolower="loadMore">
      <view v-if="filteredPosts.length === 0 && !loading" class="empty">
        <text class="empty-text">这个分类还没有帖子</text>
        <text class="empty-sub">来发第一个吧</text>
      </view>

      <view
        v-for="post in filteredPosts"
        :key="post.id"
        class="post-card"
        @tap="goDetail(post)"
      >
        <view class="post-header">
          <image :src="post.avatar || '/static/default-avatar.png'" class="post-avatar" mode="aspectFill" @tap.stop="goUserProfile(post.author)" />
          <view class="post-meta" @tap.stop="goUserProfile(post.author)">
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
        <view class="post-footer">
          <view class="post-action" @tap.stop="toggleLike(post)">
            <text class="action-icon">{{ post.liked ? '❤️' : '♡' }}</text>
            <text class="action-num">{{ post.likes || 0 }}</text>
          </view>
          <view class="post-action">
            <text class="action-icon">💬</text>
            <text class="action-num">{{ post.comments || 0 }}</text>
          </view>
          <view class="post-action">
            <text class="action-icon">⭐</text>
          </view>
        </view>
      </view>

      <view v-if="loading" class="loading">
        <text class="loading-text">加载中...</text>
      </view>
    </scroll-view>

    <!-- 发帖按钮 -->
    <view class="fab" @tap="goCreate">
      <text class="fab-icon">+</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onShow } from "@dcloudio/uni-app";

const tabs = [
  { id: "all", name: "推荐" },
  { id: "经期", name: "经期" },
  { id: "健身", name: "健身" },
  { id: "饮食", name: "饮食" },
  { id: "护肤", name: "护肤" },
  { id: "心情", name: "心情" },
];

const currentTab = ref("all");
const loading = ref(false);
const myAvatar = ref("");

// 存储帖子到localStorage（模拟后端）
const STORAGE_KEY = "forum_posts";

function getPosts(): any[] {
  const saved = uni.getStorageSync(STORAGE_KEY);
  if (saved) {
    try { return JSON.parse(saved); } catch {}
  }
  // 默认帖子
  return [
    {
      id: 1,
      author: "小甜甜",
      avatar: "",
      time: "2小时前",
      tag: "经期",
      title: "经期第3天，终于不疼了",
      content: "前两天痛得死去活来，今天终于活过来了。分享一下我的缓解方法：热水袋+红糖姜茶+布洛芬。姐妹们你们经期都怎么过的？",
      image: "",
      likes: 28,
      comments: 12,
      liked: false,
    },
    {
      id: 2,
      author: "健身少女Amy",
      avatar: "",
      time: "5小时前",
      tag: "健身",
      title: "卵泡期练臀真的太爽了",
      content: "卵泡期精力旺盛，今天臀推做了4组x12个，感觉比黄体期有力多了。姐妹们一定要抓住这个黄金期练起来！",
      image: "",
      likes: 45,
      comments: 8,
      liked: false,
    },
    {
      id: 3,
      author: "吃货小圆",
      avatar: "",
      time: "昨天",
      tag: "饮食",
      title: "分享我的减脂午餐",
      content: "糙米饭+鸡胸肉+西兰花+牛油果，热量大概450kcal，饱腹感超强。减脂期不用饿肚子，关键是吃对东西。",
      image: "",
      likes: 67,
      comments: 23,
      liked: false,
    },
    {
      id: 4,
      author: "月亮姐姐",
      avatar: "",
      time: "昨天",
      tag: "心情",
      title: "黄体期emo了怎么办",
      content: "每次黄体期都控制不住情绪，一点小事就哭。后来看了科普才知道是激素在作怪。现在学会了接纳自己，emo就emo吧，过几天就好了。",
      image: "",
      likes: 89,
      comments: 34,
      liked: false,
    },
    {
      id: 5,
      author: "护肤达人Luna",
      avatar: "",
      time: "2天前",
      tag: "护肤",
      title: "经期长痘的急救方法",
      content: "经前必长痘星人来分享了：1.水杨酸棉片敷5分钟 2.不要挤！ 3.清淡饮食少糖 4.早睡。坚持一周痘痘就消了。",
      image: "",
      likes: 112,
      comments: 41,
      liked: false,
    },
  ];
}

const posts = ref<any[]>(getPosts());

const filteredPosts = computed(() => {
  if (currentTab.value === "all") return posts.value;
  return posts.value.filter((p) => p.tag === currentTab.value);
});

onShow(() => {
  myAvatar.value = uni.getStorageSync("avatar") || "";
  // 检查有没有新帖子
  const latest = getPosts();
  if (latest.length !== posts.value.length) {
    posts.value = latest;
  }
});

function switchTab(id: string) {
  currentTab.value = id;
}

function goDetail(post: any) {
  // 存帖子到临时storage
  uni.setStorageSync("current_post", JSON.stringify(post));
  uni.navigateTo({ url: "/pages/post/detail" });
}

function goUserProfile(author: string) {
  uni.setStorageSync("view_user", author);
  uni.navigateTo({ url: "/pages/profile/user-profile" });
}

function goCreate() {
  uni.navigateTo({ url: "/pages/post/create" });
}

function toggleLike(post: any) {
  post.liked = !post.liked;
  post.likes += post.liked ? 1 : -1;
  uni.setStorageSync(STORAGE_KEY, JSON.stringify(posts.value));
}

function loadMore() {
  // TODO: 分页
}
</script>

<style scoped>
.forum-page {
  min-height: 100vh;
  background: #fff5f5;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 88rpx 32rpx 20rpx;
  background: linear-gradient(135deg, #e8837c, #d4625a);
}

.header-left {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 42rpx;
  font-weight: 700;
  color: #fff;
}

.header-sub {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 4rpx;
}

.header-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  border: 3rpx solid rgba(255, 255, 255, 0.5);
}

.tabs-scroll {
  white-space: nowrap;
  background: #fff;
  border-bottom: 1rpx solid #f0e8e8;
}

.tabs-row {
  display: flex;
  padding: 0 20rpx;
}

.tab-item {
  padding: 20rpx 28rpx;
  font-size: 28rpx;
  color: #999;
  white-space: nowrap;
  position: relative;
}

.tab-item.active {
  color: #e8837c;
  font-weight: 600;
}

.tab-item.active::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40rpx;
  height: 6rpx;
  background: #e8837c;
  border-radius: 3rpx;
}

.post-list {
  flex: 1;
  padding: 20rpx 24rpx;
  padding-bottom: 160rpx;
}

.post-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(232, 131, 124, 0.05);
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.post-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  margin-right: 16rpx;
}

.post-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.post-author {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
}

.post-time {
  font-size: 22rpx;
  color: #bbb;
  margin-top: 4rpx;
}

.post-tag {
  background: #fff0ef;
  color: #e8837c;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 16rpx;
}

.post-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 12rpx;
  display: block;
}

.post-content {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 16rpx;
}

.post-image {
  width: 100%;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
}

.post-footer {
  display: flex;
  gap: 40rpx;
}

.post-action {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.action-icon {
  font-size: 28rpx;
}

.action-num {
  font-size: 24rpx;
  color: #999;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
}

.empty-text {
  color: #bbb;
  font-size: 28rpx;
  margin-bottom: 8rpx;
}

.empty-sub {
  color: #ddd;
  font-size: 24rpx;
}

.loading {
  text-align: center;
  padding: 40rpx;
}

.loading-text {
  color: #ccc;
  font-size: 24rpx;
}

.fab {
  position: fixed;
  right: 40rpx;
  bottom: 180rpx;
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #e8837c, #d4625a);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(232, 131, 124, 0.4);
}

.fab:active {
  transform: scale(0.9);
}

.fab-icon {
  color: #fff;
  font-size: 52rpx;
  font-weight: 300;
  line-height: 1;
}
</style>
