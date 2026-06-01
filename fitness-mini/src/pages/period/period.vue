<template>
  <view class="period-page">
    <!-- 顶部 -->
    <view class="header">
      <text class="header-title">{{ pageTitle }}</text>
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
      <view class="status-circle" :class="currentMode">
        <text class="cycle-day">{{ mainNumber }}</text>
        <text class="cycle-label">{{ mainLabel }}</text>
      </view>
      <view class="status-info">
        <text class="status-phase">{{ statusTitle }}</text>
        <text class="status-next">{{ statusSub }}</text>
      </view>
    </view>

    <!-- 日历 (所有模式共用) -->
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
          :class="{ empty: !cell.day, period: cell.isPeriod, predicted: cell.isPredicted, today: cell.isToday, logged: cell.isLogged, ovulation: cell.isOvulation }"
          @tap="cell.day && selectDate(cell)"
        >
          <text class="cal-day">{{ cell.day || '' }}</text>
          <view class="cal-dot" v-if="cell.isPeriod"></view>
          <view class="cal-dot ov-dot" v-if="cell.isOvulation"></view>
        </view>
      </view>
      <view class="cal-legend">
        <view class="legend-item" v-if="currentMode === 'period'">
          <view class="legend-dot period"></view>
          <text class="legend-text">经期</text>
        </view>
        <view class="legend-item" v-if="currentMode === 'pregnancy'">
          <view class="legend-dot ov-dot"></view>
          <text class="legend-text">排卵日</text>
        </view>
        <view class="legend-item" v-if="currentMode === 'baby'">
          <view class="legend-dot checkup"></view>
          <text class="legend-text">产检</text>
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

    <!-- ============= 经期模式 ============= -->
    <view v-if="currentMode === 'period'">
      <view class="action-row">
        <button class="action-btn primary" @tap="recordStart" :loading="loading">
          <text class="btn-text">记录经期开始</text>
        </button>
        <button class="action-btn secondary" @tap="recordEnd" :loading="loading">
          <text class="btn-text2">记录经期结束</text>
        </button>
      </view>

      <view class="card">
        <view class="card-header">
          <text class="card-title">今日状态</text>
          <text class="card-date">{{ todayStr }}</text>
        </view>
        <view class="track-section">
          <view class="track-label-row">
            <text class="track-label">流量</text>
            <text class="saved-tag" v-if="flowSaved">已记录 ✓</text>
          </view>
          <view class="track-options">
            <view v-for="f in flowOptions" :key="f" class="track-opt" :class="{ active: todayFlow === f, locked: flowSaved && todayFlow !== f }" @tap="setFlow(f)">{{ f }}</view>
          </view>
        </view>
        <view class="track-section">
          <view class="track-label-row">
            <text class="track-label">颜色</text>
            <text class="saved-tag" v-if="colorSaved">已记录 ✓</text>
          </view>
          <view class="track-options">
            <view v-for="c in colorOptions" :key="c.value" class="track-opt color-opt" :class="{ active: todayColor === c.value, locked: colorSaved && todayColor !== c.value }" @tap="setColor(c.value)">
              <view class="color-circle" :style="{ background: c.hex }"></view>
              <text class="color-name">{{ c.name }}</text>
            </view>
          </view>
        </view>
        <view class="track-section">
          <view class="track-label-row">
            <text class="track-label">症状（可多选）</text>
            <text class="saved-tag" v-if="symptomsSaved">已记录 ✓</text>
          </view>
          <view class="track-options symptom-options">
            <view v-for="s in symptomOptions" :key="s" class="track-opt symptom-opt" :class="{ active: todaySymptoms.includes(s), locked: symptomsSaved }" @tap="toggleSymptom(s)">{{ s }}</view>
          </view>
        </view>
        <view class="track-section">
          <view class="track-label-row">
            <text class="track-label">基础体温</text>
            <text class="saved-tag" v-if="tempSaved">已记录 ✓</text>
          </view>
          <view class="temp-row">
            <input v-model="todayTemp" type="digit" class="temp-input" :disabled="tempSaved" placeholder="36.5" @blur="saveTemp" />
            <text class="temp-unit">°C</text>
          </view>
        </view>
        <view class="track-section">
          <view class="track-label-row">
            <text class="track-label">喝水（每杯250ml）</text>
            <text class="saved-tag" v-if="waterSaved">已记录 ✓</text>
          </view>
          <view class="water-row">
            <view v-for="i in 8" :key="i" class="water-cup" :class="{ filled: i <= waterCount, locked: waterSaved }" @tap="toggleWater(i)">
              <text class="cup-icon">{{ i <= waterCount ? '💧' : '○' }}</text>
            </view>
          </view>
          <text class="water-info">已喝 {{ waterCount * 250 }}ml / 2000ml</text>
        </view>
        <view class="track-section">
          <view class="track-label-row">
            <text class="track-label">体重</text>
            <text class="saved-tag" v-if="weightSaved">已记录 ✓</text>
          </view>
          <view class="temp-row">
            <input v-model="todayWeight" type="digit" class="temp-input" :disabled="weightSaved" placeholder="55.0" @blur="saveWeight" />
            <text class="temp-unit">kg</text>
          </view>
        </view>
      </view>
    </view>

    <!-- ============= 备孕模式 ============= -->
    <view v-if="currentMode === 'pregnancy'">
      <!-- 备孕天数 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">备孕进度</text>
        </view>
        <view class="progress-grid">
          <view class="progress-item">
            <text class="progress-num">{{ tryDays }}</text>
            <text class="progress-label">备孕天数</text>
          </view>
          <view class="progress-item">
            <text class="progress-num">{{ ovulationCount }}</text>
            <text class="progress-label">记录排卵</text>
          </view>
          <view class="progress-item">
            <text class="progress-num">{{ intimacyCount }}</text>
            <text class="progress-label">同房次数</text>
          </view>
        </view>
      </view>

      <!-- 排卵测试 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">排卵监测</text>
          <text class="card-date">{{ todayStr }}</text>
        </view>
        <view class="track-section">
          <text class="track-label">排卵试纸结果</text>
          <view class="track-options">
            <view v-for="o in ovulationOptions" :key="o.value" class="track-opt ov-opt" :class="{ active: todayOvulation === o.value }" @tap="setOvulation(o.value)">
              <text class="ov-dot-icon" :style="{ color: o.color }">●</text>
              <text>{{ o.name }}</text>
            </view>
          </view>
        </view>
        <view class="track-section">
          <text class="track-label">基础体温</text>
          <view class="temp-row">
            <input v-model="todayTemp" type="digit" class="temp-input" placeholder="36.5" @blur="saveTemp" />
            <text class="temp-unit">°C</text>
          </view>
          <text class="temp-hint">排卵后体温通常升高0.3-0.5°C</text>
        </view>
        <view class="track-section">
          <text class="track-label">宫颈粘液</text>
          <view class="track-options">
            <view v-for="m in mucusOptions" :key="m" class="track-opt" :class="{ active: todayMucus === m }" @tap="setMucus(m)">{{ m }}</view>
          </view>
        </view>
        <view class="track-section">
          <text class="track-label">同房记录</text>
          <view class="intimacy-row" @tap="toggleIntimacy">
            <view class="intimacy-check" :class="{ checked: todayIntimacy }">
              <text v-if="todayIntimacy">✓</text>
            </view>
            <text class="intimacy-text">{{ todayIntimacy ? '今日已记录同房' : '点击记录今日同房' }}</text>
          </view>
        </view>
      </view>

      <!-- 补充剂提醒 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">营养补充</text>
        </view>
        <view class="supplement-list">
          <view v-for="s in supplements" :key="s.name" class="supplement-item" @tap="toggleSupplement(s.name)">
            <view class="supp-check" :class="{ checked: s.taken }"><text v-if="s.taken">✓</text></view>
            <view class="supp-info">
              <text class="supp-name">{{ s.name }}</text>
              <text class="supp-dose">{{ s.dose }}</text>
            </view>
            <text class="supp-status">{{ s.taken ? '已服用' : '未服用' }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- ============= 怀孕模式 ============= -->
    <view v-if="currentMode === 'baby'">
      <!-- 孕周设置 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">孕期信息</text>
        </view>
        <view class="preg-info-row">
          <view class="preg-field">
            <text class="preg-label">预产期</text>
            <picker mode="date" :value="dueDate" @change="onDueDateChange">
              <text class="preg-value">{{ dueDate || '点击设置' }}</text>
            </picker>
          </view>
          <view class="preg-field">
            <text class="preg-label">末次月经</text>
            <picker mode="date" :value="lastPeriod" @change="onLastPeriodChange">
              <text class="preg-value">{{ lastPeriod || '点击设置' }}</text>
            </picker>
          </view>
        </view>
      </view>

      <!-- 宝宝发育 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">宝宝发育</text>
          <text class="card-date">{{ pregWeekNum }}周{{ pregDayNum }}天</text>
        </view>
        <view class="baby-info">
          <text class="baby-fruit">{{ babyFruit }}</text>
          <text class="baby-size">本周宝宝大约{{ babySize }}</text>
          <text class="baby-desc">{{ babyDesc }}</text>
        </view>
      </view>

      <!-- 产检记录 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">产检记录</text>
          <view class="add-btn" @tap="addCheckup">
            <text class="add-btn-text">+ 添加</text>
          </view>
        </view>
        <view v-if="checkups.length === 0" class="empty-section">
          <text class="empty-text">还没有产检记录</text>
        </view>
        <view v-for="(c, i) in checkups" :key="i" class="checkup-item">
          <view class="checkup-left">
            <text class="checkup-date">{{ c.date }}</text>
            <text class="checkup-week" v-if="c.week">第{{ c.week }}周</text>
          </view>
          <view class="checkup-right">
            <text class="checkup-content">{{ c.content }}</text>
            <text class="checkup-result" :class="c.result">{{ c.resultText }}</text>
          </view>
        </view>
        <!-- 下次产检提醒 -->
        <view class="next-checkup" v-if="nextCheckup">
          <text class="next-label">下次产检</text>
          <text class="next-date">{{ nextCheckup }}</text>
        </view>
      </view>

      <!-- 今日记录 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">今日记录</text>
          <text class="card-date">{{ todayStr }}</text>
        </view>
        <view class="track-section">
          <text class="track-label">体重</text>
          <view class="temp-row">
            <input v-model="todayWeight" type="digit" class="temp-input" placeholder="65.0" @blur="saveWeight" />
            <text class="temp-unit">kg</text>
          </view>
          <text class="temp-hint">孕期增重: {{ weightGain }}</text>
        </view>
        <view class="track-section">
          <text class="track-label">胎动计数（1小时）</text>
          <view class="kick-row">
            <view class="kick-btn" @tap="addKick">
              <text class="kick-num">{{ kickCount }}</text>
              <text class="kick-label">次</text>
            </view>
            <text class="kick-hint" v-if="kickCount > 0">正常: 3-5次/小时</text>
            <text class="kick-hint" v-else>点击记录胎动</text>
          </view>
        </view>
        <view class="track-section">
          <text class="track-label">孕期症状</text>
          <view class="track-options symptom-options">
            <view v-for="s in pregnancySymptoms" :key="s" class="track-opt symptom-opt" :class="{ active: todayPregSymptoms.includes(s) }" @tap="togglePregSymptom(s)">{{ s }}</view>
          </view>
        </view>
        <view class="track-section">
          <text class="track-label">心情</text>
          <view class="track-options">
            <view v-for="m in moodOptions" :key="m" class="track-opt" :class="{ active: todayMood === m }" @tap="setMood(m)">{{ m }}</view>
          </view>
        </view>
      </view>
    </view>

    <!-- ============= 育儿模式 ============= -->
    <view v-if="currentMode === 'parenting'">
      <!-- 宝宝信息 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">宝宝信息</text>
        </view>
        <view class="baby-profile">
          <view class="baby-avatar-edit" @tap="chooseBabyAvatar">
            <image :src="babyAvatar || '/static/default-avatar.png'" class="baby-avatar-img" mode="aspectFill" />
            <text class="baby-avatar-edit-text">换头像</text>
          </view>
          <view class="baby-detail">
            <text class="baby-name">{{ babyName || '点击设置昵称' }}</text>
            <text class="baby-age">出生: {{ babyBirthday || '未设置' }}</text>
            <text class="baby-age-days" v-if="babyAgeDays > 0">已出生 {{ babyAgeDays }} 天</text>
          </view>
        </view>
        <view class="baby-set-row">
          <view class="baby-set-item" @tap="setBabyName">
            <text class="baby-set-label">昵称</text>
            <text class="baby-set-val">{{ babyName || '设置' }}</text>
          </view>
          <view class="baby-set-item" @tap="setBabyBirthday">
            <text class="baby-set-label">生日</text>
            <text class="baby-set-val">{{ babyBirthday || '设置' }}</text>
          </view>
          <view class="baby-set-item" @tap="setBabyGender">
            <text class="baby-set-label">性别</text>
            <text class="baby-set-val">{{ babyGender || '设置' }}</text>
          </view>
        </view>
      </view>

      <!-- 喂养记录 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">喂养记录</text>
          <text class="card-date">{{ todayStr }}</text>
        </view>
        <view class="track-section">
          <text class="track-label">喂养方式</text>
          <view class="track-options">
            <view v-for="f in feedOptions" :key="f" class="track-opt" :class="{ active: todayFeed === f }" @tap="setFeed(f)">{{ f }}</view>
          </view>
        </view>
        <view class="track-section" v-if="todayFeed === '奶粉' || todayFeed === '混合'">
          <text class="track-label">今日奶量</text>
          <view class="milk-row">
            <view class="milk-btn" @tap="addMilk(-60)">
              <text class="milk-btn-text">-60</text>
            </view>
            <view class="milk-display">
              <text class="milk-num">{{ todayMilk }}</text>
              <text class="milk-unit">ml</text>
            </view>
            <view class="milk-btn" @tap="addMilk(60)">
              <text class="milk-btn-text">+60</text>
            </view>
          </view>
        </view>
        <view class="track-section" v-if="babyAgeDays > 180">
          <text class="track-label">辅食</text>
          <view class="track-options">
            <view v-for="a in foodOptions" :key="a" class="track-opt" :class="{ active: todayFoods.includes(a) }" @tap="toggleFood(a)">{{ a }}</view>
          </view>
        </view>
      </view>

      <!-- 睡眠记录 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">睡眠记录</text>
          <text class="card-date">{{ todayStr }}</text>
        </view>
        <view class="sleep-summary">
          <text class="sleep-total">今日睡眠: {{ sleepTotal }}小时</text>
        </view>
        <view class="track-section">
          <text class="track-label">睡眠质量</text>
          <view class="track-options">
            <view v-for="s in sleepOptions" :key="s" class="track-opt" :class="{ active: todaySleep === s }" @tap="setSleep(s)">{{ s }}</view>
          </view>
        </view>
        <view class="track-section">
          <text class="track-label">夜醒次数</text>
          <view class="temp-row">
            <input v-model="nightWakes" type="number" class="temp-input" placeholder="0" @blur="saveNightWakes" />
            <text class="temp-unit">次</text>
          </view>
        </view>
      </view>

      <!-- 生长记录 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">生长记录</text>
          <view class="add-btn" @tap="addGrowth">
            <text class="add-btn-text">+ 记录</text>
          </view>
        </view>
        <view v-if="growthRecords.length === 0" class="empty-section">
          <text class="empty-text">还没有生长记录</text>
        </view>
        <view v-for="(g, i) in growthRecords" :key="i" class="growth-item">
          <text class="growth-date">{{ g.date }}</text>
          <view class="growth-data">
            <text class="growth-val">身高 {{ g.height }}cm</text>
            <text class="growth-val">体重 {{ g.weight }}kg</text>
            <text class="growth-val" v-if="g.head">头围 {{ g.head }}cm</text>
          </view>
        </view>
      </view>

      <!-- 疫苗记录 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">疫苗接种</text>
          <view class="add-btn" @tap="addVaccine">
            <text class="add-btn-text">+ 记录</text>
          </view>
        </view>
        <view v-if="vaccines.length === 0" class="empty-section">
          <text class="empty-text">还没有疫苗记录</text>
        </view>
        <view v-for="(v, i) in vaccines" :key="i" class="vaccine-item">
          <view class="vaccine-left">
            <text class="vaccine-name">{{ v.name }}</text>
            <text class="vaccine-date">{{ v.date }}</text>
          </view>
          <text class="vaccine-status" :class="v.done ? 'done' : ''">{{ v.done ? '已接种 ✓' : '待接种' }}</text>
        </view>
      </view>

      <!-- 里程碑 -->
      <view class="card">
        <view class="card-header">
          <text class="card-title">成长里程碑</text>
        </view>
        <view class="milestone-list">
          <view v-for="(m, i) in milestones" :key="i" class="milestone-item" @tap="toggleMilestone(i)">
            <view class="milestone-check" :class="{ checked: m.done }">
              <text v-if="m.done">✓</text>
            </view>
            <view class="milestone-info">
              <text class="milestone-name">{{ m.name }}</text>
              <text class="milestone-age">{{ m.done ? m.date : m.expectedAge }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 历史记录 (经期模式) -->
    <view class="card" v-if="currentMode === 'period'">
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
const todayTemp = ref("");
const todayFlow = ref("");
const todayColor = ref("");
const todaySymptoms = ref<string[]>([]);

// 保存状态标记
const flowSaved = ref(false);
const colorSaved = ref(false);
const symptomsSaved = ref(false);
const tempSaved = ref(false);
const waterSaved = ref(false);
const weightSaved = ref(false);

// 修改前确认
function confirmChange(field: string, callback: () => void) {
  uni.showModal({
    title: "修改已记录数据",
    content: "今日状态已保存，确认要修改吗？",
    success: (res) => {
      if (res.confirm) {
        // 解锁该字段，允许修改
        if (field === 'flow') flowSaved.value = false;
        if (field === 'color') colorSaved.value = false;
        if (field === 'symptoms') symptomsSaved.value = false;
        if (field === 'temp') tempSaved.value = false;
        if (field === 'water') waterSaved.value = false;
        if (field === 'weight') weightSaved.value = false;
        callback();
      }
    },
  });
}

const today = new Date();
const todayStr = computed(() => `${today.getMonth() + 1}月${today.getDate()}日`);

// 日历
const calYear = ref(today.getFullYear());
const calMonth = ref(today.getMonth());
const weekDays = ["日", "一", "二", "三", "四", "五", "六"];
const periodDays = ref<Set<string>>(new Set());
const predictedDays = ref<Set<string>>(new Set());
const loggedDays = ref<Set<string>>(new Set());
const ovulationDays = ref<Set<string>>(new Set());

// 经期选项
const flowOptions = ["无", "少量", "中等", "多", "大量"];
const colorOptions = [
  { value: "bright_red", name: "鲜红", hex: "#e53935" },
  { value: "dark_red", name: "暗红", hex: "#b71c1c" },
  { value: "brown", name: "褐色", hex: "#795548" },
  { value: "pink", name: "粉色", hex: "#f48fb1" },
];
const symptomOptions = ["痛经", "头痛", "胸胀", "疲劳", "失眠", "情绪波动", "食欲增加", "腰酸"];

// 备孕选项
const ovulationOptions = [
  { value: "negative", name: "阴性", color: "#bbb" },
  { value: "weak", name: "弱阳", color: "#ffb74d" },
  { value: "strong", name: "强阳", color: "#f44336" },
  { value: "ovulated", name: "已排卵", color: "#4caf50" },
];
const mucusOptions = ["干燥", "粘稠", "奶油状", "蛋清状（最佳）", "水样"];
const todayOvulation = ref("");
const todayMucus = ref("");
const todayIntimacy = ref(false);
const supplements = ref([
  { name: "叶酸", dose: "0.4mg/天", taken: false },
  { name: "维生素D", dose: "400IU/天", taken: false },
  { name: "铁剂", dose: "按需", taken: false },
  { name: "DHA", dose: "200mg/天", taken: false },
]);

// 怀孕模式
const dueDate = ref("");
const lastPeriod = ref("");
const kickCount = ref(0);
const todayPregSymptoms = ref<string[]>([]);
const todayMood = ref("");
const pregnancySymptoms = ["孕吐", "头晕", "腰酸", "水肿", "便秘", "失眠", "腿抽筋", "心悸"];
const moodOptions = ["😊 开心", "😐 一般", "😢 低落", "😰 焦虑"];
const checkups = ref<any[]>([]);

const pregWeekNum = computed(() => {
  if (!lastPeriod.value) return 0;
  const lp = new Date(lastPeriod.value);
  const diff = Math.floor((today.getTime() - lp.getTime()) / (1000 * 60 * 60 * 24 * 7));
  return diff > 0 ? diff : 0;
});

const pregDayNum = computed(() => {
  if (!lastPeriod.value) return 0;
  const lp = new Date(lastPeriod.value);
  const totalDays = Math.floor((today.getTime() - lp.getTime()) / (1000 * 60 * 60 * 24));
  return totalDays > 0 ? totalDays % 7 : 0;
});

const weightGain = computed(() => {
  if (!todayWeight.value) return "请先记录孕前体重";
  return "记录体重后可查看增重趋势";
});

// 宝宝发育信息（简化版）
const babyFruit = computed(() => {
  const w = pregWeekNum.value;
  if (w < 5) return "🫘";
  if (w < 8) return "🫐";
  if (w < 12) return "🍋";
  if (w < 16) return "🥑";
  if (w < 20) return "🍌";
  if (w < 24) return "🌽";
  if (w < 28) return "🥦";
  if (w < 32) return "🥥";
  if (w < 36) return "🍈";
  return "🍉";
});

const babySize = computed(() => {
  const w = pregWeekNum.value;
  if (w < 5) return "芝麻大小";
  if (w < 8) return "蓝莓大小";
  if (w < 12) return "柠檬大小";
  if (w < 16) return "牛油果大小";
  if (w < 20) return "香蕉大小";
  if (w < 24) return "玉米大小";
  if (w < 28) return "大茄子大小";
  if (w < 32) return "椰子大小";
  if (w < 36) return "哈密瓜大小";
  return "西瓜大小";
});

const babyDesc = computed(() => {
  const w = pregWeekNum.value;
  if (w < 8) return "宝宝正在快速发育，器官开始形成";
  if (w < 12) return "宝宝已经有心跳了，手指和脚趾正在形成";
  if (w < 16) return "宝宝开始有听觉了，能听到你的声音";
  if (w < 20) return "宝宝开始活跃地踢腿了，你很快就能感受到胎动";
  if (w < 24) return "宝宝的肺部正在发育，已经能吞咽羊水了";
  if (w < 28) return "宝宝的眼睛可以睁开了，开始有规律地睡眠和清醒";
  if (w < 32) return "宝宝在积累脂肪，身体越来越圆润";
  if (w < 36) return "宝宝大部分器官已经发育成熟，在为出生做准备";
  if (w < 40) return "宝宝已经足月了，随时可能发动";
  return "预产期已过，请随时关注身体变化";
});

const nextCheckup = computed(() => {
  const w = pregWeekNum.value;
  if (w < 12) return `${12 - w}周后 NT检查`;
  if (w < 16) return `${16 - w}周后 唐筛`;
  if (w < 20) return `${20 - w}周后 大排畸`;
  if (w < 24) return `${24 - w}周后 糖耐`;
  if (w < 28) return `${28 - w}周后 产检`;
  if (w < 36) return "每2周产检一次";
  return "每周产检一次";
});

// 育儿模式
const babyName = ref("");
const babyBirthday = ref("");
const babyGender = ref("");
const babyAvatar = ref("");
const todayFeed = ref("");
const todayMilk = ref(0);
const todaySleep = ref("");
const todayFoods = ref<string[]>([]);
const nightWakes = ref("");
const sleepTotal = ref("0");
const feedOptions = ["母乳", "奶粉", "混合", "辅食"];
const sleepOptions = ["😊 好", "😐 一般", "😫 差"];
const foodOptions = ["米粉", "果泥", "蔬菜泥", "肉泥", "蛋黄", "面条", "粥"];
const growthRecords = ref<any[]>([]);
const vaccines = ref<any[]>([]);
const milestones = ref([
  { name: "抬头", expectedAge: "1-2个月", done: false, date: "" },
  { name: "翻身", expectedAge: "3-4个月", done: false, date: "" },
  { name: "坐稳", expectedAge: "5-7个月", done: false, date: "" },
  { name: "爬行", expectedAge: "7-10个月", done: false, date: "" },
  { name: "站立", expectedAge: "9-12个月", done: false, date: "" },
  { name: "走路", expectedAge: "10-15个月", done: false, date: "" },
  { name: "说第一个词", expectedAge: "10-14个月", done: false, date: "" },
  { name: "有意识叫爸妈", expectedAge: "12-18个月", done: false, date: "" },
]);

const babyAgeDays = computed(() => {
  if (!babyBirthday.value) return 0;
  const bd = new Date(babyBirthday.value);
  return Math.max(0, Math.floor((today.getTime() - bd.getTime()) / (1000 * 60 * 60 * 24)));
});

// 状态卡片
const pageTitle = computed(() => {
  const map: Record<string, string> = { period: "经期记录", pregnancy: "备孕助手", baby: "孕期记录", parenting: "育儿记录" };
  return map[currentMode.value] || "";
});

const mainNumber = computed(() => {
  if (currentMode.value === "period") return status.value?.current_cycle_day || "--";
  if (currentMode.value === "pregnancy") return String(ovulationDays.value.size);
  if (currentMode.value === "baby") return pregWeekNum.value ? String(pregWeekNum.value) : "--";
  if (currentMode.value === "parenting") return babyAgeDays.value ? String(babyAgeDays.value) : "--";
  return "--";
});

const mainLabel = computed(() => {
  const map: Record<string, string> = { period: "天", pregnancy: "次排卵", baby: "周", parenting: "天" };
  return map[currentMode.value] || "";
});

const statusTitle = computed(() => {
  if (currentMode.value === "period") return status.value?.current_phase || "暂无数据";
  if (currentMode.value === "pregnancy") return todayOvulation.value ? `今日: ${ovulationOptions.find(o => o.value === todayOvulation.value)?.name}` : "记录排卵日开始备孕";
  if (currentMode.value === "baby") return pregWeekNum.value ? `孕${pregWeekNum.value}周${pregDayNum.value}天` : "设置末次月经开始追踪";
  if (currentMode.value === "parenting") return babyName.value ? `${babyName.value} ${babyAgeDays.value}天` : "设置宝宝信息开始记录";
  return "";
});

const statusSub = computed(() => {
  if (currentMode.value === "period" && status.value?.next_predicted_date) return `预计下次: ${status.value.next_predicted_date}`;
  if (currentMode.value === "pregnancy") return `备孕${tryDays.value}天 · 同房${intimacyCount.value}次`;
  if (currentMode.value === "baby") return babySize.value;
  if (currentMode.value === "parenting") return babyAgeDays.value > 180 ? "可以添加辅食了" : "纯母乳/奶粉喂养阶段";
  return "";
});

const tryDays = computed(() => {
  const start = uni.getStorageSync("pregnancy_start");
  if (!start) return 0;
  return Math.max(0, Math.floor((today.getTime() - new Date(start).getTime()) / (1000 * 60 * 60 * 24)));
});

const ovulationCount = computed(() => ovulationDays.value.size);

const intimacyCount = computed(() => {
  const saved = uni.getStorageSync(`intimacy_count_${uni.getStorageSync("username")}`);
  return parseInt(saved || "0");
});

// 日历计算
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
      isOvulation: ovulationDays.value.has(dateStr),
    });
  }
  return cells;
});

function changeMonth(delta: number) {
  calMonth.value += delta;
  if (calMonth.value > 11) { calMonth.value = 0; calYear.value++; }
  if (calMonth.value < 0) { calMonth.value = 11; calYear.value--; }
}

function selectDate(cell: any) {
  const d = cell.dateStr;
  let info = "";
  if (cell.isPeriod) info = "这天是经期日";
  if (cell.isOvulation) info = "这天记录了排卵";
  if (cell.isLogged) info = "这天有记录";

  if (info) {
    uni.showToast({ title: info, icon: "none" });
  }
}

function confirmSwitchMode(modeId: string) {
  if (modeId === currentMode.value) return;
  const modeName = modes.find((m) => m.id === modeId)?.name || "";
  uni.showModal({
    title: `切换到${modeName}模式`,
    content: `确定要切换到${modeName}模式吗？页面内容将随之改变。`,
    success: (res) => {
      if (res.confirm) {
        currentMode.value = modeId;
        uni.setStorageSync("appMode", modeId);
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
    uni.setStorageSync("period_history", JSON.stringify(history.value));
  } catch {}

  // 加载其他数据
  const username = uni.getStorageSync("username") || "";
  ovulationDays.value = new Set(JSON.parse(uni.getStorageSync(`ovulation_days_${username}`) || "[]"));
  checkups.value = JSON.parse(uni.getStorageSync(`checkups_${username}`) || "[]");
  growthRecords.value = JSON.parse(uni.getStorageSync(`growth_${username}`) || "[]");
  vaccines.value = JSON.parse(uni.getStorageSync(`vaccines_${username}`) || "[]");
  babyName.value = uni.getStorageSync("baby_name") || "";
  babyBirthday.value = uni.getStorageSync("baby_birthday") || "";
  babyGender.value = uni.getStorageSync("baby_gender") || "";
  babyAvatar.value = uni.getStorageSync("baby_avatar") || "";
  dueDate.value = uni.getStorageSync("due_date") || "";
  lastPeriod.value = uni.getStorageSync("last_period_date") || "";
  const savedMilestones = uni.getStorageSync(`milestones_${username}`);
  if (savedMilestones) {
    try { milestones.value = JSON.parse(savedMilestones); } catch {}
  }
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
  todayMucus.value = uni.getStorageSync(`${prefix}_mucus`) || "";
  todayIntimacy.value = uni.getStorageSync(`${prefix}_intimacy`) === "true";
  kickCount.value = parseInt(uni.getStorageSync(`${prefix}_kick`) || "0");

  // 恢复保存状态
  flowSaved.value = !!todayFlow.value;
  colorSaved.value = !!todayColor.value;
  symptomsSaved.value = todaySymptoms.value.length > 0;
  tempSaved.value = !!todayTemp.value;
  waterSaved.value = waterCount.value > 0;
  weightSaved.value = !!todayWeight.value;
  todayMood.value = uni.getStorageSync(`${prefix}_mood`) || "";
  const pregSymp = uni.getStorageSync(`${prefix}_preg_symptoms`);
  todayPregSymptoms.value = pregSymp ? JSON.parse(pregSymp) : [];
  todayFeed.value = uni.getStorageSync(`${prefix}_feed`) || "";
  todayMilk.value = parseInt(uni.getStorageSync(`${prefix}_milk`) || "0");
  todaySleep.value = uni.getStorageSync(`${prefix}_sleep`) || "";
  nightWakes.value = uni.getStorageSync(`${prefix}_night_wakes`) || "";
  sleepTotal.value = uni.getStorageSync(`${prefix}_sleep_total`) || "0";
  const foods = uni.getStorageSync(`${prefix}_foods`);
  todayFoods.value = foods ? JSON.parse(foods) : [];
  // Load supplements
  const supp = uni.getStorageSync(`${prefix}_supplements`);
  if (supp) {
    try {
      const arr = JSON.parse(supp);
      supplements.value.forEach((s, i) => { s.taken = arr.includes(s.name); });
    } catch {}
  }
  // Logged days
  const logged = uni.getStorageSync(`logged_days_${username}`);
  loggedDays.value = logged ? new Set(JSON.parse(logged)) : new Set();

  // 从后端拉取今日数据（覆盖本地）
  syncFromServer(dateStr);
}

async function syncFromServer(dateStr: string) {
  const token = uni.getStorageSync("token");
  if (!token) return;
  try {
    const resp = await new Promise<any>((resolve, reject) => {
      uni.request({
        url: `http://127.0.0.1:8000/daily/log/${dateStr}`,
        method: "GET",
        header: { "Authorization": `Bearer ${token}` },
        success: (res) => resolve(res),
        fail: reject,
      });
    });
    if (resp.statusCode === 200 && resp.data) {
      const d = resp.data;
      if (d.flow) { todayFlow.value = d.flow; flowSaved.value = true; }
      if (d.color) { todayColor.value = d.color; colorSaved.value = true; }
      if (d.symptoms && d.symptoms.length > 0) { todaySymptoms.value = d.symptoms; symptomsSaved.value = true; }
      if (d.temperature) { todayTemp.value = String(d.temperature); tempSaved.value = true; }
      if (d.water > 0) { waterCount.value = d.water; waterSaved.value = true; }
      if (d.weight) { todayWeight.value = String(d.weight); weightSaved.value = true; }
      // 同步到本地
      const username = uni.getStorageSync("username") || "";
      const prefix = `daily_${username}_${dateStr}`;
      uni.setStorageSync(`${prefix}_flow`, todayFlow.value);
      uni.setStorageSync(`${prefix}_color`, todayColor.value);
      uni.setStorageSync(`${prefix}_symptoms`, JSON.stringify(todaySymptoms.value));
      uni.setStorageSync(`${prefix}_temp`, todayTemp.value);
      uni.setStorageSync(`${prefix}_water`, String(waterCount.value));
      uni.setStorageSync(`${prefix}_weight`, todayWeight.value);
    }
  } catch (e) {
    console.log("syncFromServer failed:", e);
  }
}

function saveDailyField(field: string, value: any) {
  const dateStr = new Date().toISOString().split("T")[0];
  const username = uni.getStorageSync("username") || "";
  const prefix = `daily_${username}_${dateStr}`;
  uni.setStorageSync(`${prefix}_${field}`, typeof value === "object" ? JSON.stringify(value) : String(value));
  const logged = new Set(loggedDays.value);
  logged.add(dateStr);
  loggedDays.value = logged;
  uni.setStorageSync(`logged_days_${username}`, JSON.stringify(Array.from(logged)));

  // 异步同步到后端
  syncToServer(dateStr);
}

function syncToServer(dateStr: string) {
  const token = uni.getStorageSync("token");
  if (!token) return;
  const username = uni.getStorageSync("username") || "";
  const prefix = `daily_${username}_${dateStr}`;

  const symptoms = uni.getStorageSync(`${prefix}_symptoms`);
  const data = {
    log_date: dateStr,
    flow: uni.getStorageSync(`${prefix}_flow`) || null,
    color: uni.getStorageSync(`${prefix}_color`) || null,
    symptoms: symptoms ? JSON.parse(symptoms) : null,
    temperature: parseFloat(uni.getStorageSync(`${prefix}_temp`)) || null,
    water: parseInt(uni.getStorageSync(`${prefix}_water`)) || 0,
    weight: parseFloat(uni.getStorageSync(`${prefix}_weight`)) || null,
  };

  uni.request({
    url: "http://127.0.0.1:8000/daily/log",
    method: "POST",
    header: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    data,
    fail: (err) => {
      console.log("syncToServer failed:", err);
    },
  });
}

// 经期操作
function setFlow(f: string) {
  if (flowSaved.value) {
    confirmChange('flow', () => setFlow(f));
    return;
  }
  todayFlow.value = todayFlow.value === f ? "" : f;
  saveDailyField("flow", todayFlow.value);
  if (todayFlow.value) {
    flowSaved.value = true;
    uni.showToast({ title: "已保存", icon: "success", duration: 1000 });
  }
}

function setColor(c: string) {
  if (colorSaved.value) {
    confirmChange('color', () => setColor(c));
    return;
  }
  todayColor.value = todayColor.value === c ? "" : c;
  saveDailyField("color", todayColor.value);
  if (todayColor.value) {
    colorSaved.value = true;
    uni.showToast({ title: "已保存", icon: "success", duration: 1000 });
  }
}

function toggleSymptom(s: string) {
  if (symptomsSaved.value) {
    confirmChange('symptoms', () => toggleSymptom(s));
    return;
  }
  const idx = todaySymptoms.value.indexOf(s);
  if (idx >= 0) todaySymptoms.value.splice(idx, 1);
  else todaySymptoms.value.push(s);
  saveDailyField("symptoms", todaySymptoms.value);
  if (todaySymptoms.value.length > 0) {
    symptomsSaved.value = true;
    uni.showToast({ title: "已保存", icon: "success", duration: 1000 });
  }
}
function saveTemp() {
  if (tempSaved.value) {
    confirmChange('temp', () => saveTemp());
    return;
  }
  if (!todayTemp.value) return;
  saveDailyField("temp", todayTemp.value);
  tempSaved.value = true;
  uni.showToast({ title: `${todayTemp.value}°C 已保存`, icon: "none" });
}
function toggleWater(n: number) {
  if (waterSaved.value) {
    confirmChange('water', () => toggleWater(n));
    return;
  }
  waterCount.value = n === waterCount.value ? n - 1 : n;
  saveDailyField("water", waterCount.value);
  if (waterCount.value > 0) {
    waterSaved.value = true;
    uni.showToast({ title: "已保存", icon: "success", duration: 1000 });
  }
}
function saveWeight() {
  if (weightSaved.value) {
    confirmChange('weight', () => saveWeight());
    return;
  }
  if (!todayWeight.value) return;
  saveDailyField("weight", todayWeight.value);
  weightSaved.value = true;
  uni.showToast({ title: `${todayWeight.value}kg 已保存`, icon: "none" });
}

// 备孕操作
function setOvulation(o: string) {
  todayOvulation.value = todayOvulation.value === o ? "" : o;
  saveDailyField("ovulation", todayOvulation.value);
  if (todayOvulation.value) {
    const dateStr = new Date().toISOString().split("T")[0];
    const username = uni.getStorageSync("username") || "";
    const days = new Set(ovulationDays.value);
    days.add(dateStr);
    ovulationDays.value = days;
    uni.setStorageSync(`ovulation_days_${username}`, JSON.stringify(Array.from(days)));
  }
  // 记录备孕开始日
  if (!uni.getStorageSync("pregnancy_start")) {
    uni.setStorageSync("pregnancy_start", new Date().toISOString().split("T")[0]);
  }
}
function setMucus(m: string) { todayMucus.value = todayMucus.value === m ? "" : m; saveDailyField("mucus", todayMucus.value); }
function toggleIntimacy() {
  todayIntimacy.value = !todayIntimacy.value;
  saveDailyField("intimacy", todayIntimacy.value);
  if (todayIntimacy.value) {
    const username = uni.getStorageSync("username") || "";
    const count = parseInt(uni.getStorageSync(`intimacy_count_${username}`) || "0") + 1;
    uni.setStorageSync(`intimacy_count_${username}`, String(count));
  }
  uni.showToast({ title: todayIntimacy.value ? "已记录" : "已取消", icon: "none" });
}
function toggleSupplement(name: string) {
  const s = supplements.value.find((x) => x.name === name);
  if (s) {
    s.taken = !s.taken;
    const taken = supplements.value.filter((x) => x.taken).map((x) => x.name);
    saveDailyField("supplements", taken);
  }
}

// 怀孕操作
function onDueDateChange(e: any) { dueDate.value = e.detail.value; uni.setStorageSync("due_date", dueDate.value); uni.showToast({ title: "预产期已设置", icon: "success" }); }
function onLastPeriodChange(e: any) { lastPeriod.value = e.detail.value; uni.setStorageSync("last_period_date", lastPeriod.value); uni.showToast({ title: "末次月经已设置", icon: "success" }); }
function addKick() {
  kickCount.value++;
  saveDailyField("kick", kickCount.value);
  if (kickCount.value >= 3 && kickCount.value <= 5) {
    uni.showToast({ title: "胎动正常 ✓", icon: "none" });
  } else if (kickCount.value > 5) {
    uni.showToast({ title: `${kickCount.value}次`, icon: "none" });
  }
}
function togglePregSymptom(s: string) {
  const idx = todayPregSymptoms.value.indexOf(s);
  if (idx >= 0) todayPregSymptoms.value.splice(idx, 1);
  else todayPregSymptoms.value.push(s);
  saveDailyField("preg_symptoms", todayPregSymptoms.value);
}
function setMood(m: string) { todayMood.value = todayMood.value === m ? "" : m; saveDailyField("mood", todayMood.value); }
function addCheckup() {
  uni.showModal({
    title: "添加产检记录",
    editable: true,
    placeholderText: `${pregWeekNum.value}周 - 输入检查内容和结果`,
    success: (res) => {
      if (res.confirm && res.content) {
        const username = uni.getStorageSync("username") || "";
        const list = JSON.parse(uni.getStorageSync(`checkups_${username}`) || "[]");
        list.unshift({ date: new Date().toISOString().split("T")[0], week: pregWeekNum.value, content: res.content, result: "normal", resultText: "正常" });
        checkups.value = list;
        uni.setStorageSync(`checkups_${username}`, JSON.stringify(list));
        uni.showToast({ title: "已保存", icon: "success" });
      }
    },
  });
}

// 育儿操作
function setBabyName() {
  uni.showModal({
    title: "宝宝昵称",
    editable: true,
    placeholderText: "输入宝宝昵称",
    success: (res) => {
      if (res.confirm && res.content) {
        babyName.value = res.content;
        uni.setStorageSync("baby_name", res.content);
      }
    },
  });
}
function setBabyBirthday() {
  uni.showModal({
    title: "出生日期",
    editable: true,
    placeholderText: "格式: 2025-01-15",
    success: (res) => {
      if (res.confirm && res.content) {
        babyBirthday.value = res.content;
        uni.setStorageSync("baby_birthday", res.content);
      }
    },
  });
}
function setBabyGender() {
  uni.showActionSheet({
    itemList: ["男宝 👦", "女宝 👧"],
    success: (res) => {
      babyGender.value = res.tapIndex === 0 ? "男宝" : "女宝";
      uni.setStorageSync("baby_gender", babyGender.value);
    },
  });
}
function chooseBabyAvatar() {
  uni.chooseImage({
    count: 1,
    sizeType: ["compressed"],
    success: (res) => {
      babyAvatar.value = res.tempFilePaths[0];
      uni.setStorageSync("baby_avatar", babyAvatar.value);
    },
  });
}
function setFeed(f: string) { todayFeed.value = todayFeed.value === f ? "" : f; saveDailyField("feed", todayFeed.value); }
function addMilk(amount: number) {
  todayMilk.value = Math.max(0, todayMilk.value + amount);
  saveDailyField("milk", todayMilk.value);
}
function setSleep(s: string) { todaySleep.value = todaySleep.value === s ? "" : s; saveDailyField("sleep", todaySleep.value); }
function saveNightWakes() { saveDailyField("night_wakes", nightWakes.value); }
function toggleFood(f: string) {
  const idx = todayFoods.value.indexOf(f);
  if (idx >= 0) todayFoods.value.splice(idx, 1);
  else todayFoods.value.push(f);
  saveDailyField("foods", todayFoods.value);
}
function addGrowth() {
  uni.showModal({
    title: "记录生长数据",
    editable: true,
    placeholderText: "身高cm,体重kg (如: 65,7.5)",
    success: (res) => {
      if (res.confirm && res.content) {
        const parts = res.content.split(",").map((s: string) => s.trim());
        const username = uni.getStorageSync("username") || "";
        const list = JSON.parse(uni.getStorageSync(`growth_${username}`) || "[]");
        list.unshift({ date: new Date().toISOString().split("T")[0], height: parts[0] || "", weight: parts[1] || "", head: parts[2] || "" });
        growthRecords.value = list;
        uni.setStorageSync(`growth_${username}`, JSON.stringify(list));
        uni.showToast({ title: "已保存", icon: "success" });
      }
    },
  });
}
function addVaccine() {
  uni.showModal({
    title: "记录疫苗接种",
    editable: true,
    placeholderText: "输入疫苗名称",
    success: (res) => {
      if (res.confirm && res.content) {
        const username = uni.getStorageSync("username") || "";
        const list = JSON.parse(uni.getStorageSync(`vaccines_${username}`) || "[]");
        list.unshift({ name: res.content, date: new Date().toISOString().split("T")[0], done: true });
        vaccines.value = list;
        uni.setStorageSync(`vaccines_${username}`, JSON.stringify(list));
        uni.showToast({ title: "已记录", icon: "success" });
      }
    },
  });
}
function toggleMilestone(i: number) {
  const m = milestones.value[i];
  if (m.done) {
    m.done = false;
    m.date = "";
  } else {
    m.done = true;
    m.date = new Date().toISOString().split("T")[0];
    uni.showToast({ title: `恭喜！${m.name} 达成！`, icon: "success" });
  }
  const username = uni.getStorageSync("username") || "";
  uni.setStorageSync(`milestones_${username}`, JSON.stringify(milestones.value));
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
          if (h.id) await api({ url: `/period/record/${h.id}`, method: "DELETE" }).catch(() => {});
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
.header { padding: 88rpx 32rpx 20rpx; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); }
.header-title { font-size: 38rpx; font-weight: 600; color: #fff; display: block; margin-bottom: 16rpx; }
.mode-row { display: flex; gap: 10rpx; }
.mode-btn { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4rpx; padding: 12rpx 8rpx; border-radius: 16rpx; background: rgba(255,255,255,0.12); }
.mode-btn.active { background: rgba(255,255,255,0.3); }
.mode-icon { font-size: 28rpx; }
.mode-name { font-size: 22rpx; color: rgba(255,255,255,0.8); }
.mode-btn.active .mode-name { color: #fff; font-weight: 500; }

.status-card { display: flex; align-items: center; background: #fff; border-radius: 24rpx; padding: 36rpx 32rpx; margin: -16rpx 24rpx 24rpx; box-shadow: 0 8rpx 32rpx rgba(232,131,124,0.12); }
.status-circle { width: 130rpx; height: 130rpx; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 24rpx; }
.status-circle.period { background: linear-gradient(135deg, #fce4ec, #f8bbd0); }
.status-circle.pregnancy { background: linear-gradient(135deg, #fff3e0, #ffe0b2); }
.status-circle.baby { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); }
.status-circle.parenting { background: linear-gradient(135deg, #e3f2fd, #bbdefb); }
.cycle-day { font-size: 44rpx; font-weight: 700; color: var(--primary-dark); line-height: 1; }
.cycle-label { font-size: 20rpx; color: var(--primary); }
.status-info { flex: 1; }
.status-phase { font-size: 30rpx; font-weight: 600; color: #333; display: block; margin-bottom: 6rpx; }
.status-next { font-size: 24rpx; color: #999; }

.card { background: #fff; border-radius: 24rpx; padding: 28rpx; margin: 0 24rpx 20rpx; box-shadow: 0 2rpx 12rpx rgba(232,131,124,0.05); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
.card-title { font-size: 30rpx; font-weight: 600; color: #333; }
.card-date { font-size: 24rpx; color: #bbb; }

/* Calendar */
.cal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.cal-nav { font-size: 36rpx; color: var(--primary); padding: 8rpx 20rpx; }
.cal-title { font-size: 28rpx; font-weight: 600; color: #333; }
.cal-weekdays { display: flex; margin-bottom: 8rpx; }
.cal-weekday { flex: 1; text-align: center; font-size: 22rpx; color: #bbb; }
.cal-grid { display: flex; flex-wrap: wrap; }
.cal-cell { width: 14.28%; height: 72rpx; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; }
.cal-cell.empty { pointer-events: none; }
.cal-day { font-size: 26rpx; color: #333; }
.cal-cell.today .cal-day { color: var(--primary); font-weight: 700; }
.cal-cell.period { background: rgba(232,131,124,0.12); border-radius: 8rpx; }
.cal-cell.predicted { background: rgba(232,131,124,0.06); border-radius: 8rpx; }
.cal-cell.logged { border-bottom: 3rpx solid #4caf50; }
.cal-cell.ovulation { background: rgba(255,152,0,0.12); border-radius: 8rpx; }
.cal-dot { width: 8rpx; height: 8rpx; border-radius: 50%; background: var(--primary); margin-top: 2rpx; }
.cal-dot.ov-dot { background: #ff9800; }
.cal-legend { display: flex; gap: 20rpx; margin-top: 16rpx; justify-content: center; }
.legend-item { display: flex; align-items: center; gap: 6rpx; }
.legend-dot { width: 14rpx; height: 14rpx; border-radius: 4rpx; }
.legend-dot.period { background: rgba(232,131,124,0.3); }
.legend-dot.predicted { background: rgba(232,131,124,0.1); border: 1rpx dashed var(--primary); }
.legend-dot.logged { background: #4caf50; }
.legend-dot.ov-dot { background: #ff9800; }
.legend-dot.checkup { background: #66bb6a; }
.legend-text { font-size: 22rpx; color: #999; }

.action-row { display: flex; gap: 16rpx; padding: 0 24rpx 20rpx; }
.action-btn { flex: 1; border: none; border-radius: 20rpx; padding: 24rpx; font-size: 28rpx; }
.action-btn.primary { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); }
.btn-text { color: #fff; }
.action-btn.secondary { background: #fff; border: 2rpx solid var(--primary-border); }
.btn-text2 { color: var(--primary); }

.track-section { margin-bottom: 24rpx; }
.track-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12rpx; }
.track-label { font-size: 26rpx; color: #666; }
.saved-tag { font-size: 22rpx; color: #4caf50; font-weight: 500; }
.track-options { display: flex; flex-wrap: wrap; gap: 12rpx; }
.track-opt { padding: 12rpx 24rpx; border-radius: 24rpx; font-size: 24rpx; background: #f8f0f0; color: #999; }
.track-opt.active { background: var(--primary-light); color: var(--primary); font-weight: 500; border: 1rpx solid var(--primary-border); }
.track-opt.locked { opacity: 0.5; }
.water-cup.locked { opacity: 0.6; }
.color-opt { display: flex; align-items: center; gap: 8rpx; }
.color-circle { width: 20rpx; height: 20rpx; border-radius: 50%; }
.color-name { font-size: 24rpx; }
.symptom-options { gap: 10rpx; }
.temp-row { display: flex; align-items: center; gap: 12rpx; }
.temp-input { width: 200rpx; background: #f8f0f0; border-radius: 16rpx; padding: 14rpx 20rpx; font-size: 28rpx; text-align: center; }
.temp-unit { font-size: 28rpx; color: #999; }
.temp-hint { font-size: 22rpx; color: #bbb; margin-top: 8rpx; display: block; }
.water-row { display: flex; gap: 8rpx; flex-wrap: wrap; }
.water-cup { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; border-radius: 12rpx; background: #f8f0f0; font-size: 28rpx; }
.water-cup.filled { background: #e3f2fd; }
.cup-icon { font-size: 28rpx; }
.water-info { font-size: 22rpx; color: #999; margin-top: 8rpx; }

/* 备孕 */
.progress-grid { display: flex; justify-content: space-around; }
.progress-item { display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.progress-num { font-size: 40rpx; font-weight: 700; color: var(--primary); }
.progress-label { font-size: 22rpx; color: #999; }
.ov-opt { display: flex; align-items: center; gap: 6rpx; }
.ov-dot-icon { font-size: 24rpx; }
.intimacy-row { display: flex; align-items: center; gap: 16rpx; padding: 16rpx; background: #f8f0f0; border-radius: 16rpx; }
.intimacy-check { width: 40rpx; height: 40rpx; border-radius: 50%; border: 2rpx solid #ddd; display: flex; align-items: center; justify-content: center; font-size: 24rpx; color: #fff; }
.intimacy-check.checked { background: var(--primary); border-color: var(--primary); }
.intimacy-text { font-size: 28rpx; color: #666; }
.supplement-list { display: flex; flex-direction: column; gap: 12rpx; }
.supplement-item { display: flex; align-items: center; padding: 16rpx; background: #fef7f6; border-radius: 16rpx; gap: 16rpx; }
.supp-check { width: 36rpx; height: 36rpx; border-radius: 50%; border: 2rpx solid #ddd; display: flex; align-items: center; justify-content: center; font-size: 20rpx; color: #fff; }
.supp-check.checked { background: #4caf50; border-color: #4caf50; }
.supp-info { flex: 1; }
.supp-name { font-size: 28rpx; color: #333; display: block; }
.supp-dose { font-size: 22rpx; color: #999; }
.supp-status { font-size: 22rpx; color: #999; }

/* 怀孕 */
.preg-info-row { display: flex; gap: 20rpx; }
.preg-field { flex: 1; background: #fef7f6; border-radius: 16rpx; padding: 16rpx; display: flex; flex-direction: column; gap: 8rpx; }
.preg-label { font-size: 22rpx; color: #999; }
.preg-value { font-size: 28rpx; color: var(--primary); font-weight: 500; }
.baby-info { text-align: center; padding: 20rpx 0; }
.baby-fruit { font-size: 80rpx; display: block; margin-bottom: 12rpx; }
.baby-size { font-size: 28rpx; color: #333; display: block; margin-bottom: 8rpx; }
.baby-desc { font-size: 24rpx; color: #999; display: block; }
.checkup-item { display: flex; justify-content: space-between; padding: 16rpx 0; border-bottom: 1rpx solid #f8f0f0; }
.checkup-left { display: flex; flex-direction: column; gap: 4rpx; }
.checkup-date { font-size: 26rpx; color: #333; }
.checkup-week { font-size: 22rpx; color: #bbb; }
.checkup-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4rpx; }
.checkup-content { font-size: 26rpx; color: #666; }
.checkup-result { font-size: 22rpx; padding: 4rpx 12rpx; border-radius: 8rpx; }
.checkup-result.normal { background: #e8f5e9; color: #4caf50; }
.next-checkup { display: flex; justify-content: space-between; padding: 16rpx; background: var(--primary-light); border-radius: 12rpx; margin-top: 16rpx; }
.next-label { font-size: 24rpx; color: #999; }
.next-date { font-size: 24rpx; color: var(--primary); font-weight: 500; }
.kick-row { display: flex; align-items: center; gap: 20rpx; }
.kick-btn { width: 120rpx; height: 120rpx; border-radius: 50%; background: linear-gradient(135deg, #fce4ec, #f8bbd0); display: flex; flex-direction: column; align-items: center; justify-content: center; }
.kick-num { font-size: 40rpx; font-weight: 700; color: var(--primary-dark); }
.kick-label { font-size: 20rpx; color: #999; }
.kick-hint { font-size: 24rpx; color: #999; }
.add-btn { background: var(--primary-light); padding: 8rpx 20rpx; border-radius: 16rpx; }
.add-btn-text { font-size: 24rpx; color: var(--primary); }
.empty-section { text-align: center; padding: 32rpx; }
.empty-text { font-size: 26rpx; color: #ccc; }

/* 育儿 */
.baby-profile { display: flex; align-items: center; gap: 24rpx; margin-bottom: 20rpx; }
.baby-avatar-edit { display: flex; flex-direction: column; align-items: center; gap: 4rpx; }
.baby-avatar-img { width: 100rpx; height: 100rpx; border-radius: 50%; border: 3rpx solid var(--primary-border); }
.baby-avatar-edit-text { font-size: 20rpx; color: #999; }
.baby-detail { flex: 1; }
.baby-name { font-size: 32rpx; font-weight: 600; color: #333; display: block; }
.baby-age { font-size: 24rpx; color: #999; display: block; margin-top: 4rpx; }
.baby-age-days { font-size: 24rpx; color: var(--primary); display: block; margin-top: 4rpx; }
.baby-set-row { display: flex; gap: 12rpx; }
.baby-set-item { flex: 1; background: #fef7f6; border-radius: 12rpx; padding: 12rpx; display: flex; flex-direction: column; align-items: center; gap: 4rpx; }
.baby-set-label { font-size: 22rpx; color: #999; }
.baby-set-val { font-size: 24rpx; color: var(--primary); }
.milk-row { display: flex; align-items: center; gap: 20rpx; }
.milk-btn { background: #f8f0f0; border-radius: 12rpx; padding: 12rpx 24rpx; }
.milk-btn-text { font-size: 28rpx; color: var(--primary); font-weight: 500; }
.milk-display { display: flex; align-items: baseline; gap: 4rpx; }
.milk-num { font-size: 44rpx; font-weight: 700; color: #333; }
.milk-unit { font-size: 24rpx; color: #999; }
.sleep-summary { margin-bottom: 16rpx; }
.sleep-total { font-size: 28rpx; color: var(--primary); font-weight: 500; }
.growth-item { display: flex; justify-content: space-between; padding: 14rpx 0; border-bottom: 1rpx solid #f8f0f0; }
.growth-date { font-size: 26rpx; color: #333; }
.growth-data { display: flex; gap: 16rpx; }
.growth-val { font-size: 24rpx; color: #666; }
.vaccine-item { display: flex; justify-content: space-between; align-items: center; padding: 14rpx 0; border-bottom: 1rpx solid #f8f0f0; }
.vaccine-left { display: flex; flex-direction: column; gap: 4rpx; }
.vaccine-name { font-size: 28rpx; color: #333; }
.vaccine-date { font-size: 22rpx; color: #bbb; }
.vaccine-status { font-size: 24rpx; color: #999; }
.vaccine-status.done { color: #4caf50; }
.milestone-list { display: flex; flex-direction: column; gap: 12rpx; }
.milestone-item { display: flex; align-items: center; gap: 16rpx; padding: 12rpx; background: #fef7f6; border-radius: 12rpx; }
.milestone-check { width: 36rpx; height: 36rpx; border-radius: 50%; border: 2rpx solid #ddd; display: flex; align-items: center; justify-content: center; font-size: 20rpx; color: #fff; flex-shrink: 0; }
.milestone-check.checked { background: #4caf50; border-color: #4caf50; }
.milestone-info { flex: 1; }
.milestone-name { font-size: 28rpx; color: #333; display: block; }
.milestone-age { font-size: 22rpx; color: #999; }

/* History */
.empty-history { text-align: center; padding: 32rpx; }
.history-item { display: flex; justify-content: space-between; align-items: center; padding: 18rpx 0; border-bottom: 1rpx solid #f8f0f0; }
.history-item:last-child { border-bottom: none; }
.history-left { display: flex; flex-direction: column; }
.history-date { font-size: 28rpx; color: #333; font-weight: 500; }
.history-end { font-size: 22rpx; color: #bbb; margin-top: 4rpx; }
.history-right { display: flex; align-items: center; gap: 12rpx; }
.history-dur { font-size: 26rpx; color: #666; }
.history-status { font-size: 22rpx; color: #999; background: #f8f0f0; padding: 4rpx 12rpx; border-radius: 12rpx; }
.history-status.active { color: var(--primary); background: var(--primary-light); }
.delete-btn { width: 44rpx; height: 44rpx; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: var(--primary-light); }
.delete-icon { color: var(--primary); font-size: 28rpx; }
</style>
