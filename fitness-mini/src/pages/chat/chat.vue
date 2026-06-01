<template>
  <view class="chat-page">
    <!-- 顶部 -->
    <view class="nav-bar">
      <view class="back-btn" @tap="goBack">
        <text class="back-arrow">‹</text>
      </view>
      <text class="nav-title">{{ currentAssistantObj.name }}</text>
      <view class="nav-right"></view>
    </view>

    <!-- 聊天区域 -->
    <scroll-view
      class="message-list"
      scroll-y
      :scroll-into-view="scrollToId"
      :scroll-with-animation="true"
    >
      <view v-if="messages.length === 0" class="empty-chat">
        <view class="empty-emoji">{{ currentAssistantObj.emoji }}</view>
        <text class="empty-name">{{ currentAssistantName }}</text>
        <text class="empty-desc">{{ currentAssistantObj.desc }}</text>
        <view class="suggest-list">
          <view
            class="suggest-item"
            v-for="(s, i) in suggestions"
            :key="i"
            @tap="sendSuggestion(s)"
          >{{ s }}</view>
        </view>
      </view>

      <view
        v-for="(msg, i) in messages"
        :key="i"
        :id="'msg-' + i"
        class="message-row"
        :class="msg.role"
      >
        <view class="avatar-small" v-if="msg.role === 'assistant'">
          <text>{{ currentAssistantObj.emoji }}</text>
        </view>
        <view class="bubble" :class="msg.role">
          <text selectable user-select>{{ msg.content }}</text>
        </view>
      </view>

      <view v-if="streaming" class="message-row assistant">
        <view class="avatar-small"><text>{{ currentAssistantObj.emoji }}</text></view>
        <view class="bubble assistant">
          <text selectable user-select>{{ streamingText }}</text>
        </view>
      </view>

      <view id="msg-bottom" style="height: 20rpx;"></view>
    </scroll-view>

    <!-- 输入栏 -->
    <view class="input-bar">
      <input
        v-model="inputText"
        class="chat-input"
        placeholder="问我任何问题..."
        confirm-type="send"
        @confirm="send"
        :disabled="streaming"
      />
      <view
        class="send-btn"
        :class="{ active: inputText && !streaming }"
        @tap="send"
      >
        <text class="send-icon">↑</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { chatStream } from "@/utils/api";

const assistants = [
  { id: "xiaojian", name: "小健", emoji: "💪", desc: "你的私人健身教练，定制训练计划" },
  { id: "xiaokang", name: "小康", emoji: "🥗", desc: "你的营养师闺蜜，教你吃得健康" },
  { id: "shiqing", name: "十七", emoji: "💗", desc: "温柔的周期管家，陪你度过每一天" },
];

const suggestions = [
  "今天练什么好？",
  "帮我规划一周饮食",
  "经期可以吃什么？",
  "最近总是失眠怎么办",
];

const currentAssistant = ref("shiqing");
const messages = ref<{ role: string; content: string }[]>([]);
const inputText = ref("");
const streaming = ref(false);
const streamingText = ref("");
const scrollToId = ref("msg-bottom");

const currentAssistantName = computed(
  () => assistants.find((a) => a.id === currentAssistant.value)?.name || ""
);

const currentAssistantObj = computed(
  () => assistants.find((a) => a.id === currentAssistant.value) || assistants[2]
);

onLoad((query: any) => {
  if (query?.assistant) {
    currentAssistant.value = query.assistant;
  }
  loadHistory();
});

function goBack() {
  uni.navigateBack({ fail: () => uni.switchTab({ url: "/pages/message/message" }) });
}

function loadHistory() {
  const username = uni.getStorageSync("username");
  const key = `fitherHistories_${username}`;
  const saved = uni.getStorageSync(key);
  if (saved) {
    try {
      const all = JSON.parse(saved);
      messages.value = all[currentAssistant.value] || [];
      scrollToBottom();
    } catch {}
  }
}

function saveHistory() {
  const username = uni.getStorageSync("username");
  const key = `fitherHistories_${username}`;
  let all: Record<string, any[]> = {};
  try {
    all = JSON.parse(uni.getStorageSync(key) || "{}");
  } catch {}
  all[currentAssistant.value] = messages.value.slice(-20);
  uni.setStorageSync(key, JSON.stringify(all));
}

function sendSuggestion(text: string) {
  inputText.value = text;
  send();
}

async function send() {
  const text = inputText.value.trim();
  if (!text || streaming.value) return;

  inputText.value = "";
  messages.value.push({ role: "user", content: text });
  scrollToBottom();

  streaming.value = true;
  streamingText.value = "";

  const history = messages.value.slice(-10).map((m) => ({
    role: m.role,
    content: m.content,
  }));

  try {
    await chatStream(text, currentAssistant.value, history, (chunk) => {
      streamingText.value += chunk;
      scrollToBottom();
    });

    messages.value.push({ role: "assistant", content: streamingText.value });
    saveHistory();
  } catch (e) {
    messages.value.push({ role: "assistant", content: "抱歉，网络不太好，请重试" });
  }

  streaming.value = false;
  streamingText.value = "";
  scrollToBottom();
}

function scrollToBottom() {
  nextTick(() => {
    scrollToId.value = "";
    nextTick(() => {
      scrollToId.value = "msg-bottom";
    });
  });
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fff5f5;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 88rpx;
  padding-bottom: 16rpx;
  padding-left: 16rpx;
  padding-right: 16rpx;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-arrow {
  font-size: 52rpx;
  color: #fff;
  font-weight: 300;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 500;
  color: #fff;
}

.nav-right {
  width: 64rpx;
}

.message-list {
  flex: 1;
  padding: 24rpx;
  padding-bottom: 140rpx;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 60rpx;
}

.empty-emoji {
  font-size: 80rpx;
  margin-bottom: 16rpx;
}

.empty-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
}

.empty-desc {
  color: #999;
  font-size: 26rpx;
  margin-bottom: 40rpx;
  text-align: center;
}

.suggest-list {
  width: 100%;
  padding: 0 40rpx;
}

.suggest-item {
  background: #fff;
  border: 2rpx solid var(--primary-border);
  border-radius: 32rpx;
  padding: 22rpx 28rpx;
  margin-bottom: 16rpx;
  font-size: 26rpx;
  color: var(--primary);
  text-align: center;
}

.suggest-item:active {
  background: var(--primary-light);
}

.message-row {
  display: flex;
  margin-bottom: 24rpx;
  align-items: flex-start;
}

.message-row.user {
  justify-content: flex-end;
}

.avatar-small {
  width: 60rpx;
  height: 60rpx;
  border-radius: 16rpx;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  margin-right: 12rpx;
  flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.bubble {
  max-width: 72%;
  padding: 22rpx 28rpx;
  border-radius: 24rpx;
  font-size: 28rpx;
  line-height: 1.7;
  word-break: break-all;
}

.bubble.user {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
  border-bottom-right-radius: 6rpx;
}

.bubble.assistant {
  background: #fff;
  color: #333;
  border-bottom-left-radius: 6rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.04);
}

.input-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #f0e0e0;
  gap: 16rpx;
  z-index: 20;
}

.chat-input {
  flex: 1;
  background: #f8f0f0;
  border-radius: 36rpx;
  padding: 22rpx 28rpx;
  font-size: 28rpx;
}

.send-btn {
  width: 68rpx;
  height: 68rpx;
  border-radius: 50%;
  background: #e0c8c6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn.active {
  background: var(--primary);
}

.send-icon {
  color: #fff;
  font-size: 34rpx;
  font-weight: 700;
}
</style>
