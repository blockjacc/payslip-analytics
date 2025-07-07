<template>
  <div class="min-h-screen w-full bg-gradient-to-br from-[#0f2027] via-[#2c5364] to-[#232526] p-8">
    <div class="flex flex-col items-center justify-start">
      <h1 class="font-serif text-white mb-8 text-4xl text-center">employee shifts</h1>
    
    <!-- Employee and Date Range Summary -->
    <div class="mb-6 bg-primary/8 rounded-lg p-2 px-4 text-primary text-lg flex flex-wrap items-center gap-2 max-w-4xl text-left">
      <span class="font-bold">employee:</span>
      <span class="text-white">{{ employeeName }}</span>
      <span class="text-primary">({{ empId }})</span>
      <span class="mx-2">•</span>
      <span class="font-bold">period:</span>
      <span class="text-white">{{ dateRange }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white/10 rounded-xl p-8 w-full max-w-6xl text-center">
      <div class="text-white text-lg">loading shift history...</div>
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="bg-red-500/20 border border-red-500/30 rounded-xl p-8 w-full max-w-6xl text-center">
      <div class="text-red-300 text-lg mb-4">{{ error }}</div>
      <button 
        class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
        @click="goBack"
      >
        back
      </button>
    </div>

    <!-- Shift History Table -->
    <div v-if="shiftHistory.length > 0 && !loading" class="bg-white/10 rounded-xl p-8 w-full max-w-6xl">
      <div class="mb-6 text-center">
        <div class="text-white text-lg font-semibold">{{ shiftHistory.length }} shift assignments</div>
        <div class="text-white/70 text-sm">ordered chronologically (most recent first)</div>
      </div>

      <!-- Pagination Controls (Top) -->
      <div v-if="totalPages > 1" class="flex justify-between items-center mb-6">
        <button 
          v-if="hasPrevPage" 
          @click="currentPage--" 
          class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600 transition"
        >
          &larr; previous
        </button>
        <div v-else class="w-20"></div>
        
        <div class="text-white text-sm">
          page {{ currentPage }} of {{ totalPages }} 
          <span class="text-white/70">(showing {{ (currentPage - 1) * itemsPerPage + 1 }}-{{ Math.min(currentPage * itemsPerPage, shiftHistory.length) }} of {{ shiftHistory.length }})</span>
        </div>
        
        <button 
          v-if="hasNextPage" 
          @click="currentPage++" 
          class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600 transition"
        >
          next &rarr;
        </button>
        <div v-else class="w-20"></div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-white">
          <thead>
            <tr class="border-b border-white/20 text-left">
              <th class="pb-3 pr-4 text-sm font-semibold text-white/70">date</th>
              <th class="pb-3 pr-4 text-sm font-semibold text-white/70">shift name</th>
              <th class="pb-3 pr-4 text-sm font-semibold text-white/70">shift type</th>
              <th class="pb-3 pr-4 text-sm font-semibold text-white/70">status</th>
              <th class="pb-3 pr-4 text-sm font-semibold text-white/70">department</th>
              <th class="pb-3 text-sm font-semibold text-white/70">location</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(shift, index) in paginatedShifts" 
              :key="index"
              class="border-b border-white/10 hover:bg-white/5 transition-colors"
            >
              <td class="py-3 pr-4 text-sm">
                <div class="font-medium">{{ formatDate(shift.valid_from) }}</div>
                <div v-if="shift.valid_from !== shift.until" class="text-white/50 text-xs">
                  to {{ formatDate(shift.until) }}
                </div>
              </td>
              <td class="py-3 pr-4 text-sm font-medium">{{ shift.shift_name }}</td>
              <td class="py-3 pr-4 text-sm text-white/80">{{ shift.shift_type }}</td>
              <td class="py-3 pr-4 text-sm">
                <span 
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium',
                    shift.status === 'Active' ? 'bg-green-500/20 text-green-300' : 'bg-gray-500/20 text-gray-300'
                  ]"
                >
                  {{ shift.status }}
                </span>
              </td>
              <td class="py-3 pr-4 text-sm text-white/80">{{ shift.department_name }}</td>
              <td class="py-3 text-sm text-white/80">{{ shift.location_office }}</td>
            </tr>
          </tbody>
        </table>
              </div>

      <!-- Pagination Controls (Bottom) -->
      <div v-if="totalPages > 1" class="flex justify-between items-center mt-6">
        <button 
          v-if="hasPrevPage" 
          @click="currentPage--" 
          class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600 transition"
        >
          &larr; previous
        </button>
        <div v-else class="w-20"></div>
        
        <div class="text-white text-sm">
          page {{ currentPage }} of {{ totalPages }}
        </div>
        
        <button 
          v-if="hasNextPage" 
          @click="currentPage++" 
          class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600 transition"
        >
          next &rarr;
        </button>
        <div v-else class="w-20"></div>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-4 justify-center mt-8">
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
          @click="goBack"
        >
          back
        </button>
        <button 
          class="px-6 py-3 text-base bg-emerald-500 text-white hover:bg-emerald-600 transition"
          @click="changeEmployee"
        >
          change employee
        </button>
      </div>
    </div>

    <!-- No Data State -->
    <div v-if="shiftHistory.length === 0 && !loading && !error" class="bg-white/10 rounded-xl p-8 w-full max-w-6xl text-center">
      <div class="text-white text-lg mb-4">no shift assignments found</div>
      <div class="text-white/70 text-sm mb-6">{{ employeeName }} has no shift assignments in the selected date range.</div>
      <div class="flex gap-4 justify-center">
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
          @click="goBack"
        >
          back
        </button>
        <button 
          class="px-6 py-3 text-base bg-emerald-500 text-white hover:bg-emerald-600 transition"
          @click="changeEmployee"
        >
          change employee
        </button>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'EmployeeShiftHistory',
  data() {
    return {
      companyId: '',
      empId: '',
      dateFrom: '',
      dateTo: '',
      employeeName: '',
      shiftHistory: [],
      currentPage: 1,
      itemsPerPage: 20,
      loading: true,
      error: null
    }
  },
  computed: {
    dateRange() {
      if (!this.dateFrom || !this.dateTo) return '';
      return `${this.formatDate(this.dateFrom)} - ${this.formatDate(this.dateTo)}`;
    },
    totalPages() {
      return Math.ceil(this.shiftHistory.length / this.itemsPerPage);
    },
    paginatedShifts() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.shiftHistory.slice(start, end);
    },
    hasPrevPage() {
      return this.currentPage > 1;
    },
    hasNextPage() {
      return this.currentPage < this.totalPages;
    }
  },
  created() {
    // Get parameters from route
    this.companyId = this.$route.params.companyId;
    this.empId = this.$route.params.empId;
    this.dateFrom = this.$route.query.date_from;
    this.dateTo = this.$route.query.date_to;
    
    // Validate required parameters
    if (!this.companyId || !this.empId || !this.dateFrom || !this.dateTo) {
      this.error = 'Missing required parameters';
      this.loading = false;
      return;
    }
    
    // Load employee info from sessionStorage
    this.loadEmployeeInfo();
    
    // Load shift history
    this.loadShiftHistory();
  },
  methods: {
    loadEmployeeInfo() {
      const storedEmployee = sessionStorage.getItem('selectedEmployee');
      if (storedEmployee) {
        const employee = JSON.parse(storedEmployee);
        this.employeeName = `${employee.first_name} ${employee.last_name}`;
      } else {
        this.employeeName = `Employee ${this.empId}`;
      }
    },
    async loadShiftHistory() {
      this.loading = true;
      this.error = null;
      
      try {
        // Get employee info to search by name
        const storedEmployee = sessionStorage.getItem('selectedEmployee');
        if (!storedEmployee) {
          this.error = 'Employee information not found';
          return;
        }
        
        const employee = JSON.parse(storedEmployee);
        const searchTerm = employee.last_name || employee.first_name || this.empId;
        
        // Use drilldown mode to get detailed shift assignment records
        const response = await axios.get(
          `/api/employee-shifts/${this.companyId}/${searchTerm}?date_from=${this.dateFrom}&date_to=${this.dateTo}&drilldown=true`
        );
        
        // Filter results to only show this specific employee
        const allShifts = response.data.shift_assignments || [];
        this.shiftHistory = allShifts.filter(shift => shift.emp_id.toString() === this.empId.toString());
        
        // Sort by date (most recent first)
        this.shiftHistory.sort((a, b) => {
          const dateA = new Date(a.valid_from);
          const dateB = new Date(b.valid_from);
          return dateB - dateA; // Descending order
        });
        
        // Reset pagination when new data loads
        this.resetPagination();
        
      } catch (err) {
        console.error('Error loading shift history:', err);
        this.error = 'Failed to load shift history. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      } catch (e) {
        return dateString;
      }
    },
    goBack() {
      this.$router.push(`/employee-shifts/${this.companyId}`);
    },
    changeEmployee() {
      // Clear stored data and go back to employee selection
      sessionStorage.removeItem('selectedEmployee');
      sessionStorage.removeItem('selectedDateRange');
      this.$router.push(`/employee-shifts/${this.companyId}`);
    },
    resetPagination() {
      this.currentPage = 1;
    }
  }
}
</script> 