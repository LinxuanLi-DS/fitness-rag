<template>
  <view class="period-page">
    <!-- 顶部 -->
    <view class="header">
      <text class="header-title">经期记录</text>
      <!-- 模式切换 -->
      <view class="mode-row">
        <view
          v-for="m in modes"
          :key="m.id"
          class="mode-btn"
          :class="{ active: currentMode === m.id }"
          @tap="confirmSwitchMode(m.id)"
        >
          <text class="mode-icon">{{ m.icon }}</text>
          <text class="mode-name">{{ m.name }}</text>
        </view>
      </view>
    </view>

    <!-- 当前状态卡片 -->
    <view class="status-card">
      <view class="status-circle">
        <text class="cycle-day">{{ status?.current_cycle_day || '--' }}</text>
        <text class="cycle-label">天</text>
      </view>
      <view class="status-info">
        <text class="status-phase">{{ status?.current_phase || modeStatusText }}</text>
        <text class="status-next">{{ modeNextText }}</text>
      </view>
    </view>

    <!-- 日历 -->
    <view class="card">
      <view class="cal-header">
        <view class="cal-nav" @tap="changeMonth(-1)">‹</view>
        <text class="cal-title">{{ calYear }}年{{ calMonth + 1 }}月</text>
        <view class="cal-nav" @tap="changeMonth(1)">›</view>
      </view>
      <view class="cal-weekdays">
        <text v-for="d in weekDays" :key="d" class="cal-weekday">{{ d }}</text>
      </view>
      <view class="cal-grid">
        <view
          v-for="(cell, i) in calendarCells"
          :key="i"
          class="cal-cell"
          :class="{ empty: !cell.day, period: cell.isPeriod, predicted: cell.isPredicted, today: cell.isToday, logged: cell.isLogged }"
          @tap="cell.day && selectDate(cell.day)"
        >
          <text class="cal-day">{{ cell.day || '' }}</text>
          <view class="cal-dot" v-if="cell.isPeriod"></view>
        </view>
      </view>
      <view class="cal-legend">
        <view class="legend-item">
          <view class="legend-dot period"></view>
          <text class="legend-text">经期</text>
        </view>
        <view class="legend-item">
          <view class="legend-dot predicted"></view>
          <text class="legend-text">预测</text>
        </view>
        <view class="legend-item">
          <view class="legend-dot logged"></view>
          <text class="legend-text">已记录</text>
        </view>
      </view>
    </view>

    <!-- 操作按钮 (经期模式) -->
    <view class="action-row" v-if="currentMode === 'period'">
      <button class="action-btn primary" @tap="recordStart" :loading="loading">
        <text class="btn-text">记录经期开始</text>
      </button>
      <button class="action-btn secondary" @tap="recordEnd" :loading="loading">
        <text class="btn-text2">记录经期结束</text>
      </button>
    </view>

    <!-- 备孕模式提示 -->
    <view class="card" v-if="currentMode === 'pregnancy'">
      <view class="card-header">
        <text class="card-title">备孕记录</text>
      </view>
      <view class="track-section">
        <text class="track-label">排卵测试</text>
        <view class="track-options">
          <view v-for="o in ovulationOptions" :key="o" class="track-opt" :class="{ active: todayOvulation === o }" @tap="setOvulation(o)">{{ o }}</view>
        </view>
      </view>
      <view class="track-section">
        <text class="track-label">同房记录</text>
        <view class="toggle-row" @tap="toggleIntimacy">
          <text class="toggle-text">{{ todayIntimacy ? '已记录 ✓' : '点击记录今日' }}</text>
        </view>
      </view>
    </view>

    <!-- 怀孕模式提示 -->
    <view class="card" v-if="currentMode === 'baby'">
      <view class="card-header">
        <text class="card-title">孕期记录</text>
      </view>
      <view class="track-section">
        <text class="track-label">当前孕周</text>
        <view class="week-input-row">
          <input v-model="pregWeek" type="number" class="week-input" placeholder="周" />
          <text class="week-unit">周</text>
          <input v-model="pregDay" type="number" class="week-input" placeholder="天" />
          <text class="week-unit">天</text>
        </view>
      </view>
      <view class="track-section">
        <text class="track-label">产检记录</text>
        <view class="toggle-row" @tap="addCheckup">
          <text class="toggle-text">+ 添加产检记录</text>
        </view>
      </view>
    </view>

    <!-- 育儿模式提示 -->
    <view class="card" v-if="currentMode === 'parenting'">
      <view class="card-header">
        <text class="card-title">育儿记录</text>
      </view>
      <view class="track-section">
        <text class="track-label">喂养方式</text>
        <view class="track-options">
          <view v-for="f in feedOptions" :key="f" class="track-opt" :class="{ active: todayFeed === f }" @tap="setFeed(f)">{{ f }}</view>
        </view>
      </view>
      <view class="track-section">
        <text class="track-label">宝宝睡眠</text>
        <view class="track-options">
          <view v-for="s in sleepOptions" :key="s" class="track-opt" :class="{ active: todaySleep === s }" @tap="setSleep(s)">{{ s }}</view>
        </view>
      </view>
    </view>

    <!-- 今日状态记录 (经期模式通用) -->
    <view class="card" v-if="currentMode === 'period'">
      <view class="card-header">
        <text class="card-title">今日状态</text>
        <text class="card-date">{{ todayStr }}</text>
      </view>

      <!-- 流量 -->
      <view class="track-section">
        <text class="track-label">流量</text>
        <view class="track-options">
          <view v-for="f in flowOptions" :key="f" class="track-opt" :class="{ active: todayFlow === f }" @tap="setFlow(f)">{{ f }}</view>
        </view>
      </view>

      <!-- 颜色 -->
      <view class="track-section">
        <text class="track-label">颜色</text>
        <view class="track-options">
          <view v-for="c in colorOptions" :key="c.value" class="track-opt color-opt" :class="{ active: todayColor === c.value }" @tap="setColor(c.value)">
            <view class="color-circle" :style="{ background: c.hex }"></view>
            <text class="color-name">{{ c.name }}</text>
          </view>
        </view>
      </view>

      <!-- 症状 -->
      <view class="track-section">
        <text class="track-label">症状（可多选）</text>
        <view class="track-options symptom-options">
          <view v-for="s in symptomOptions" :key="s" class="track-opt symptom-opt" :class="{ active: todaySymptoms.includes(s) }" @tap="toggleSymptom(s)">{{ s }}</view>
        </view>
      </view>

      <!-- 体温 -->
      <view class="track-section">
        <text class="track-label">体温</text>
        <view class="temp-row">
          <input v-model="todayTemp" type="digit" class="temp-input" placeholder="36.5" @blur="saveTemp" />
          <text class="temp-unit">°C</text>
        </view>
      </view>

      <!-- 喝水 -->
      <view class="track-section">
        <text class="track-label">喝水（每杯250ml）</text>
        <view class="water-row">
          <view
            v-for="i in 8"
            :key="i"
            class="water-cup"
            :class="{ filled: i <= waterCount }"
            @tap="toggleWater(i)"
          >
            <text class="cup-icon">{{ i <= waterCount ? '💧' : '○' }}</text>
          </view>
        </view>
        <text class="water-info">已喝 {{ waterCount * 250 }}ml / 2000ml</text>
      </view>

      <!-- 体重 -->
      <view class="track-section">
        <text class="track-label">体重</text>
        <view class="temp-row">
          <input v-model="todayWeight" type="digit" class="temp-input" placeholder="55.0" @blur="saveWeight" />
          <text class="temp-unit">kg</text>
        </view>
      </view>
    </view>

    <!-- 历史记录 -->
    <view class="card">
      <view class="card-header">
        <text class="card-title">历史记录</text>
      </view>
      <view v-if="history.length === 0" class="empty-history">
        <text class="empty-text">还没有记录</text>
      </view>
      <view v-for="(h, i) in history" :key="i" class="history-item">
        <view class="history-left">
          <text class="history-date">{{ h.start_date }}</text>
          <text class="history-end" v-if="h.end_date">至 {{ h.end_date }}</text>
        </view>
        <view class="history-right">
          <text class="history-dur">{{ h.duration || '?' }}天</text>
          <text class="history-status" :class="{ active: !h.end_date }">{{ h.end_date ? '已结束' : '进行中' }}</text>
          <view class="delete-btn" @tap.stop="deleteRecord(h, i)">
            <text class="delete-icon">×</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { api } from "@/utils/api";

const modes = [
  { id: "period", name: "经期", icon: "🌸" },
  { id: "pregnancy", name: "备孕", icon: "🤰" },
  { id: "baby", name: "怀孕", icon: "👶" },
  { id: "parenting", name: "育儿", icon: "🍼" },
];

const currentMode = ref("period");
const status = ref<any>(null);
const history = ref<any[]>([]);
const loading = ref(false);
const waterCount = ref(0);
const todayWeight = ref("");

const today = new Date();
const todayStr = computed(() => `${today.getMonth() + 1}月${today.getDate()}日`);

// 模式相关文案
const modeStatusText = computed(() => {
  const map: Record<string, string> = {
    period: "暂无数据",
    pregnancy: "记录排卵日开始备孕",
    baby: "记录你的孕期",
    parenting: "记录宝宝的成长",
  };
  return map[currentMode.value] || "";
});

const modeNextText = computed(() => {
  if (currentMode.value === "period" && !status.value?.next_predicted_date) return "记录经期数据开始追踪";
  if (status.value?.next_predicted_date) return `预计下次: ${status.value.next_predicted_date}`;
  const map: Record<string, string> = {
    pregnancy: "开始记录排卵日",
    baby: "记录孕周开始追踪",
    parenting: "记录喂养和睡眠",
  };
  return map[currentMode.value] || "";
});

// 日历
const calYear = ref(today.getFullYear());
const calMonth = ref(today.getMonth());
const weekDays = ["日", "一", "二", "三", "四", "五", "六"];
const periodDays = ref<Set<string>>(new Set());
const predictedDays = ref<Set<string>>(new Set());
const loggedDays = ref<Set<string>>(new Set());

// 经期模式选项
const flowOptions = ["无", "少量", "中等", "多", "大量"];
const colorOptions = [
  { value: "bright_red", name: "鲜红", hex: "#e53935" },
  { value: "dark_red", name: "暗红", hex: "#b71c1c" },
  { value: "brown", name: "褐色", hex: "#795548" },
  { value: "pink", name: "粉色", hex: "#f48fb1" },
];
const symptomOptions = ["痛经", "头痛", "胸胀", "疲劳", "失眠", "情绪波动", "食欲增加", "腰酸"];

// 备孕模式选项
const ovulationOptions = ["阴性", "弱阳", "强阳", "排卵"];
const todayOvulation = ref("");
const todayIntimacy = ref(false);

// 怀孕模式
const pregWeek = ref("");
const pregDay = ref("");

// 育儿模式
const feedOptions = ["母乳", "奶粉", "混合"];
const sleepOptions = ["好", "一般", "差"];
const todayFeed = ref("");
const todaySleep = ref("");

// 今日记录
const todayFlow = ref("");
const todayColor = ref("");
const todaySymptoms = ref<string[]>([]);
const todayTemp = ref("");

const calendarCells = computed(() => {
  const firstDay = new Date(calYear.value, calMonth.value, 1).getDay();
  const daysInMonth = new Date(calYear.value, calMonth.value + 1, 0).getDate();
  const cells: any[] = [];
  for (let i = 0; i < firstDay; i++) cells.push({ day: 0 });
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${calYear.value}-${String(calMonth.value + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    cells.push({
      day: d, dateStr,
      isPeriod: periodDays.value.has(dateStr),
      isPredicted: predictedDays.value.has(dateStr),
      isToday: d === today.getDate() && calMonth.value === today.getMonth() && calYear.value === today.getFullYear(),
      isLogged: loggedDays.value.has(dateStr),
    });
  }
  return cells;
});

function changeMonth(delta: number) {
  calMonth.value += delta;
  if (calMonth.value > 11) { calMonth.value = 0; calYear.value++; }
  if (calMonth.value < 0) { calMonth.value = 11; calYear.value--; }
}

function selectDate(day: number) {
  const dateStr = `${calYear.value}-${String(calMonth.value + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  uni.showModal({
    title: `${calMonth.value + 1}月${day}日`,
    content: periodDays.value.has(dateStr) ? "这天是经期日" : "要标记为经期日吗？",
    confirmText: periodDays.value.has(dateStr) ? "知道了" : "标记",
    showCancel: !periodDays.value.has(dateStr),
    cancelText: "取消",
    success: (res) => {
      if (res.confirm && !periodDays.value.has(dateStr)) {
        // TODO: 标记经期
      }
    },
  });
}

function confirmSwitchMode(modeId: string) {
  if (modeId === currentMode.value) return;
  const modeName = modes.find((m) => m.id === modeId)?.name || "";
  uni.showModal({
    title: `切换到${modeName}模式`,
    content: `确定要切换到${modeName}模式吗？页面内容将随之改变。`,
    confirmText: "确定",
    success: (res) => {
      if (res.confirm) {
        currentMode.value = modeId;
        uni.setStorageSync("appMode", modeId);
        uni.showToast({ title: `已切换到${modeName}模式`, icon: "none" });
      }
    },
  });
}

onShow(() => {
  currentMode.value = uni.getStorageSync("appMode") || "period";
  loadData();
  loadDailyStatus();
});

async function loadData() {
  try {
    status.value = await api({ url: "/period/predict" }).catch(() => null);
    const h = await api({ url: "/period/history" }).catch(() => null);
    history.value = h?.records || [];
    const pDays = new Set<string>();
    history.value.forEach((rec: any) => {
      if (rec.start_date && rec.end_date) {
        const start = new Date(rec.start_date);
        const end = new Date(rec.end_date);
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
          pDays.add(d.toISOString().split('T')[0]);
        }
      }
    });
    periodDays.value = pDays;
    // Save to global storage for analysis page
    uni.setStorageSync("period_history", JSON.stringify(history.value));
  } catch {}
}

function loadDailyStatus() {
  const dateStr = new Date().toISOString().split("T")[0];
  const username = uni.getStorageSync("username") || "";
  const prefix = `daily_${username}_${dateStr}`;
  todayFlow.value = uni.getStorageSync(`${prefix}_flow`) || "";
  todayColor.value = uni.getStorageSync(`${prefix}_color`) || "";
  const symptoms = uni.getStorageSync(`${prefix}_symptoms`);
  todaySymptoms.value = symptoms ? JSON.parse(symptoms) : [];
  todayTemp.value = uni.getStorageSync(`${prefix}_temp`) || "";
  waterCount.value = parseInt(uni.getStorageSync(`${prefix}_water`) || "0");
  todayWeight.value = uni.getStorageSync(`${prefix}_weight`) || "";
  todayOvulation.value = uni.getStorageSync(`${prefix}_ovulation`) || "";
  todayIntimacy.value = uni.getStorageSync(`${prefix}_intimacy`) === "true";
  pregWeek.value = uni.getStorageSync("preg_week") || "";
  pregDay.value = uni.getStorageSync("preg_day") || "";
  todayFeed.value = uni.getStorageSync(`${prefix}_feed`) || "";
  todaySleep.value = uni.getStorageSync(`${prefix}_sleep`) || "";
  // Load logged days
  const logged = uni.getStorageSync(`logged_days_${username}`);
  loggedDays.value = logged ? new Set(JSON.parse(logged)) : new Set();
}

function saveDailyField(field: string, value: any) {
  const dateStr = new Date().toISOString().split("T")[0];
  const username = uni.getStorageSync("username") || "";
  const prefix = `daily_${username}_${dateStr}`;
  uni.setStorageSync(`${prefix}_${field}`, typeof value === "object" ? JSON.stringify(value) : String(value));
  // Mark day as logged
  const logged = new Set(loggedDays.value);
  logged.add(dateStr);
  loggedDays.value = logged;
  uni.setStorageSync(`logged_days_${username}`, JSON.stringify(Array.from(logged)));
}

// 经期模式
function setFlow(f: string) {
  todayFlow.value = todayFlow.value === f ? "" : f;
  saveDailyField("flow", todayFlow.value);
}

function setColor(c: string) {
  todayColor.value = todayColor.value === c ? "" : c;
  saveDailyField("color", todayColor.value);
}

function toggleSymptom(s: string) {
  const idx = todaySymptoms.value.indexOf(s);
  if (idx >= 0) todaySymptoms.value.splice(idx, 1);
  else todaySymptoms.value.push(s);
  saveDailyField("symptoms", todaySymptoms.value);
}

function saveTemp() {
  if (!todayTemp.value) return;
  saveDailyField("temp", todayTemp.value);
  uni.showToast({ title: `体温 ${todayTemp.value}°C 已保存`, icon: "none" });
}

function toggleWater(n: number) {
  // 点击已填充的最后一个取消，否则设为n
  if (n === waterCount.value) {
    waterCount.value = n - 1;
  } else {
    waterCount.value = n;
  }
  saveDailyField("water", waterCount.value);
}

function saveWeight() {
  if (!todayWeight.value) return;
  saveDailyField("weight", todayWeight.value);
  uni.showToast({ title: `${todayWeight.value}kg 已保存`, icon: "none" });
}

// 备孕模式
function setOvulation(o: string) {
  todayOvulation.value = todayOvulation.value === o ? "" : o;
  saveDailyField("ovulation", todayOvulation.value);
}

function toggleIntimacy() {
  todayIntimacy.value = !todayIntimacy.value;
  saveDailyField("intimacy", todayIntimacy.value);
  uni.showToast({ title: todayIntimacy.value ? "已记录" : "已取消", icon: "none" });
}

// 怀孕模式
function addCheckup() {
  uni.showModal({
    title: "添加产检记录",
    editable: true,
    placeholderText: "输入产检内容",
    success: (res) => {
      if (res.confirm && res.content) {
        const dateStr = new Date().toISOString().split("T")[0];
        const key = `checkups_${uni.getStorageSync("username")}`;
        const list = JSON.parse(uni.getStorageSync(key) || "[]");
        list.unshift({ date: dateStr, content: res.content });
        uni.setStorageSync(key, JSON.stringify(list));
        uni.showToast({ title: "已保存", icon: "success" });
      }
    },
  });
}

// 育儿模式
function setFeed(f: string) {
  todayFeed.value = todayFeed.value === f ? "" : f;
  saveDailyField("feed", todayFeed.value);
}

function setSleep(s: string) {
  todaySleep.value = todaySleep.value === s ? "" : s;
  saveDailyField("sleep", todaySleep.value);
}

// 经期记录操作
async function recordStart() {
  loading.value = true;
  try {
    await api({ url: "/period/record", method: "POST", data: { start_date: new Date().toISOString().split("T")[0] } });
    uni.showToast({ title: "已记录", icon: "success" });
    loadData();
  } catch { uni.showToast({ title: "记录失败", icon: "none" }); }
  loading.value = false;
}

async function recordEnd() {
  loading.value = true;
  try {
    const latestOpen = history.value.find((h: any) => !h.end_date);
    if (latestOpen) {
      await api({ url: `/period/record/${latestOpen.id}`, method: "PUT", data: { end_date: new Date().toISOString().split("T")[0] } });
      uni.showToast({ title: "已记录结束", icon: "success" });
    } else { uni.showToast({ title: "没有进行中的记录", icon: "none" }); }
    loadData();
  } catch { uni.showToast({ title: "记录失败", icon: "none" }); }
  loading.value = false;
}

function deleteRecord(h: any, idx: number) {
  uni.showModal({
    title: "确认删除",
    content: `确定删除 ${h.start_date} 的记录吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          if (h.id) {
            await api({ url: `/period/record/${h.id}`, method: "DELETE" }).catch(() => {});
          }
          history.value.splice(idx, 1);
          uni.setStorageSync("period_history", JSON.stringify(history.value));
          loadData();
          uni.showToast({ title: "已删除", icon: "success" });
        } catch { uni.showToast({ title: "删除失败", icon: "none" }); }
      }
    },
  });
}
</script>

<style scoped>
.period-page { min-height: 100vh; background: #fff5f5; padding-bottom: 160rpx; }
.header { padding: 88rpx 32rpx 20rpx; background: linear-gradient(135deg, #e8837c, #d4625a); }
.header-title { font-size: 38rpx; font-weight: 600; color: #fff; display: block; margin-bottom: 16rpx; }
.mode-row { display: flex; gap: 10rpx; }
.mode-btn { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4rpx; padding: 12rpx 8rpx; border-radius: 16rpx; background: rgba(255,255,255,0.12); }
.mode-btn.active { background: rgba(255,255,255,0.3); }
.mode-icon { font-size: 28rpx; }
.mode-name { font-size: 22rpx; color: rgba(255,255,255,0.8); }
.mode-btn.active .mode-name { color: #fff; font-weight: 500; }
.status-card { display: flex; align-items: center; background: #fff; border-radius: 24rpx; padding: 36rpx 32rpx; margin: -16rpx 24rpx 24rpx; box-shadow: 0 8rpx 32rpx rgba(232,131,124,0.12); }
.status-circle { width: 130rpx; height: 130rpx; border-radius: 50%; background: linear-gradient(135deg, #fce4ec, #f8bbd0); display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 24rpx; }
.cycle-day { font-size: 44rpx; font-weight: 700; color: #d4625a; line-height: 1; }
.cycle-label { font-size: 20rpx; color: #e8837c; }
.status-info { flex: 1; }
.status-phase { font-size: 32rpx; font-weight: 600; color: #333; display: block; margin-bottom: 6rpx; }
.status-next { font-size: 24rpx; color: #999; }
.card { background: #fff; border-radius: 24rpx; padding: 28rpx; margin: 0 24rpx 20rpx; box-shadow: 0 2rpx 12rpx rgba(232,131,124,0.05); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
.card-title { font-size: 30rpx; font-weight: 600; color: #333; }
.card-date { font-size: 24rpx; color: #bbb; }
.cal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.cal-nav { font-size: 36rpx; color: #e8837c; padding: 8rpx 20rpx; }
.cal-title { font-size: 28rpx; font-weight: 600; color: #333; }
.cal-weekdays { display: flex; margin-bottom: 8rpx; }
.cal-weekday { flex: 1; text-align: center; font-size: 22rpx; color: #bbb; }
.cal-grid { display: flex; flex-wrap: wrap; }
.cal-cell { width: 14.28%; height: 72rpx; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; }
.cal-cell.empty { pointer-events: none; }
.cal-day { font-size: 26rpx; color: #333; }
.cal-cell.today .cal-day { color: #e8837c; font-weight: 700; }
.cal-cell.period { background: rgba(232,131,124,0.12); border-radius: 8rpx; }
.cal-cell.predicted { background: rgba(232,131,124,0.06); border-radius: 8rpx; }
.cal-cell.logged { border-bottom: 3rpx solid #4caf50; }
.cal-dot { width: 8rpx; height: 8rpx; border-radius: 50%; background: #e8837c; margin-top: 2rpx; }
.cal-legend { display: flex; gap: 24rpx; margin-top: 16rpx; justify-content: center; }
.legend-item { display: flex; align-items: center; gap: 8rpx; }
.legend-dot { width: 16rpx; height: 16rpx; border-radius: 4rpx; }
.legend-dot.period { background: rgba(232,131,124,0.3); }
.legend-dot.predicted { background: rgba(232,131,124,0.1); border: 1rpx dashed #e8837c; }
.legend-dot.logged { background: #4caf50; }
.legend-text { font-size: 22rpx; color: #999; }
.action-row { display: flex; gap: 16rpx; padding: 0 24rpx 20rpx; }
.action-btn { flex: 1; border: none; border-radius: 20rpx; padding: 24rpx; font-size: 28rpx; }
.action-btn.primary { background: linear-gradient(135deg, #e8837c, #d4625a); }
.btn-text { color: #fff; }
.action-btn.secondary { background: #fff; border: 2rpx solid #f0d0ce; }
.btn-text2 { color: #e8837c; }
.track-section { margin-bottom: 24rpx; }
.track-label { font-size: 26rpx; color: #666; display: block; margin-bottom: 12rpx; }
.track-options { display: flex; flex-wrap: wrap; gap: 12rpx; }
.track-opt { padding: 12rpx 24rpx; border-radius: 24rpx; font-size: 24rpx; background: #f8f0f0; color: #999; }
.track-opt.active { background: #fff0ef; color: #e8837c; font-weight: 500; border: 1rpx solid #f0d0ce; }
.color-opt { display: flex; align-items: center; gap: 8rpx; }
.color-circle { width: 20rpx; height: 20rpx; border-radius: 50%; }
.color-name { font-size: 24rpx; }
.symptom-options { gap: 10rpx; }
.temp-row { display: flex; align-items: center; gap: 12rpx; }
.temp-input { width: 200rpx; background: #f8f0f0; border-radius: 16rpx; padding: 14rpx 20rpx; font-size: 28rpx; text-align: center; }
.temp-unit { font-size: 28rpx; color: #999; }
.water-row { display: flex; gap: 8rpx; flex-wrap: wrap; }
.water-cup { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; border-radius: 12rpx; background: #f8f0f0; font-size: 28rpx; }
.water-cup.filled { background: #e3f2fd; }
.cup-icon { font-size: 28rpx; }
.water-info { font-size: 22rpx; color: #999; margin-top: 8rpx; }
.toggle-row { padding: 16rpx 24rpx; background: #f8f0f0; border-radius: 16rpx; }
.toggle-text { font-size: 28rpx; color: #666; }
.week-input-row { display: flex; align-items: center; gap: 8rpx; }
.week-input { width: 120rpx; background: #f8f0f0; border-radius: 12rpx; padding: 14rpx 16rpx; font-size: 28rpx; text-align: center; }
.week-unit { font-size: 28rpx; color: #999; }
.empty-history { text-align: center; padding: 32rpx; }
.empty-text { font-size: 26rpx; color: #ccc; }
.history-item { display: flex; justify-content: space-between; align-items: center; padding: 18rpx 0; border-bottom: 1rpx solid #f8f0f0; }
.history-item:last-child { border-bottom: none; }
.history-left { display: flex; flex-direction: column; }
.history-date { font-size: 28rpx; color: #333; font-weight: 500; }
.history-end { font-size: 22rpx; color: #bbb; margin-top: 4rpx; }
.history-right { display: flex; align-items: center; gap: 12rpx; }
.history-dur { font-size: 26rpx; color: #666; }
.history-status { font-size: 22rpx; color: #999; background: #f8f0f0; padding: 4rpx 12rpx; border-radius: 12rpx; }
.history-status.active { color: #e8837c; background: #fff0ef; }
.delete-btn { width: 44rpx; height: 44rpx; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: #fff0ef; }
.delete-icon { color: #e8837c; font-size: 28rpx; }
</style>
