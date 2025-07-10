<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
    <div class="container mx-auto px-6 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-3xl font-bold text-primary">
            Shift Configuration Details
          </h1>
          <button
            @click="goBack"
            class="bg-secondary/20 hover:bg-secondary/40 text-white rounded-lg px-4 py-2 transition-colors flex items-center gap-2"
          >
            <span class="text-lg">←</span>
            Back to Results
          </button>
        </div>
        
        <!-- Shift Summary -->
        <div class="bg-slate-800/50 rounded-lg p-6 mb-6">
          <h2 class="text-xl font-semibold mb-4 text-primary">{{ shiftDetails.shift_name }}</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span class="text-gray-400">Type:</span>
              <span class="ml-2 font-medium">{{ shiftDetails.shift_type }}</span>
            </div>
            <div>
              <span class="text-gray-400">Start Time:</span>
              <span class="ml-2 font-medium text-primary">{{ formatTime(shiftDetails.work_start_time) }}</span>
            </div>
            <div>
              <span class="text-gray-400">End Time:</span>
              <span class="ml-2 font-medium">{{ formatTime(shiftDetails.work_end_time) }}</span>
            </div>
            <div>
              <span class="text-gray-400">Employees:</span>
              <span class="ml-2 font-medium">{{ formatNumber(shiftDetails.employee_count) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Configuration Details Table -->
      <div class="bg-slate-800/30 rounded-lg overflow-hidden mb-6">
        <div class="p-6 border-b border-white/10">
          <h3 class="text-lg font-semibold text-primary">Configuration Characteristics</h3>
          <p class="text-sm text-gray-400 mt-1">All configuration settings for this shift</p>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-700/50">
              <tr>
                <th class="text-left p-4 text-primary font-semibold">Category</th>
                <th class="text-left p-4 text-primary font-semibold">Configuration</th>
                <th class="text-center p-4 text-primary font-semibold">Enabled</th>
                <th class="text-center p-4 text-primary font-semibold">Value</th>
                <th class="text-left p-4 text-primary font-semibold">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="config in configurationDetails" :key="config.key" 
                  class="border-b border-white/10 hover:bg-white/5 transition-colors">
                <td class="p-4 font-medium text-secondary">{{ config.category }}</td>
                <td class="p-4">{{ config.name }}</td>
                <td class="p-4 text-center">
                  <span :class="config.enabled ? 'text-green-400' : 'text-gray-500'">
                    {{ config.enabled ? '✓' : '✗' }}
                  </span>
                </td>
                <td class="p-4 text-center font-bold text-primary">
                  {{ config.value }}
                </td>
                <td class="p-4 text-sm text-gray-400">{{ config.description }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Employee Data Actions -->
      <div class="bg-slate-800/30 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-primary mb-4">Employee Data</h3>
        <div class="flex flex-wrap gap-4">
          <button 
            @click="downloadEmployeeList"
            :disabled="isDownloading"
            class="bg-primary/20 hover:bg-primary/40 disabled:opacity-50 text-white rounded-lg px-6 py-3 transition-colors flex items-center gap-2"
          >
            <span>📥</span>
            {{ isDownloading ? 'Downloading...' : 'Download Employee List' }}
          </button>
          
          <button 
            @click="viewEmployees"
            class="bg-secondary/20 hover:bg-secondary/40 text-white rounded-lg px-6 py-3 transition-colors flex items-center gap-2"
          >
            <span>👥</span>
            View All Employees ({{ shiftDetails.employee_count }})
          </button>
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
      shiftDetails: {},
      isDownloading: false
    };
  },
  
  computed: {
    configurationDetails() {
      if (!this.shiftDetails.config_flags || !this.shiftDetails.config_values) {
        return [];
      }
      
      const flags = this.shiftDetails.config_flags;
      const values = this.shiftDetails.config_values;
      
      return [
        // Break & Time Management
        {
          key: 'lunch_break',
          category: 'Break & Time',
          name: 'Lunch Break',
          enabled: flags.enable_lunch_break,
          value: flags.enable_lunch_break ? `${values.lunch_break_duration} mins` : 'N/A',
          description: 'Standard lunch break duration during shift'
        },
        {
          key: 'additional_breaks',
          category: 'Break & Time',
          name: 'Additional Breaks',
          enabled: flags.enable_additional_breaks,
          value: flags.enable_additional_breaks ? `${values.additional_break_duration} mins` : 'N/A',
          description: 'Extra break time beyond lunch break'
        },
        {
          key: 'shift_threshold',
          category: 'Break & Time',
          name: 'Shift Threshold',
          enabled: flags.enable_shift_threshold,
          value: flags.enable_shift_threshold ? `${values.shift_threshold_mins} mins` : 'N/A',
          description: 'Minimum time required to qualify for full shift'
        },
        {
          key: 'grace_period',
          category: 'Break & Time',
          name: 'Grace Period',
          enabled: flags.enable_grace_period,
          value: flags.enable_grace_period ? `${values.grace_period_mins} mins` : 'N/A',
          description: 'Allowable late arrival without penalty'
        },
        {
          key: 'advance_break_rules',
          category: 'Break & Time',
          name: 'Advanced Break Rules',
          enabled: flags.enable_advance_break_rules,
          value: flags.enable_advance_break_rules ? 'Enabled' : 'Disabled',
          description: 'Complex break calculation rules'
        },
        
        // Premium Pay & Compensation
        {
          key: 'premium_payments',
          category: 'Premium Pay',
          name: 'Premium Payments',
          enabled: flags.premium_payments_enabled,
          value: flags.premium_payments_enabled ? 'Enabled' : 'Disabled',
          description: 'Overtime and premium pay calculations'
        },
        {
          key: 'premium_holiday_restday',
          category: 'Premium Pay',
          name: 'Holiday/Rest Day Premium',
          enabled: flags.enable_premium_payments_starts_on_holiday_restday,
          value: flags.enable_premium_payments_starts_on_holiday_restday ? 'Enabled' : 'Disabled',
          description: 'Premium pay starts immediately on holidays/rest days'
        },
        {
          key: 'advanced_premium_rules',
          category: 'Premium Pay',
          name: 'Advanced Premium Rules',
          enabled: flags.advanced_rules_premium_pay,
          value: flags.advanced_rules_premium_pay ? 'Enabled' : 'Disabled',
          description: 'Complex premium pay calculation rules'
        },
        
        // Holiday & Rest Day Policies
        {
          key: 'breaks_on_holiday',
          category: 'Holiday Policy',
          name: 'Breaks on Holiday',
          enabled: flags.enable_breaks_on_holiday,
          value: flags.enable_breaks_on_holiday ? `${values.breaks_on_holiday_duration} mins` : 'N/A',
          description: 'Break duration when working on holidays'
        },
        {
          key: 'working_on_restday',
          category: 'Holiday Policy',
          name: 'Working on Rest Day',
          enabled: flags.enable_working_on_restday,
          value: flags.enable_working_on_restday ? `${values.working_on_restday_additional_time} mins` : 'N/A',
          description: 'Additional time/compensation for rest day work'
        },
        {
          key: 'advanced_settings',
          category: 'Holiday Policy',
          name: 'Advanced Settings',
          enabled: flags.advanced_settings,
          value: flags.advanced_settings ? 'Enabled' : 'Disabled',
          description: 'Advanced holiday and rest day configurations'
        },
        {
          key: 'custom_schedule',
          category: 'Schedule Type',
          name: 'Custom Schedule',
          enabled: flags.is_custom_schedule,
          value: flags.is_custom_schedule ? 'Custom' : 'Standard',
          description: 'Whether this is a custom or standard schedule'
        }
      ];
    }
  },
  
  created() {
    this.loadShiftDetails();
  },
  
  methods: {
    loadShiftDetails() {
      // Get shift details from route params or localStorage
      const shiftData = this.$route.params.shiftData || JSON.parse(localStorage.getItem('selectedShiftDetails') || '{}');
      this.shiftDetails = shiftData;
      
      if (!this.shiftDetails.work_schedule_id) {
        // Redirect back if no shift data
        this.goBack();
      }
    },
    
    formatTime(time) {
      if (!time) return 'N/A';
      return time.toString().replace(/(\d{2})(\d{2})/, '$1:$2');
    },
    
    formatNumber(num) {
      return new Intl.NumberFormat().format(num || 0);
    },
    
    goBack() {
      this.$router.go(-1);
    },
    
    async downloadEmployeeList() {
      try {
        this.isDownloading = true;
        
        // First get the employee list
        const response = await fetch(`/api/shifts/allocation-drilldown/${this.shiftDetails.company_id}/${this.shiftDetails.shift_type}/${this.shiftDetails.work_schedule_id}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch employee data');
        }
        
        const data = await response.json();
        
        // Create CSV content
        const headers = ['Employee ID', 'Last Name', 'First Name', 'Location/Office'];
        const csvContent = [
          headers.join(','),
          ...data.employees.map(emp => [
            emp.emp_id,
            `"${emp.last_name}"`,
            `"${emp.first_name}"`,
            `"${emp.location_office}"`
          ].join(','))
        ].join('\n');
        
        // Download CSV
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${this.shiftDetails.shift_name.replace(/[^a-zA-Z0-9]/g, '_')}_employees.csv`;
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
    },
    
    viewEmployees() {
      // Navigate to existing drilldown view
      this.$router.push(`/shifts-allocation-drilldown/${this.shiftDetails.company_id}/${this.shiftDetails.shift_type}/${this.shiftDetails.work_schedule_id}`);
    }
  }
};
</script> 