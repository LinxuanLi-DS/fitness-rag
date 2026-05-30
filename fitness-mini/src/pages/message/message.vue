<template>
  <view class="message-page">
    <view class="header">
      <text class="header-title">消息</text>
    </view>

    <!-- Tab -->
    <view class="msg-tabs">
      <view v-for="t in msgTabs" :key="t.id" class="msg-tab" :class="{ active: currentMsgTab === t.id }" @tap="currentMsgTab = t.id">
        <text>{{ t.name }}</text>
        <view class="tab-badge" v-if="t.count > 0">{{ t.count }}</view>
      </view>
    </view>

    <!-- 互动消息 -->
    <view v-if="currentMsgTab === 'interact'" class="msg-list">
      <view v-if="interactions.length === 0" class="empty-msg">
        <text class="empty-icon">🔔</text>
        <text class="empty-text">暂无互动消息</text>
      </view>
      <view v-for="item in interactions" :key="item.id" class="msg-item">
        <image :src="item.avatar || '/static/default-avatar.png'" class="msg-avatar" mode="aspectFill" />
        <view class="msg-body">
          <text class="msg-main"><text class="msg-user">{{ item.user }}</text> {{ item.action }}</text>
          <text class="msg-context">{{ item.context }}</text>
          <text class="msg-time">{{ item.time }}</text>
        </view>
        <text class="msg-type-icon">{{ item.typeIcon }}</text>
      </view>
    </view>

    <!-- AI助手 - 平级设计 -->
    <view v-if="currentMsgTab === 'ai'" class="ai-section">
      <text class="ai-section-title">选择你的AI助手</text>
      <view v-for="a in aiAssistants" :key="a.id" class="ai-card-full" @tap="goAI(a.id)">
        <view class="ai-card-left">
          <view class="ai-big-avatar" :class="a.theme">{{ a.emoji }}</view>
          <view class="ai-card-info">
            <text class="ai-card-name">{{ a.name }}</text>
            <text class="ai-card-role">{{ a.role }}</text>
            <text class="ai-card-desc">{{ a.desc }}</text>
          </view>
        </view>
        <view class="ai-card-right">
          <view class="ai-online-dot"></view>
          <text class="ai-online-text">在线</text>
        </view>
      </view>
    </view>

    <!-- 好友 -->
    <view v-if="currentMsgTab === 'chat'" class="msg-list">
      <view class="add-friend-bar" @tap="addFriend">
        <text class="add-icon">+ 添加好友</text>
      </view>
      <view v-if="chats.length === 0" class="empty-msg">
        <text class="empty-icon">💬</text>
        <text class="empty-text">还没有好友消息</text>
        <text class="empty-sub">添加好友开始聊天吧</text>
      </view>
      <view v-for="chat in chats" :key="chat.id" class="msg-item">
        <image :src="chat.avatar || '/static/default-avatar.png'" class="msg-avatar" mode="aspectFill" />
        <view class="msg-body">
          <view class="msg-top-row">
            <text class="msg-name">{{ chat.name }}</text>
            <text class="msg-time">{{ chat.time }}</text>
          </view>
          <text class="msg-last">{{ chat.lastMsg }}</text>
        </view>
        <view class="unread-badge" v-if="chat.unread">
          <text class="unread-num">{{ chat.unread }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";

const msgTabs = ref([
  { id: "interact", name: "互动消息", count: 3 },
  { id: "ai", name: "AI助手", count: 0 },
  { id: "chat", name: "好友", count: 0 },
]);
const currentMsgTab = ref("interact");

const aiAssistants = [
  { id: "shiqing", name: "十七", role: "健康管家", emoji: "💗", theme: "pink", desc: "温柔陪伴，关注你的经期和身体健康" },
  { id: "xiaojian", name: "小健", role: "健身教练", emoji: "💪", theme: "blue", desc: "为你定制训练计划，陪你一起变强" },
  { id: "xiaokang", name: "小康", role: "营养师", emoji: "🥗", theme: "green", desc: "科学饮食建议，吃得健康又美味" },
];

const interactions = ref([
  { id: 1, user: "小甜甜", avatar: "", action: "赞了你的帖子", context: "「卵泡期练臀真的太爽了」", time: "10分钟前", typeIcon: "❤️" },
  { id: 2, user: "健身少女Amy", avatar: "", action: "评论了你的帖子", context: "太有用了！已收藏", time: "1小时前", typeIcon: "💬" },
  { id: 3, user: "月亮姐姐", avatar: "", action: "关注了你", context: "", time: "3小时前", typeIcon: "👤" },
]);

const chats = ref<any[]>([]);

function goAI(id: string) {
  uni.navigateTo({ url: `/pages/chat/chat?assistant=${id}` });
}

function addFriend() {
  uni.showModal({
    title: "添加好友",
    editable: true,
    placeholderText: "输入对方用户名",
    success: (res) => {
      if (res.confirm && res.content) {
        uni.showToast({ title: "已发送好友请求", icon: "success" });
      }
    },
  });
}
</script>

<style scoped>
.message-page { min-height: 100vh; background: #fff5f5; }
.header { padding: 88rpx 32rpx 24rpx; background: linear-gradient(135deg, #e8837c, #d4625a); }
.header-title { font-size: 38rpx; font-weight: 600; color: #fff; }
.msg-tabs { display: flex; background: #fff; border-bottom: 1rpx solid #f0e8e8; }
.msg-tab { flex: 1; text-align: center; padding: 22rpx 0; font-size: 28rpx; color: #999; position: relative; }
.msg-tab.active { color: #e8837c; font-weight: 600; }
.msg-tab.active::after { content: ""; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 48rpx; height: 6rpx; background: #e8837c; border-radius: 3rpx; }
.tab-badge { position: absolute; top: 8rpx; right: 20%; background: #e8837c; color: #fff; font-size: 18rpx; min-width: 28rpx; height: 28rpx; line-height: 28rpx; border-radius: 14rpx; padding: 0 8rpx; text-align: center; }
.msg-list { padding: 16rpx 0; }
.empty-msg { display: flex; flex-direction: column; align-items: center; padding: 100rpx 0; }
.empty-icon { font-size: 64rpx; margin-bottom: 16rpx; }
.empty-text { font-size: 28rpx; color: #999; margin-bottom: 8rpx; }
.empty-sub { font-size: 24rpx; color: #ccc; }
.msg-item { display: flex; align-items: center; padding: 24rpx 28rpx; background: #fff; border-bottom: 1rpx solid #f8f0f0; }
.msg-avatar { width: 80rpx; height: 80rpx; border-radius: 50%; margin-right: 20rpx; flex-shrink: 0; }
.msg-body { flex: 1; display: flex; flex-direction: column; }
.msg-top-row { display: flex; justify-content: space-between; align-items: center; }
.msg-main { font-size: 28rpx; color: #333; margin-bottom: 6rpx; }
.msg-user { font-weight: 600; color: #e8837c; }
.msg-name { font-size: 28rpx; font-weight: 500; color: #333; }
.msg-context { font-size: 24rpx; color: #999; margin-bottom: 4rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.msg-last { font-size: 24rpx; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.msg-time { font-size: 22rpx; color: #ccc; }
.msg-type-icon { font-size: 28rpx; margin-left: 12rpx; }
.unread-badge { background: #e8837c; border-radius: 20rpx; padding: 4rpx 12rpx; margin-left: 12rpx; }
.unread-num { color: #fff; font-size: 22rpx; font-weight: 500; }
.add-friend-bar { padding: 24rpx 28rpx; background: #fff; border-bottom: 1rpx solid #f8f0f0; }
.add-icon { color: #e8837c; font-size: 28rpx; font-weight: 500; }

/* AI section - equal level design */
.ai-section { padding: 24rpx; }
.ai-section-title { font-size: 26rpx; color: #999; margin-bottom: 16rpx; display: block; }
.ai-card-full { background: #fff; border-radius: 24rpx; padding: 28rpx; margin-bottom: 16rpx; box-shadow: 0 4rpx 20rpx rgba(232,131,124,0.08); display: flex; justify-content: space-between; align-items: center; }
.ai-card-left { display: flex; align-items: center; gap: 20rpx; flex: 1; }
.ai-big-avatar { width: 96rpx; height: 96rpx; border-radius: 28rpx; display: flex; align-items: center; justify-content: center; font-size: 44rpx; }
.ai-big-avatar.pink { background: #fce4ec; }
.ai-big-avatar.blue { background: #e3f2fd; }
.ai-big-avatar.green { background: #e8f5e9; }
.ai-card-info { flex: 1; }
.ai-card-name { font-size: 32rpx; font-weight: 600; color: #333; display: block; }
.ai-card-role { font-size: 22rpx; color: #e8837c; display: block; margin: 4rpx 0; }
.ai-card-desc { font-size: 24rpx; color: #999; display: block; }
.ai-card-right { display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.ai-online-dot { width: 16rpx; height: 16rpx; border-radius: 50%; background: #4caf50; }
.ai-online-text { font-size: 20rpx; color: #4caf50; }
</style>
