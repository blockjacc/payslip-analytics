<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">employee shift history</h1>
    <div v-if="selectedEmployee" class="mb-6 bg-primary/8 rounded-lg p-2 px-4 text-primary text-lg flex flex-wrap items-center gap-2 max-w-2xl text-left">
      <span class="font-bold">selected employee:</span>
      <span class="text-white">{{ selectedEmployee.first_name }} {{ selectedEmployee.last_name }}</span>
      <span class="text-primary">({{ selectedEmployee.emp_id }})</span>
    </div>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-lg text-center">
      <h3 class="text-primary mb-6 text-2xl">company id: {{ companyId }}</h3>
      
      <!-- Employee Name Search Section -->
      <div v-if="!selectedEmployee" class="mb-6 relative">
        <input 
          type="text" 
          class="text-center text-lg h-12 w-full rounded border border-white/20 bg-white/10 text-white placeholder-white/50 focus:outline-none focus:border-primary transition"
          v-model="searchQuery"
          placeholder="first or last name"
          @input="debouncedSearch"
        >
        <div class="absolute top-full left-0 right-0 bg-primary/10 border border-primary/20 rounded-lg mt-1 max-h-[200px] overflow-y-auto z-50 backdrop-blur-md shadow-lg" v-if="filteredEmployees.length > 0">
          <div 
            v-for="employee in filteredEmployees" 
            :key="employee.emp_id"
            class="p-3 cursor-pointer transition-all duration-200 text-white border-b border-primary/20 text-left text-lg hover:bg-primary/20 hover:translate-x-1 last:border-b-0"
            @click="selectEmployee(employee)"
          >
            {{ employee.first_name }} {{ employee.last_name }} ({{ employee.emp_id }})
          </div>
        </div>
      </div>

      <!-- Search Button -->
      <div v-if="!selectedEmployee" class="flex gap-4 justify-center mb-4">
        <button 
          class="px-6 py-3 text-base bg-emerald-500 text-white font-semibold flex-1 max-w-[200px] disabled:opacity-70 disabled:cursor-not-allowed transition"
          @click="searchEmployees"
          :disabled="!searchQuery || searchQuery.length < 2"
        >
          search employees
        </button>
      </div>

      <!-- Date Range Selection Section (shown after employee is selected) -->
      <div v-if="selectedEmployee" class="mb-6">
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

      <!-- Continue Button (shown after employee and dates are selected) -->
      <div v-if="selectedEmployee" class="flex gap-4 justify-center mb-4">
        <button 
          class="px-6 py-3 text-base bg-emerald-500 text-white font-semibold flex-1 max-w-[200px] disabled:opacity-70 disabled:cursor-not-allowed transition"
          @click="viewShiftHistory"
          :disabled="!dateFrom || !dateTo || !!dateRangeError"
        >
          view shifts
        </button>
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
          @click="resetSelection"
        >
          change employee
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
import axios from 'axios';

export default {
  name: 'EmployeeShifts',
  data() {
    return {
      companyId: '',
      searchQuery: '',
      filteredEmployees: [],
      selectedEmployee: null,
      dateFrom: '',
      dateTo: '',
      dateRangeError: '',
      error: null,
      searchTimeout: null
    }
  },
  created() {
    // Get company ID from route params
    this.companyId = this.$route.params.companyId;
    
    // Validate company ID exists
    if (!this.companyId) {
      this.error = 'Invalid company ID';
      this.$router.push('/');
    }
  },
  methods: {
    debouncedSearch() {
      // Clear any existing timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      
      // Set a new timeout
      this.searchTimeout = setTimeout(() => {
        if (this.searchQuery && this.searchQuery.length >= 2) {
          this.searchEmployeesByName();
        } else {
          this.filteredEmployees = [];
        }
      }, 300); // 300ms delay
    },
    async searchEmployeesByName() {
      if (!this.searchQuery || this.searchQuery.length < 2) {
        this.filteredEmployees = [];
        return;
      }
      
      try {
        // Call our new backend endpoint with a short date range for demo purposes
        const currentDate = new Date().toISOString().split('T')[0];
        const lastMonth = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        
        const response = await axios.get(
          `/api/employee-shifts/${this.companyId}/${this.searchQuery}?date_from=${lastMonth}&date_to=${currentDate}`
        );
        
        // Extract unique employees from the response
        const employees = response.data.employees || [];
        this.filteredEmployees = employees.map(emp => ({
          emp_id: emp.emp_id,
          first_name: emp.first_name,
          last_name: emp.last_name
        }));
        
        this.error = null;
      } catch (err) {
        this.error = 'Failed to search employees';
        this.filteredEmployees = [];
      }
    },
    async searchEmployees() {
      // Trigger the same search when button is clicked
      await this.searchEmployeesByName();
    },
    selectEmployee(employee) {
      if (!employee) return;
      
      // Set selected employee and clear search results
      this.selectedEmployee = employee;
      this.filteredEmployees = [];
      this.searchQuery = '';
      
      // Set default date range (last 30 days)
      const today = new Date();
      const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
      
      this.dateTo = today.toISOString().split('T')[0];
      this.dateFrom = thirtyDaysAgo.toISOString().split('T')[0];
      
      // Clear any previous errors
      this.error = null;
      this.dateRangeError = '';
    },
    resetSelection() {
      this.selectedEmployee = null;
      this.dateFrom = '';
      this.dateTo = '';
      this.dateRangeError = '';
      this.searchQuery = '';
      this.filteredEmployees = [];
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
      if (!this.selectedEmployee || !this.dateFrom || !this.dateTo || this.dateRangeError) {
        return;
      }
      
      // Store selected employee and date range info
      sessionStorage.setItem('selectedEmployee', JSON.stringify(this.selectedEmployee));
      sessionStorage.setItem('selectedDateRange', JSON.stringify({
        dateFrom: this.dateFrom,
        dateTo: this.dateTo
      }));
      
      // Navigate to employee shift history table view
      this.$router.push(`/employee-shift-history/${this.companyId}/${this.selectedEmployee.emp_id}?date_from=${this.dateFrom}&date_to=${this.dateTo}`);
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