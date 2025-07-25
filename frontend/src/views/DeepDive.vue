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
          <button :class="{active: tab==='applications'}" @click="tab='applications'">Applications</button>
        </div>
        <div v-if="tab==='pay'" class="tab-content">
          <div class="flex gap-4 mb-4">
            <button :class="['px-4 py-2 rounded', payView==='debit' ? 'bg-primary text-white' : 'bg-white/10 text-primary']" @click="payView='debit'">Debit</button>
            <button :class="['px-4 py-2 rounded', payView==='credit' ? 'bg-primary text-white' : 'bg-white/10 text-primary']" @click="payView='credit'">Credit</button>
          </div>
          <div v-if="payLoading">Loading pay data...</div>
          <div v-else-if="payError">{{ payError }}</div>
          <div v-else-if="payData && payData.length">
            <div v-for="(record, idx) in payData" :key="idx">
              <!-- Main pay fields in horizontal grid -->
              <div class="bg-slate-800/50 rounded-lg p-6 mb-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div class="space-y-1">
                    <div class="text-xs uppercase tracking-wide text-white/50">basic pay</div>
                    <div class="text-white font-medium">{{ formatFieldValue(record.basic_pay) }}</div>
                  </div>
                  <div class="space-y-1">
                    <div class="text-xs uppercase tracking-wide text-white/50">hourly rate</div>
                    <div class="text-white font-medium">{{ formatFieldValue(record.rate) }}</div>
                  </div>
                  <div class="space-y-1">
                    <div class="text-xs uppercase tracking-wide text-white/50">hours worked</div>
                    <div class="text-white font-medium">{{ formatFieldValue(record.hours_worked) }}</div>
                  </div>
                </div>
              </div>
              
              <!-- Paycheck details in tabular format -->
              <div class="bg-slate-800/50 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-emerald-400 mb-4">paycheck details</h3>
                <div class="space-y-3">
                  <div class="flex justify-between items-center py-2 border-b border-white/10">
                    <span class="text-white/70">absences</span>
                    <span class="text-white font-medium">{{ formatFieldValue(record.absences) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-white/10">
                    <span class="text-white/70">tardiness</span>
                    <span class="text-white font-medium">{{ formatFieldValue(record.tardiness) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-white/10">
                    <span class="text-white/70">undertime</span>
                    <span class="text-white font-medium">{{ formatFieldValue(record.undertime) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-white/10">
                    <span class="text-white/70">paid/unpaid leave</span>
                    <span class="text-white font-medium">{{ formatFieldValue(record.paid_leave) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-white/10">
                    <span class="text-white/70">overtime</span>
                    <span class="text-white font-medium">{{ formatFieldValue(record.overtime) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-white/10">
                    <span class="text-white/70">restday</span>
                    <span class="text-white font-medium">{{ formatFieldValue(record.rest_day) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-white/10">
                    <span class="text-white/70">holiday</span>
                    <span class="text-white font-medium">{{ formatFieldValue(record.holiday_premium) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-white/10">
                    <span class="text-white/70">night shift differential</span>
                    <span class="text-white font-medium">{{ formatFieldValue(record.night_differential) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else>No pay data found.</div>
        </div>
        <div v-if="tab==='attendance'" class="tab-content">
          <div class="flex gap-4 mb-4">
            <button :class="['px-4 py-2 rounded', attendanceView==='filtered' ? 'bg-primary text-white' : 'bg-white/10 text-primary']" @click="attendanceView='filtered'">Filtered</button>
            <button :class="['px-4 py-2 rounded', attendanceView==='all' ? 'bg-primary text-white' : 'bg-white/10 text-primary']" @click="attendanceView='all'">All</button>
          </div>
          <div v-if="attendanceLoading">Loading attendance...</div>
          <div v-else-if="attendanceError">{{ attendanceError }}</div>
          <div v-else-if="attendanceData && attendanceData.length">
            <div v-for="(record, idx) in attendanceData" :key="idx" class="bg-slate-800/50 rounded-lg p-6 mb-6">
              <template v-for="(group, groupIdx) in getAttendanceFieldsForDisplay(record, attendanceView)" :key="groupIdx">
                <div v-if="group.length" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-2">
                  <div v-for="key in group" :key="key" class="space-y-1">
                    <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                    <div class="text-white font-medium">{{ formatFieldValue(record[key]) }}</div>
                  </div>
                </div>
                <hr v-if="group.length && groupIdx < getAttendanceFieldsForDisplay(record, attendanceView).length-1" class="my-2 border-white/30" />
              </template>
            </div>
          </div>
          <div v-else>No attendance data found.</div>
        </div>
        <div v-if="tab==='settings'" class="tab-content">
          <div class="flex gap-4 mb-4">
            <button :class="['px-4 py-2 rounded', settingsView==='filtered' ? 'bg-primary text-white' : 'bg-white/10 text-primary']" @click="settingsView='filtered'">Filtered</button>
            <button :class="['px-4 py-2 rounded', settingsView==='all' ? 'bg-primary text-white' : 'bg-white/10 text-primary']" @click="settingsView='all'">All</button>
          </div>
          <div v-if="settingsLoading">Loading settings...</div>
          <div v-else-if="settingsError">{{ settingsError }}</div>
          <div v-else-if="settingsData">
            <div v-for="(section, sectionKey) in settingsSections" :key="sectionKey">
              <template v-if="section.key !== 'shift_summary'">
                <h2 class="section-title text-xl font-semibold text-emerald-400 mb-4">{{ section.label }}</h2>
                <div v-if="Array.isArray(settingsData[section.key])">
                  <div v-for="(item, idx) in settingsData[section.key]" :key="idx" class="bg-slate-800/50 rounded-lg p-6 mb-6">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-2">
                      <div v-for="key in getSettingsFieldsForDisplay(item, settingsView)" :key="key" class="space-y-1">
                        <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                        <div class="text-white font-medium">{{ formatFieldValue(item[key]) }}</div>
                      </div>
                    </div>
                    <hr class="my-2 border-white/30" />
                  </div>
                </div>
                <div v-else-if="settingsData[section.key] && typeof settingsData[section.key] === 'object'">
                  <div class="bg-slate-800/50 rounded-lg p-6 mb-6">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-2">
                      <div v-for="key in getSettingsFieldsForDisplay(settingsData[section.key], settingsView)" :key="key" class="space-y-1">
                        <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                        <div class="text-white font-medium">{{ formatFieldValue(settingsData[section.key][key]) }}</div>
                      </div>
                    </div>
                    <hr class="my-2 border-white/30" />
                  </div>
                </div>
              </template>
            </div>
            <div v-if="settingsSections.filter(s => s.key !== 'shift_summary').length === 0">No settings data found.</div>
          </div>
          <div v-else>No settings data found.</div>
        </div>
        <div v-if="tab==='applications'" class="tab-content">
          <div class="flex gap-4 mb-4">
            <button :class="['px-4 py-2 rounded', applicationsView==='pending' ? 'bg-primary text-white' : 'bg-white/10 text-primary']" @click="applicationsView='pending'">Pending</button>
            <button :class="['px-4 py-2 rounded', applicationsView==='approved' ? 'bg-primary text-white' : 'bg-white/10 text-primary']" @click="applicationsView='approved'">Approved</button>
            <button :class="['px-4 py-2 rounded', applicationsView==='rejected' ? 'bg-primary text-white' : 'bg-white/10 text-primary']" @click="applicationsView='rejected'">Rejected</button>
          </div>
          <div class="text-white/60 text-center py-8">(Applications content goes here)</div>
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
const payView = ref('debit'); // 'debit' or 'credit'
const applicationsView = ref('pending'); // 'pending', 'approved', 'rejected'
const route = useRoute();
const router = useRouter();
const companyId = route.params.company_id;
const empId = route.params.emp_id;
const date = route.params.date;

// Attendance
const attendanceData = ref([]);
const attendanceLoading = ref(false);
const attendanceError = ref('');

// Pay
const payData = ref([]);
const payLoading = ref(false);
const payError = ref('');

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

// Efficient recursive filtering function for display fields
function filteredFieldsForDisplay(obj) {
  const technicalFields = [
    'emp_id', 'employee_id', 'company_id', 'comp_id', 'reg_work_sched_id', 'work_schedule_id', 'created_by_account_id', 'updated_by_account_id', 'category_id', 'account_id', 'shift_id', 'id', 'status', 'deleted', 'flag_migrate', 'flag_custom', 'archive', 'archived_date', 'created_date', 'updated_date', 'period_type', 'cost_center', 'notes', 'bg_color', 'advanced_settings', 'default', 'flag_default_restday', 'flag_half_day', 'flag_open_shift', 'flag_trapp_source', 'flag_api_import', 'flag_payroll_correction', 'flag_tardiness_undertime', 'flag_delete_on_hours', 'flag_new_time_keeping', 'flag_on_leave', 'flag_holiday_include', 'flag_rd_include', 'flag_regular_or_excess', 'flag_time_in', 'flag_time_out', 'flag_lunch_break', 'flag_additional_breaks', 'flag_grace_period', 'flag_shift_threshold', 'flag_advance_break_rules', 'flag_working_on_restday', 'flag_breaks_on_holiday', 'flag_premium_payments', 'flag_premium_payments_starts_on_holiday_restday', 'flag_holiday_premium_on_regular_workday', 'flag_holiday_premium_on_regular_workday_nsd', 'flag_holiday_premium_on_holiday', 'flag_holiday_premium_on_holiday_nsd', 'flag_restday_premium_on_regular_workday', 'flag_restday_premium_on_regular_workday_nsd', 'flag_holiday_premium_on_restday', 'flag_holiday_premium_on_restday_nsd', 'flag_ot_holiday_rates_workday_holiday', 'flag_ot_holiday_rates_holiday_workday', 'flag_ot_rest_day_rates_workday_restday', 'flag_ot_rest_day_rates_restday_workday'];

  if (Array.isArray(obj)) {
    return obj.map(filteredFieldsForDisplay);
  }
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }
  return Object.fromEntries(
    Object.entries(obj).filter(([key, value]) => {
      if (technicalFields.includes(key)) return false;
      if (
        value === null ||
        value === '' ||
        value === undefined ||
        value === 'N/A'
      ) {
        return false;
      }
      if (
        value === 0 ||
        value === 0.0 ||
        value === '0' ||
        value === '0.00'
      ) {
        return false;
      }
      // Exclude 'Disabled' and 'no' values (boolean false, string 'Disabled', string 'no')
      if (
        value === false ||
        (typeof value === 'string' && (
          value.trim().toLowerCase() === 'disabled' ||
          value.trim().toLowerCase() === 'no'
        ))
      ) {
        return false;
      }
      return true;
    }).map(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        return [key, filteredFieldsForDisplay(value)];
      }
      return [key, value];
    })
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
  // Remove 'GMT' from time strings if present
  if (typeof value === 'string' && value.match(/\d{2}:\d{2}:\d{2}/) && value.includes('GMT')) {
    return value.replace(/\s*GMT\s*/g, '').trim();
  }
  return value.toString();
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

// Utility to log data to a file (for debugging)
function logDataToFile(filename, heading, data, source) {
  // Only works in Node.js or Electron, not in browser, so this is a placeholder for real-world debugging
  // In a real Vue app, you would use a backend API or devtool for this
  if (typeof window === 'undefined' && typeof require === 'function') {
    const fs = require('fs');
    const logContent = `==== ${heading} ====
Source: ${source}
Data:
${JSON.stringify(data, null, 2)}\n\n`;
    fs.appendFileSync(filename, logContent);
  } else {
    // For browser: print to console for now
    console.log(`==== ${heading} (${source}) ====`);
    console.log(data);
  }
}

async function fetchAttendance() {
  if (!selectedEmployee.value || !selectedDate.value) return;
  attendanceLoading.value = true;
  attendanceError.value = '';
  try {
    const res = await fetch(`/api/deepdive/timekeeping/${companyId}/${selectedEmployee.value.emp_id}/${selectedDate.value}`);
    const json = await res.json();
    attendanceData.value = json.data || [];
    logDataToFile('attendance_log.txt', 'Attendance Data', json.data, `/api/deepdive/timekeeping/${companyId}/${selectedEmployee.value.emp_id}/${selectedDate.value}`);
  } catch (e) {
    attendanceError.value = 'Failed to load attendance data.';
  } finally {
    attendanceLoading.value = false;
  }
}

async function fetchPay() {
  if (!selectedEmployee.value || !selectedDate.value) return;
  payLoading.value = true;
  payError.value = '';
  try {
    const res = await fetch(`/api/deepdive/payroll-cronjob/${companyId}/${selectedEmployee.value.emp_id}/${selectedDate.value}`);
    const json = await res.json();
    payData.value = json.data || [];
  } catch (e) {
    payError.value = 'Failed to load pay data.';
  } finally {
    payLoading.value = false;
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
      logDataToFile('settings_log.txt', 'Settings Data', json.data, `/api/deepdive/shifts/${companyId}/${selectedEmployee.value.emp_id}/${selectedDate.value}`);
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
    fetchPay(); // Added fetchPay to watch
    fetchSettings();
  }
});

onMounted(() => {
  // Initial fetch might happen on mount if empId and date are already in route
  // or if they are set by the user before the component mounts.
  // The watch will handle the actual fetching when emp and date are available.
});

const attendanceView = ref('filtered'); // 'filtered' or 'all'
const settingsView = ref('filtered'); // 'filtered' or 'all'

// Field groups for employee_time_in (from timekeepingdocumentation.txt)
const attendanceFieldGroups = [
  [ // Group 1
    'employee_time_in_id', 'work_schedule_id', 'date', 'time_in', 'lunch_out', 'lunch_in', 'break1_out', 'break1_in', 'break2_out', 'break2_in', 'time_out'
  ],
  [ // Group 2
    'total_hours', 'total_hours_required', 'corrected', 'reason', 'time_in_status', 'overbreak_min', 'late_min', 'tardiness_min', 'undertime_min', 'absent_min', 'notes'
  ],
  [ // Group 3
    'source', 'last_source', 'shift_name', 'status', 'change_log_date_filed', 'approval_time_in_id', 'flag_regular_or_excess', 'flag_delete_on_hours', 'flag_payroll_correction', 'ip_address', 'rest_day_r_a', 'flag_rd_include', 'holiday_approve', 'flag_holiday_include', 'kiosk_location', 'missing_lunch', 'approval_date', 'flag_open_shift', 'os_approval_time_in_id', 'action_time', 'current_date_nsd', 'next_date_nsd', 'for_resend_auto_rejected_id', 'current_date_holiday', 'next_date_holiday', 'source_rule', 'miss_required_break', 'hours_application_id', 'created_at', 'updated_at'
  ]
];

// Helper to get all mobile_ fields from a record
function getMobileFields(record) {
  return Object.keys(record).filter(key => key.startsWith('mobile_'));
}

function getAttendanceFieldsForDisplay(record, view) {
  // Exclude emp_id, comp_id, company_id
  const exclude = ['emp_id', 'comp_id', 'company_id'];
  // For each group, get fields present in the record
  const groups = attendanceFieldGroups.map(group =>
    group.filter(field => field in record && !exclude.includes(field))
  );
  // Mobile fields group
  const mobileFields = getMobileFields(record).filter(f => !exclude.includes(f));
  // For 'filtered', apply filtering logic
  if (view === 'filtered') {
    const filterFn = (key) => {
      const value = record[key];
      if (
        value === null || value === '' || value === undefined || value === 'N/A' ||
        value === 0 || value === 0.0 || value === '0' || value === '0.00' ||
        value === false ||
        (typeof value === 'string' && (
          value.trim().toLowerCase() === 'disabled' ||
          value.trim().toLowerCase() === 'no'
        ))
      ) {
        return false;
      }
      // Always show 'active'/'inactive'
      if (typeof value === 'string' && (value.trim().toLowerCase() === 'active' || value.trim().toLowerCase() === 'inactive')) {
        return true;
      }
      return true;
    };
    return [
      ...groups.map(group => group.filter(filterFn)),
      mobileFields.filter(filterFn)
    ];
  } else {
    // 'all' view: show all fields in each group
    return [
      ...groups,
      mobileFields
    ];
  }
}

function getSettingsFieldsForDisplay(obj, view) {
  // Exclude emp_id, comp_id/company_id at every level, recursively
  const exclude = ['emp_id', 'comp_id', 'company_id'];
  if (Array.isArray(obj)) {
    // For arrays, return an array of filtered key arrays for each object
    return obj.map(item => getSettingsFieldsForDisplay(item, view));
  }
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }
  // For objects, get keys that are not excluded
  let keys = Object.keys(obj).filter(key => !exclude.includes(key));
  if (view === 'filtered') {
    const filterFn = (key) => {
      const value = obj[key];
      if (
        value === null || value === '' || value === undefined || value === 'N/A' ||
        value === 0 || value === 0.0 || value === '0' || value === '0.00' ||
        value === false ||
        (typeof value === 'string' && (
          value.trim().toLowerCase() === 'disabled' ||
          value.trim().toLowerCase() === 'no'
        ))
      ) {
        return false;
      }
      // Always show 'active'/'inactive'
      if (typeof value === 'string' && (value.trim().toLowerCase() === 'active' || value.trim().toLowerCase() === 'inactive')) {
        return true;
      }
      return true;
    };
    keys = keys.filter(filterFn);
  }
  // For each key, if the value is an object or array, recursively filter its keys as well
  return keys.filter(key => {
    const value = obj[key];
    if (typeof value === 'object' && value !== null) {
      // If the nested object/array has no displayable keys, skip it
      const nested = getSettingsFieldsForDisplay(value, view);
      if (Array.isArray(nested)) {
        return nested.some(arr => Array.isArray(arr) ? arr.length > 0 : Object.keys(arr).length > 0);
      } else if (typeof nested === 'object') {
        return Object.keys(nested).length > 0;
      }
    }
    return true;
  });
}
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