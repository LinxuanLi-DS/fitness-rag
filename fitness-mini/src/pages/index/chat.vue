<template>
  <view class="chat-page">
    <!-- 助手切换 -->
    <view class="assistant-tabs">
      <view
        v-for="a in assistants"
        :key="a.id"
        class="tab-item"
        :class="{ active: currentAssistant === a.id }"
        @tap="currentAssistant = a.id"
      >
        <text>{{ a.emoji }} {{ a.name }}</text>
      </view>
    </view>

    <!-- 消息列表 -->
    <scroll-view
      class="message-list"
      scroll-y
      :scroll-into-view="scrollToId"
      :scroll-with-animation="true"
    >
      <view v-if="messages.length === 0" class="empty-chat">
        <text class="empty-text">和{{ currentAssistantName }}聊聊天吧</text>
      </view>
      <view
        v-for="(msg, i) in messages"
        :key="i"
        :id="'msg-' + i"
        class="message-row"
        :class="msg.role"
      >
        <view class="bubble" :class="msg.role">
          <text>{{ msg.content }}</text>
        </view>
      </view>
      <view v-if="streaming" class="message-row assistant">
        <view class="bubble assistant">
          <text>{{ streamingText }}</text>
        </view>
      </view>
      <view id="msg-bottom"></view>
    </scroll-view>

    <!-- 输入区 -->
    <view class="input-area">
      <input
        v-model="inputText"
        class="chat-input"
        placeholder="输入消息..."
        confirm-type="send"
        @confirm="send"
        :disabled="streaming"
      />
      <view class="send-btn" :class="{ disabled: streaming || !inputText }" @tap="send">
        <text class="send-icon">↑</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { chatStream } from "@/utils/api";

const assistants = [
  { id: "xiaojian", name: "小健", emoji: "💪" },
  { id: "xiaokang", name: "小康", emoji: "🥗" },
  { id: "shiqing", name: "十七", emoji: "💗" },
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

onLoad((query: any) => {
  loadHistory();
  if (query?.message) {
    inputText.value = decodeURIComponent(query.message);
    send();
  }
});

function loadHistory() {
  const username = uni.getStorageSync("username");
  const key = `fitherHistories_${username}`;
  const saved = uni.getStorageSync(key);
  if (saved) {
    try {
      const all = JSON.parse(saved);
      messages.value = all[currentAssistant.value] || [];
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
  all[currentAssistant.value] = messages.value.slice(-10);
  uni.setStorageSync(key, JSON.stringify(all));
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
    messages.value.push({ role: "assistant", content: "抱歉，出了点问题，请重试" });
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

.assistant-tabs {
  display: flex;
  background: #fff;
  padding: 16rpx 24rpx;
  gap: 16rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 14rpx;
  border-radius: 12rpx;
  font-size: 26rpx;
  background: #f5f5f5;
}

.tab-item.active {
  background: #fff0ef;
  color: #e8837c;
  font-weight: 500;
}

.message-list {
  flex: 1;
  padding: 24rpx;
  overflow-y: auto;
}

.empty-chat {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400rpx;
}

.empty-text {
  color: #ccc;
  font-size: 28rpx;
}

.message-row {
  display: flex;
  margin-bottom: 20rpx;
}

.message-row.user {
  justify-content: flex-end;
}

.bubble {
  max-width: 75%;
  padding: 20rpx 28rpx;
  border-radius: 24rpx;
  font-size: 28rpx;
  line-height: 1.6;
  word-break: break-all;
}

.bubble.user {
  background: linear-gradient(135deg, #e8837c, #d4625a);
  color: #fff;
  border-bottom-right-radius: 6rpx;
}

.bubble.assistant {
  background: #fff;
  color: #333;
  border-bottom-left-radius: 6rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.input-area {
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #f0f0f0;
  gap: 16rpx;
}

.chat-input {
  flex: 1;
  background: #f5f5f5;
  border-radius: 32rpx;
  padding: 20rpx 28rpx;
  font-size: 28rpx;
}

.send-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #e8837c;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn.disabled {
  opacity: 0.4;
}

.send-icon {
  color: #fff;
  font-size: 32rpx;
  font-weight: 700;
}
</style>
