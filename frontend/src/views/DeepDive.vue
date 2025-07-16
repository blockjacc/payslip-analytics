<template>
  <BaseLayout>
    <div class="deep-dive-container">
      <div class="bg-white/10 rounded-xl p-8 w-full max-w-2xl text-center mx-auto mb-8">
        <h3 class="text-primary mb-6 text-2xl">company: {{ companyName }}</h3>
        <div v-if="!selectedEmployee">
          <EmployeeSearch
            :company-id="companyId"
            context="all"
            placeholder="first or last name"
            @employee-selected="onEmployeeSelected"
            @error="handleSearchError"
          />
          <div v-if="error" class="text-red-400 text-sm mt-2">{{ error }}</div>
        </div>
        <div v-else-if="!selectedDate">
          <div class="mb-6 text-lg text-primary font-semibold">selected employee: <span class="text-white">{{ selectedEmployee.first_name }} {{ selectedEmployee.last_name }}</span></div>
          <div class="mb-6">
            <label class="block mb-2 text-secondary text-sm">select date to examine:</label>
            <DatePicker v-model:value="selectedDate" type="date" format="YYYY-MM-DD" value-type="format" :editable="false" :input-class="'w-full h-12 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition'" placeholder="Select date" />
          </div>
        </div>
        <div v-else>
          <div class="mb-6 text-lg text-primary font-semibold">selected employee: <span class="text-white">{{ selectedEmployee.first_name }} {{ selectedEmployee.last_name }}</span></div>
          <div class="mb-6 text-lg text-primary font-semibold">date: <span class="text-white">{{ formatDate(selectedDate) }}</span></div>
        </div>
      </div>
      <div v-if="selectedEmployee && selectedDate">
        <h1 class="page-title mb-8">
          Employee Deep Dive – {{ formatDate(selectedDate) }}
          <span v-if="shiftName">– {{ shiftName }}</span>
        </h1>
        <div v-if="shiftName" class="text-primary text-lg mb-4 text-center font-semibold">Shift: {{ shiftName }}</div>
        <div class="tab-bar">
          <button :class="{active: tab==='pay'}" @click="tab='pay'">Pay</button>
          <button :class="{active: tab==='attendance'}" @click="tab='attendance'">Attendance</button>
          <button :class="{active: tab==='settings'}" @click="tab='settings'">Settings</button>
        </div>
        <div v-if="tab==='pay'" class="tab-content">
          <div class="text-center text-gray-400 py-8">Pay details coming soon.</div>
        </div>
        <div v-if="tab==='attendance'" class="tab-content">
          <div v-if="attendanceLoading">Loading attendance...</div>
          <div v-else-if="attendanceError">{{ attendanceError }}</div>
          <div v-else-if="attendanceData && attendanceData.length">
            <div v-for="(record, idx) in attendanceData" :key="idx" class="bg-slate-800/50 rounded-lg p-6 mb-6">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div v-for="(value, key) in filteredFields(record)" :key="key" class="space-y-1">
                  <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                  <div class="text-white font-medium">{{ formatFieldValue(value) }}</div>
                </div>
              </div>
            </div>
          </div>
          <div v-else>No attendance data found.</div>
        </div>
        <div v-if="tab==='settings'" class="tab-content">
          <div v-if="settingsLoading">Loading settings...</div>
          <div v-else-if="settingsError">{{ settingsError }}</div>
          <div v-else-if="settingsData">
            <div v-for="(section, sectionKey) in settingsSections" :key="sectionKey">
              <template v-if="section.key !== 'shift_summary'">
                <h2 class="section-title text-xl font-semibold text-emerald-400 mb-4">{{ section.label }}</h2>
                <div v-if="Array.isArray(settingsData[section.key])">
                  <div v-for="(item, idx) in settingsData[section.key]" :key="idx" class="bg-slate-800/50 rounded-lg p-6 mb-6">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div v-for="(value, key) in filteredFields(item)" :key="key" class="space-y-1">
                        <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                        <div class="text-white font-medium">{{ formatFieldValue(value) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else-if="settingsData[section.key] && typeof settingsData[section.key] === 'object'">
                  <div class="bg-slate-800/50 rounded-lg p-6 mb-6">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div v-for="(value, key) in filteredFields(settingsData[section.key])" :key="key" class="space-y-1">
                        <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                        <div class="text-white font-medium">{{ formatFieldValue(value) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </div>
            <div v-if="settingsSections.filter(s => s.key !== 'shift_summary').length === 0">No settings data found.</div>
          </div>
          <div v-else>No settings data found.</div>
        </div>
      </div>
    </div>
  </BaseLayout>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BaseLayout from '../components/layouts/BaseLayout.vue';
import EmployeeSearch from '../components/EmployeeSearch.vue';
import DatePicker from 'vue-datepicker-next';
import 'vue-datepicker-next/index.css';

const tab = ref('pay');
const route = useRoute();
const router = useRouter();
const companyId = route.params.company_id;
const empId = route.params.emp_id;
const date = route.params.date;

// Attendance
const attendanceData = ref([]);
const attendanceLoading = ref(false);
const attendanceError = ref('');

// Settings
const settingsData = ref(null);
const settingsLoading = ref(false);
const settingsError = ref('');

// For settings, define the sections to display
const settingsSections = [
  { key: 'shift_summary', label: 'Shift Summary' },
  { key: 'work_schedule', label: 'Work Schedule Configuration' },
  { key: 'regular_schedule', label: 'Regular Schedule' },
  { key: 'flexible_hours', label: 'Flexible Hours' },
  { key: 'rest_days', label: 'Rest Days' },
];

const selectedEmployee = ref(null);
const error = ref(null);
const companyName = computed(() => sessionStorage.getItem('selectedCompanyName') || '');
const selectedDate = ref('');

// In the script setup, add a computed property for shiftName:
const shiftName = computed(() => {
  if (settingsData.value && settingsData.value.shift_summary && settingsData.value.shift_summary.shift_name) {
    return settingsData.value.shift_summary.shift_name;
  }
  return '';
});

function filteredFields(obj) {
  // Only show fields with non-null, non-empty, non-'N/A' values
  return Object.fromEntries(
    Object.entries(obj).filter(
      ([, value]) => value !== null && value !== '' && value !== 'N/A' && value !== undefined
    )
  );
}

function formatFieldName(fieldName) {
  return fieldName.replace(/_/g, ' ').toLowerCase();
}
function formatFieldValue(value) {
  if (value === null || value === undefined || value === '') {
    return 'N/A';
  }
  if (typeof value === 'boolean') {
    return value ? 'Enabled' : 'Disabled';
  }
  if (typeof value === 'string' && (value === 'yes' || value === 'no')) {
    return value === 'yes' ? 'Enabled' : 'Disabled';
  }
  return value.toString();
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

async function fetchAttendance() {
  if (!selectedEmployee.value || !selectedDate.value) return;
  attendanceLoading.value = true;
  attendanceError.value = '';
  try {
    const res = await fetch(`/api/deepdive/timekeeping/${companyId}/${selectedEmployee.value.emp_id}/${selectedDate.value}`);
    const json = await res.json();
    attendanceData.value = json.data || [];
  } catch (e) {
    attendanceError.value = 'Failed to load attendance data.';
  } finally {
    attendanceLoading.value = false;
  }
}

async function fetchSettings() {
  if (!selectedEmployee.value || !selectedDate.value) return;
  settingsLoading.value = true;
  settingsError.value = '';
  try {
    const res = await fetch(`/api/deepdive/shifts/${companyId}/${selectedEmployee.value.emp_id}/${selectedDate.value}`);
    const json = await res.json();
    if (json.data && json.data.length && json.data[0].work_schedule_id) {
      const shiftId = json.data[0].work_schedule_id;
      const settingsRes = await fetch(`/api/shift-details/${companyId}/${shiftId}`);
      settingsData.value = await settingsRes.json();
    } else {
      settingsData.value = null;
    }
  } catch (e) {
    settingsError.value = 'Failed to load settings data.';
  } finally {
    settingsLoading.value = false;
  }
}

function onEmployeeSelected(employee) {
  selectedEmployee.value = employee;
  error.value = null;
  // Fetch data for tabs here if needed
}

function handleSearchError(msg) {
  error.value = msg;
}

function resetEmployee() {
  selectedEmployee.value = null;
  error.value = null;
  // Optionally reset tab data
}

watch([selectedEmployee, selectedDate], ([emp, date]) => {
  if (emp && date) {
    fetchAttendance();
    fetchSettings();
  }
});

onMounted(() => {
  // Initial fetch might happen on mount if empId and date are already in route
  // or if they are set by the user before the component mounts.
  // The watch will handle the actual fetching when emp and date are available.
});
</script>

<style scoped>
.deep-dive-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1rem;
}
.page-title {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  text-align: center;
}
.tab-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
}
.tab-bar button {
  background: none;
  border: none;
  font-size: 1.1rem;
  padding: 0.5rem 1.5rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  color: #3ddad7;
  transition: border 0.2s;
}
.tab-bar button.active {
  border-bottom: 2px solid #3ddad7;
  font-weight: bold;
}
.tab-content {
  min-height: 300px;
}
.data-card {
  background: rgba(255,255,255,0.03);
  border-radius: 8px;
  margin-bottom: 1.5rem;
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.data-row {
  display: flex;
  justify-content: space-between;
  padding: 0.2rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.data-label {
  color: #aaa;
  font-size: 0.98rem;
}
.data-value {
  color: #fff;
  font-size: 1.05rem;
  font-weight: 500;
}
.section-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 1.5rem 0 0.5rem 0;
  color: #3ddad7;
}
</style> 