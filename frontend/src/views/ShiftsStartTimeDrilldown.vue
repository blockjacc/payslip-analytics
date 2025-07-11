<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
    <div class="container mx-auto px-6 py-8">
      
      <!-- Error State -->
      <div v-if="error && !loading" class="text-center py-12">
        <h1 class="text-3xl font-bold text-red-400 mb-4">Error Loading Shift Details</h1>
        <p class="text-white/70 mb-6">{{ error }}</p>
        <button @click="goBack" class="bg-slate-700 hover:bg-slate-600 px-6 py-2 rounded-lg transition-colors">
          Go Back
        </button>
      </div>

      <!-- Loading State -->
      <div v-else-if="loading" class="text-center py-12">
        <div class="animate-spin w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p class="text-white/70">Loading shift details...</p>
      </div>

      <!-- Main Content -->
      <div v-else-if="shiftData">
        <!-- Header -->
        <div class="text-center mb-8">
          <h1 class="text-4xl font-bold mb-3">{{ shiftData.shift_summary.shift_name }} - comprehensive shift details</h1>
          <div class="flex items-center justify-center gap-6 mb-6">
            <span class="text-lg text-white/70">{{ shiftData.shift_summary?.employee_count || 0 }} employees assigned</span>
            <button 
              @click="downloadEmployeeList" 
              :disabled="isDownloading"
              class="bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-800 px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            >
              <span v-if="isDownloading">Downloading...</span>
              <span v-else>download employee list</span>
            </button>
          </div>
        </div>

        <!-- Tabs -->
        <div class="bg-slate-800/50 rounded-lg p-6">
          <!-- Tab Headers -->
          <div class="flex border-b border-slate-600 mb-6">
            <button 
              v-for="tab in tabs" 
              :key="tab.key"
              @click="activeTab = tab.key"
              :class="[
                'px-6 py-3 font-medium transition-colors border-b-2',
                activeTab === tab.key 
                  ? 'border-emerald-500 text-emerald-400' 
                  : 'border-transparent text-white/70 hover:text-white hover:border-slate-500'
              ]"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- Tab Content -->
          <div class="min-h-[600px]">
            <!-- Work Schedule Tab -->
            <div v-if="activeTab === 'work_schedule'" class="space-y-6">
              <h3 class="text-xl font-semibold text-emerald-400 mb-4">work schedule configuration</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div v-for="(value, key) in shiftData.work_schedule" :key="key" class="space-y-1">
                  <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                  <div class="text-white font-medium">{{ formatFieldValue(value) }}</div>
                </div>
              </div>
            </div>

            <!-- Regular Schedule Tab -->
            <div v-if="activeTab === 'regular_schedule'" class="space-y-6">
              <h3 class="text-xl font-semibold text-emerald-400 mb-4">regular schedule configuration</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div v-for="(value, key) in shiftData.regular_schedule" :key="key" class="space-y-1">
                  <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                  <div class="text-white font-medium">{{ formatFieldValue(value) }}</div>
                </div>
              </div>
            </div>

            <!-- Flexible Hours Tab -->
            <div v-if="activeTab === 'flexible_hours'" class="space-y-6">
              <h3 class="text-xl font-semibold text-emerald-400 mb-4">flexible hours configuration</h3>
              <div v-if="shiftData.flexible_hours && Object.keys(shiftData.flexible_hours).length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div v-for="(value, key) in shiftData.flexible_hours" :key="key" class="space-y-1">
                  <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                  <div class="text-white font-medium">{{ formatFieldValue(value) }}</div>
                </div>
              </div>
              <div v-else class="text-center text-white/50 py-12">
                <p>No flexible hours configuration found for this shift</p>
              </div>
            </div>

            <!-- Rest Days Tab -->
            <div v-if="activeTab === 'rest_days'" class="space-y-6">
              <h3 class="text-xl font-semibold text-emerald-400 mb-4">rest days configuration</h3>
              <div v-if="shiftData.rest_days && shiftData.rest_days.length > 0" class="space-y-4">
                <div v-for="(restDay, index) in shiftData.rest_days" :key="index" class="bg-slate-700/50 p-4 rounded-lg">
                  <h4 class="text-sm font-medium text-emerald-300 mb-3">Rest Day {{ index + 1 }}</h4>
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div v-for="(value, key) in restDay" :key="key" class="space-y-1">
                      <div class="text-xs uppercase tracking-wide text-white/50">{{ formatFieldName(key) }}</div>
                      <div class="text-white font-medium">{{ formatFieldValue(value) }}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center text-white/50 py-12">
                <p>No rest days configuration found for this shift</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsStartTimeDrilldown',
  
  data() {
    return {
      loading: true,
      error: null,
      shiftData: null,
      activeTab: 'work_schedule',
      isDownloading: false,
      tabs: [
        { key: 'work_schedule', label: 'Work Schedule' },
        { key: 'regular_schedule', label: 'Regular Schedule' },
        { key: 'flexible_hours', label: 'Flexible Hours' },
        { key: 'rest_days', label: 'Rest Days' }
      ]
    };
  },
  
  created() {
    this.loadShiftDetails();
  },
  
  methods: {
    async loadShiftDetails() {
      try {
        this.loading = true;
        this.error = null;
        
        const companyId = this.$route.params.companyId;
        const shiftId = this.$route.params.shiftId;
        
        if (!companyId || !shiftId) {
          this.error = 'Missing company ID or shift ID';
          this.goBack();
          return;
        }
        
        const response = await fetch(`/api/shift-details/${companyId}/${shiftId}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch shift details');
        }
        
        const data = await response.json();
        
        // Store the comprehensive data directly from backend
        this.shiftData = data;
        
      } catch (error) {
        console.error('Error loading shift details:', error);
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },
    
    formatFieldName(fieldName) {
      return fieldName.replace(/_/g, ' ').toLowerCase();
    },
    
    formatFieldValue(value) {
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
    },
    
    goBack() {
      this.$router.go(-1);
    },
    
    async downloadEmployeeList() {
      try {
        this.isDownloading = true;
        
        // Get the employee list from the backend
        const response = await fetch(`/api/shift-employees/${this.shiftData.company_id}/${this.shiftData.shift_id}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch employee data');
        }
        
        const data = await response.json();
        
        // Create CSV content
        const headers = ['Employee ID', 'Last Name', 'First Name', 'Location/Office', 'Department', 'Rank', 'Valid From', 'Until', 'Status'];
        const csvContent = [
          headers.join(','),
          ...data.employees.map(emp => [
            emp.emp_id,
            `"${emp.last_name}"`,
            `"${emp.first_name}"`,
            `"${emp.location_office}"`,
            `"${emp.department_name}"`,
            `"${emp.rank_name}"`,
            `"${emp.valid_from}"`,
            `"${emp.until}"`,
            `"${emp.status}"`
          ].join(','))
        ].join('\n');
        
        // Download CSV
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${this.shiftData.shift_summary.shift_name.replace(/[^a-zA-Z0-9]/g, '_')}_employees.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
      } catch (error) {
        console.error('Error downloading employee list:', error);
        alert('Failed to download employee list. Please try again.');
      } finally {
        this.isDownloading = false;
      }
    }
  }
};
</script> 