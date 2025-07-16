<template>
  <div class="min-h-screen w-full p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">
      shifts starting at {{ formatStartTime(startTime) }}
    </h1>
    
    <!-- Loading and Error States -->
    <div v-if="loading" class="text-white text-center">loading shift data...</div>
    <div v-if="error" class="text-red-400 text-center">error: {{ error }}</div>
    
    <!-- Results Display -->
    <div v-if="!loading && !error && shiftsData" class="flex justify-center">
      <div class="bg-white/10 rounded-xl p-8 w-full max-w-6xl">
        
        <!-- Filter Summary -->
        <div class="mb-8 text-center">
          <h3 class="text-primary mb-2 text-2xl">company: {{ companyName || companyId }}</h3>
          <div class="text-primary text-lg mb-4">
            <p><span class="font-bold">start time:</span> {{ formatStartTime(startTime) }}</p>
            <p><span class="font-bold">total shifts found:</span> {{ shiftsData.total_shifts }}</p>
            <p><span class="font-bold">total employees:</span> {{ shiftsData.total_employees }}</p>
          </div>
          
          <!-- Applied Filters Display -->
          <div v-if="selectedConfigs.length > 0" class="mb-4 bg-primary/8 rounded-lg p-3 text-left">
            <h5 class="text-primary mb-2 text-base font-bold">applied filters:</h5>
            <div class="flex flex-wrap gap-2">
              <span v-for="config in selectedConfigs" :key="config" class="bg-primary/20 border border-primary/50 rounded-full px-3 py-1 text-sm text-white">
                {{ getConfigDisplayName(config) }}
              </span>
            </div>
          </div>
          <div v-else class="mb-4 text-white/70 text-sm">
            showing all shifts (no configuration filters applied)
          </div>
        </div>

        <!-- Shifts Table -->
        <div v-if="shiftsData.shifts && shiftsData.shifts.length > 0" class="mb-8">
          <div class="overflow-x-auto">
            <table class="w-full text-white border-collapse">
              <thead>
                <tr class="border-b border-white/20">
                  <th class="text-left p-3 text-primary font-semibold">shift name</th>
                  <th class="text-center p-3 text-primary font-semibold">employees</th>
                  <th v-for="config in sortedSelectedConfigs" :key="config" class="text-center p-3 text-primary font-semibold">
                    {{ getConfigDisplayName(config) }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="shift in shiftsData.shifts" :key="shift.work_schedule_id" 
                    class="border-b border-white/10 hover:bg-white/5 transition-colors cursor-pointer"
                    @click="viewShiftDetails(shift)">
                  <td class="p-3 font-medium text-primary">{{ shift.shift_name }}</td>
                  <td class="p-3 text-center">{{ formatNumber(shift.employee_count) }}</td>
                  <td v-for="config in sortedSelectedConfigs" :key="config" class="p-3 text-center text-primary font-bold">
                    {{ getConfigValue(shift, config) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- No Results -->
        <div v-else class="text-center text-white/70">
          <p class="text-lg">no shifts found matching your criteria</p>
          <p class="text-sm mt-2">try adjusting your filters or selecting a different start time</p>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-4 justify-center mt-8">
          <button 
            class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
            @click="goBackToFilters"
          >
            modify filters
          </button>
          <button 
            class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
            @click="goBackToStartTime"
          >
            change start time
          </button>
          <button 
            v-if="shiftsData && shiftsData.shifts && shiftsData.shifts.length > 0"
            class="px-6 py-3 text-base bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold transition"
            @click="downloadCSV"
          >
            download CSV
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsStartTimeAnalytics',
  data() {
    return {
      companyId: '',
      companyName: '',
      startTime: '',
      shiftsData: null,
      loading: false,
      error: '',
      selectedConfigs: [],
      selectedConfigCategory: '',
      
      // Display names for break time management only (no caps)
      configDisplayNames: {
        'enable_lunch_break': 'lunch break duration',
        'enable_additional_breaks': 'additional breaks schedule',
        'enable_shift_threshold': 'shift threshold minutes',
        'enable_grace_period': 'grace period settings',
        'enable_advance_break_rules': 'advanced break rules'
      }
    }
  },
  computed: {
    // Sorted selected configs for consistent column order
    sortedSelectedConfigs() {
      return [...this.selectedConfigs].sort();
    }
  },
  async created() {
    this.companyId = this.$route.params.companyId;
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    this.startTime = this.$route.params.startTime;
    
    if (!this.companyId || !this.startTime) {
      this.error = 'Missing required parameters';
      return;
    }
    
    // Load selected configurations from sessionStorage
    const storedConfigs = sessionStorage.getItem('selectedShiftConfigs');
    const storedCategory = sessionStorage.getItem('selectedShiftConfigCategory');
    
    this.selectedConfigs = storedConfigs ? JSON.parse(storedConfigs) : [];
    this.selectedConfigCategory = storedCategory || '';
    
    await this.fetchShiftsData();
  },
  methods: {
    async fetchShiftsData() {
      this.loading = true;
      this.error = '';
      
      try {
        // Convert startTime parameter (e.g., "0800") back to "08:00" format for API
        const formattedStartTime = this.startTime.length === 4 
          ? `${this.startTime.substring(0, 2)}:${this.startTime.substring(2, 4)}`
          : this.startTime;
        
        let url = `/api/shifts/by-start-time/${this.companyId}/${formattedStartTime}`;
        
        // Add configuration filters as query parameters if any are selected
        if (this.selectedConfigs.length > 0) {
          const configParams = this.selectedConfigs.map(config => `${config}=true`).join('&');
          url += `?${configParams}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }
        
        this.shiftsData = data;
      } catch (err) {
        this.error = err.message || 'Failed to fetch shifts data';
        this.shiftsData = null;
      } finally {
        this.loading = false;
      }
    },
    formatStartTime(timeStr) {
      // Convert "0800" to "08:00"
      if (timeStr.length === 4) {
        return `${timeStr.substring(0, 2)}:${timeStr.substring(2, 4)}`;
      }
      return timeStr;
    },
    formatTime(timeStr) {
      if (!timeStr) return 'N/A';
      // Convert "08:00:00" to "08:00"
      return timeStr.split(':').slice(0, 2).join(':');
    },
    formatNumber(val) {
      return new Intl.NumberFormat('en-US').format(val);
    },
    getConfigDisplayName(configName) {
      return this.configDisplayNames[configName] || configName;
    },
    
    getConfigValue(shift, configName) {
      if (!shift.config_flags) return 'N/A';
      
      const isEnabled = shift.config_flags[configName];
      
      if (!isEnabled) return '✗';
      
      // Show actual values if available
      if (shift.config_values) {
        switch(configName) {
          case 'enable_lunch_break':
            return shift.config_values.lunch_break_duration ? `${shift.config_values.lunch_break_duration}` : 'enabled';
          case 'enable_additional_breaks':
            return shift.config_values.additional_break_duration ? `${shift.config_values.additional_break_duration}` : 'enabled';
          case 'enable_shift_threshold':
            return shift.config_values.shift_threshold_mins ? `${shift.config_values.shift_threshold_mins}` : 'enabled';
          case 'enable_grace_period':
            return shift.config_values.grace_period_mins ? `${shift.config_values.grace_period_mins}` : 'enabled';
          case 'enable_advance_break_rules':
            return 'enabled';
          default:
            return 'enabled';
        }
      }
      
      return 'enabled';
    },
    viewShiftDetails(shift) {
      // Store shift details for drilldown
      const shiftData = {
        ...shift,
        company_id: this.companyId,
        start_time: this.startTime
      };
      localStorage.setItem('selectedShiftDetails', JSON.stringify(shiftData));
      
      // Navigate to the new drilldown view that shows all configuration details
      this.$router.push(`/shifts-start-time-drilldown/${this.companyId}/${shift.work_schedule_id}`);
    },
    downloadCSV() {
      if (!this.shiftsData || !this.shiftsData.shifts) return;
      
      let csv = 'Shift Name,Employees,Start Time,End Time,Total Hours\n';
      this.shiftsData.shifts.forEach(shift => {
        csv += `${shift.shift_name},${shift.employee_count},${this.formatTime(shift.work_start_time)},${this.formatTime(shift.work_end_time)},${shift.total_work_hours || 'N/A'}\n`;
      });
      csv += `Total,${this.shiftsData.total_employees},,,\n`;
      
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `shifts_by_start_time_${this.companyId}_${this.startTime}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    },
    goBackToFilters() {
      this.$router.push(`/shifts-start-time-config-selection/${this.companyId}`);
    },
    goBackToStartTime() {
      this.$router.push(`/shifts-start-time-input/${this.companyId}`);
    }
  }
}
</script> 