<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">employee shift history</h1>
    <div v-if="selectedEmployee" class="mb-6 bg-primary/8 rounded-lg p-2 px-4 text-primary text-lg flex flex-wrap items-center gap-2 max-w-2xl text-left">
      <span class="font-bold">selected employee:</span>
      <span class="text-white">{{ selectedEmployee.first_name }} {{ selectedEmployee.last_name }}</span>
      <span class="text-primary">({{ selectedEmployee.emp_id }})</span>
    </div>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-lg text-center">
      <h3 class="text-primary mb-6 text-2xl">company: {{ companyName || companyId }}</h3>
      
      <!-- Employee Name Search Section -->
      <div v-if="!selectedEmployee">
        <EmployeeSearch
          :company-id="companyId"
          context="shifts"
          placeholder="first or last name"
          @employee-selected="selectEmployee"
          @error="handleSearchError"
        />
      </div>

      <!-- View Type Selection (shown after employee is selected) -->
      <div v-if="selectedEmployee && !viewType" class="mb-6">
        <label class="block mb-4 text-secondary text-sm">what would you like to view?</label>
        <div class="grid grid-cols-1 gap-3">
          <button 
            class="p-4 bg-white/10 border border-white/20 rounded text-white hover:bg-white/20 transition text-left"
            @click="selectViewType('daily')"
          >
            <div class="font-semibold">daily shifts</div>
            <div class="text-sm text-white/70">view daily shift assignments (max 30 days)</div>
          </button>
          <button 
            class="p-4 bg-white/10 border border-white/20 rounded text-white hover:bg-white/20 transition text-left"
            @click="selectViewType('changes')"
          >
            <div class="font-semibold">schedule changes</div>
            <div class="text-sm text-white/70">detect shift assignment changes (365 days forward/backward)</div>
          </button>
        </div>
      </div>

      <!-- Date Range Selection Section (shown for daily view) -->
      <div v-if="selectedEmployee && viewType === 'daily'" class="mb-6">
        <label class="block mb-2 text-secondary text-sm">select date range (max 30 days):</label>
        <div class="grid grid-cols-1 gap-3">
          <div>
            <label class="block mb-1 text-white/70 text-xs">from:</label>
            <input 
              type="date" 
              class="w-full h-10 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition"
              v-model="dateFrom"
              @change="validateDateRange"
            >
          </div>
          <div>
            <label class="block mb-1 text-white/70 text-xs">to:</label>
            <input 
              type="date" 
              class="w-full h-10 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition"
              v-model="dateTo"
              @change="validateDateRange"
            >
          </div>
        </div>
        <div v-if="dateRangeError" class="text-red-400 text-sm mt-2">{{ dateRangeError }}</div>
      </div>

      <!-- Change Detection Direction Selection (shown for changes view) -->
      <div v-if="selectedEmployee && viewType === 'changes'" class="mb-6">
        <label class="block mb-4 text-secondary text-sm">direction to analyze (365 days):</label>
        <div class="grid grid-cols-2 gap-3">
          <button 
            class="p-3 border rounded text-white transition"
            :class="changeDirection === 'forward' ? 'bg-primary border-primary' : 'bg-white/10 border-white/20 hover:bg-white/20'"
            @click="selectChangeDirection('forward')"
          >
            <div class="font-semibold">forward</div>
            <div class="text-xs">next 12 months</div>
          </button>
          <button 
            class="p-3 border rounded text-white transition"
            :class="changeDirection === 'backward' ? 'bg-primary border-primary' : 'bg-white/10 border-white/20 hover:bg-white/20'"
            @click="selectChangeDirection('backward')"
          >
            <div class="font-semibold">backward</div>
            <div class="text-xs">past 12 months</div>
          </button>
        </div>
      </div>

      <!-- Continue Button (shown after required selections are made) -->
      <div v-if="selectedEmployee && isReadyToContinue" class="flex gap-4 justify-center mb-4">
        <button 
          class="px-6 py-3 text-base bg-emerald-500 text-white font-semibold flex-1 max-w-[200px] disabled:opacity-70 disabled:cursor-not-allowed transition"
          @click="viewShiftHistory"
          :disabled="!isValidSelections"
        >
          {{ viewType === 'daily' ? 'view shifts' : 'analyze changes' }}
        </button>
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
          @click="resetSelection"
        >
          change employee
        </button>
      </div>

      <!-- Back to View Selection Button -->
      <div v-if="selectedEmployee && viewType" class="flex gap-4 justify-center mb-4">
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
          @click="backToViewSelection"
        >
          back to options
        </button>
      </div>

      <!-- Back Button -->
      <div v-if="!selectedEmployee" class="flex gap-4 justify-center mt-6">
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
          @click="goBack"
        >
          back
        </button>
      </div>

      <div v-if="error" class="text-red-400 text-sm mt-2">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import EmployeeSearch from '../components/EmployeeSearch.vue'

export default {
  name: 'EmployeeShifts',
  components: {
    EmployeeSearch
  },
  data() {
    return {
      companyId: '',
      companyName: '',
      selectedEmployee: null,
      viewType: '', // 'daily' or 'changes'
      dateFrom: '',
      dateTo: '',
      dateRangeError: '',
      changeDirection: '', // 'forward' or 'backward'
      error: null
    }
  },
  computed: {
    isReadyToContinue() {
      if (!this.selectedEmployee) return false;
      if (this.viewType === 'daily') {
        return this.dateFrom && this.dateTo && !this.dateRangeError;
      }
      if (this.viewType === 'changes') {
        return this.changeDirection;
      }
      return false;
    },
    isValidSelections() {
      if (this.viewType === 'daily') {
        return this.dateFrom && this.dateTo && !this.dateRangeError;
      }
      if (this.viewType === 'changes') {
        return this.changeDirection;
      }
      return false;
    }
  },
  created() {
    // Get company ID from route params
    this.companyId = this.$route.params.companyId;
    // Retrieve company name from sessionStorage
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    // Validate company ID exists
    if (!this.companyId) {
      this.error = 'Invalid company ID';
      this.$router.push('/');
    }
  },
  methods: {
    handleSearchError(errorMessage) {
      this.error = errorMessage;
    },
    selectEmployee(employee) {
      if (!employee) return;
      
      // Set selected employee (now comes from reusable component)
      this.selectedEmployee = employee;
      
      // Clear any previous errors and selections
      this.error = null;
      this.viewType = '';
      this.changeDirection = '';
      this.dateRangeError = '';
    },
    selectViewType(type) {
      this.viewType = type;
      
      if (type === 'daily') {
        // Set default date range (last 30 days) for daily view
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        this.dateTo = today.toISOString().split('T')[0];
        this.dateFrom = thirtyDaysAgo.toISOString().split('T')[0];
      } else {
        // Clear date range for changes view
        this.dateFrom = '';
        this.dateTo = '';
      }
    },
    selectChangeDirection(direction) {
      this.changeDirection = direction;
    },
    backToViewSelection() {
      this.viewType = '';
      this.changeDirection = '';
      this.dateFrom = '';
      this.dateTo = '';
      this.dateRangeError = '';
    },
    resetSelection() {
      this.selectedEmployee = null;
      this.viewType = '';
      this.dateFrom = '';
      this.dateTo = '';
      this.dateRangeError = '';
      this.changeDirection = '';
    },
    validateDateRange() {
      this.dateRangeError = '';
      
      if (!this.dateFrom || !this.dateTo) {
        return;
      }
      
      const fromDate = new Date(this.dateFrom);
      const toDate = new Date(this.dateTo);
      
      // Check if from date is after to date
      if (fromDate > toDate) {
        this.dateRangeError = 'from date cannot be after to date';
        return;
      }
      
      // Check if date range exceeds 30 days
      const diffTime = Math.abs(toDate - fromDate);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays > 30) {
        this.dateRangeError = 'date range cannot exceed 30 days';
        return;
      }
    },
    viewShiftHistory() {
      if (!this.isValidSelections) {
        return;
      }
      
      // Store selected employee info
      sessionStorage.setItem('selectedEmployee', JSON.stringify(this.selectedEmployee));
      
      if (this.viewType === 'daily') {
        // Existing daily shifts view
        sessionStorage.setItem('selectedDateRange', JSON.stringify({
          dateFrom: this.dateFrom,
          dateTo: this.dateTo
        }));
        
        // Navigate to employee shift history table view
        this.$router.push(`/employee-shift-history/${this.companyId}/${this.selectedEmployee.emp_id}?date_from=${this.dateFrom}&date_to=${this.dateTo}`);
        
      } else if (this.viewType === 'changes') {
        // New change detection view
        const today = new Date();
        let startDate, endDate;
        
        if (this.changeDirection === 'forward') {
          startDate = today;
          endDate = new Date(today.getTime() + 365 * 24 * 60 * 60 * 1000);
        } else {
          startDate = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000);
          endDate = today;
        }
        
        const dateFrom = startDate.toISOString().split('T')[0];
        const dateTo = endDate.toISOString().split('T')[0];
        
        // Store change detection parameters
        sessionStorage.setItem('scheduleChangeParams', JSON.stringify({
          direction: this.changeDirection,
          dateFrom: dateFrom,
          dateTo: dateTo
        }));
        
        // Navigate to schedule changes view
        this.$router.push(`/employee-schedule-changes/${this.companyId}/${this.selectedEmployee.emp_id}?direction=${this.changeDirection}&date_from=${dateFrom}&date_to=${dateTo}`);
      }
    },
    goBack() {
      this.$router.push(`/shifts-selection/${this.companyId}`);
    }
  },
  watch: {
    // Watch for route changes to update company ID
    '$route.params.companyId': {
      handler(newCompanyId) {
        this.companyId = newCompanyId;
      },
      immediate: true
    }
  }
}
</script> 