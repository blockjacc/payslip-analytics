<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">employee schedule changes</h1>
    
    <!-- Employee Info -->
    <div v-if="employeeName" class="mb-6 bg-primary/8 rounded-lg p-2 px-4 text-primary text-lg flex flex-wrap items-center gap-2 max-w-2xl text-left">
      <span class="font-bold">employee:</span>
      <span class="text-white">{{ employeeName }}</span>
      <span class="text-primary">({{ empId }})</span>
    </div>

    <!-- Analysis Info -->
    <div v-if="analysisParams" class="mb-6 bg-white/5 rounded-lg p-4 w-full max-w-4xl">
      <div class="text-white text-center">
        <div class="text-lg font-semibold mb-2">
          analyzing {{ analysisParams.direction }} 365 days
        </div>
        <div class="text-sm text-white/70">
          {{ formatDate(analysisParams.dateFrom) }} to {{ formatDate(analysisParams.dateTo) }}
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white/10 rounded-xl p-8 w-full max-w-4xl text-center">
      <div class="text-white">
        <div class="text-lg mb-2">analyzing shift data...</div>
        <div class="text-sm text-white/70">processing 365 days of shift assignments</div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-white/10 rounded-xl p-8 w-full max-w-4xl text-center">
      <div class="text-red-400 text-lg mb-4">{{ error }}</div>
      <button 
        class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
        @click="goBack"
      >
        back
      </button>
    </div>

    <!-- Results -->
    <div v-if="!loading && !error && scheduleChanges" class="bg-white/10 rounded-xl p-8 w-full max-w-4xl">
      
      <!-- Summary -->
      <div class="mb-6 text-center">
        <div class="text-white text-lg font-semibold mb-2">
          {{ scheduleChanges.length }} schedule changes detected
        </div>
        <div v-if="scheduleChanges.length === 0" class="text-white/70">
          no shift assignment changes found in this period
        </div>
      </div>

      <!-- Changes Table -->
      <div v-if="scheduleChanges.length > 0" class="overflow-auto bg-white/5 rounded-lg">
        <table class="min-w-full text-sm text-left">
          <thead>
            <tr class="bg-primary/10 text-white font-bold">
              <th class="p-3">date</th>
              <th class="p-3">from shift</th>
              <th class="p-3">to shift</th>
              <th class="p-3">duration</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="change in scheduleChanges" :key="change.date" class="text-white border-b border-white/10">
              <td class="p-3">{{ formatDate(change.date) }}</td>
              <td class="p-3">
                <div>{{ change.fromShift || 'N/A' }}</div>
                <div class="text-xs text-white/70">{{ change.fromType || '' }}</div>
              </td>
              <td class="p-3">
                <div>{{ change.toShift || 'N/A' }}</div>
                <div class="text-xs text-white/70">{{ change.toType || '' }}</div>
              </td>
              <td class="p-3">{{ change.duration }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Navigation -->
      <div class="flex gap-4 justify-center mt-6">
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
          @click="goBack"
        >
          back
        </button>
        <button 
          class="px-6 py-3 text-base bg-primary text-white hover:bg-primary/80 transition"
          @click="exportToCSV"
          v-if="scheduleChanges.length > 0"
        >
          export csv
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EmployeeScheduleChanges',
  data() {
    return {
      companyId: '',
      empId: '',
      employeeName: '',
      analysisParams: null,
      loading: true,
      error: null,
      scheduleChanges: null
    }
  },
  created() {
    // Get parameters from route
    this.companyId = this.$route.params.companyId;
    this.empId = this.$route.params.empId;
    
    // Get analysis parameters from route query
    this.analysisParams = {
      direction: this.$route.query.direction,
      dateFrom: this.$route.query.date_from,
      dateTo: this.$route.query.date_to
    };
    
    // Validate required parameters
    if (!this.companyId || !this.empId || !this.analysisParams.dateFrom || !this.analysisParams.dateTo) {
      this.error = 'Missing required parameters';
      this.loading = false;
      return;
    }
    
    // Load employee info from sessionStorage
    this.loadEmployeeInfo();
    
    // Load and analyze shift data
    this.analyzeScheduleChanges();
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
    async analyzeScheduleChanges() {
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
        
        // Use drilldown mode to get detailed shift assignment records for 365 days
        const response = await axios.get(
          `/api/employee-shifts/${this.companyId}/${searchTerm}?date_from=${this.analysisParams.dateFrom}&date_to=${this.analysisParams.dateTo}&drilldown=true`
        );
        
        // Filter results to only show this specific employee
        const allShifts = response.data.shift_assignments || [];
        const employeeShifts = allShifts.filter(shift => shift.emp_id.toString() === this.empId.toString());
        
        // Analyze for schedule changes
        this.scheduleChanges = this.detectScheduleChanges(employeeShifts);
        
      } catch (err) {
        console.error('Error analyzing schedule changes:', err);
        this.error = 'Failed to analyze schedule changes. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    detectScheduleChanges(shifts) {
      if (!shifts || shifts.length === 0) {
        return [];
      }
      
      // Sort shifts by date (earliest first)
      const sortedShifts = shifts.sort((a, b) => {
        const dateA = new Date(a.valid_from);
        const dateB = new Date(b.valid_from);
        return dateA - dateB;
      });
      
      const changes = [];
      let previousShift = null;
      
      for (const shift of sortedShifts) {
        if (previousShift && 
            (previousShift.shift_name !== shift.shift_name || 
             previousShift.shift_type !== shift.shift_type)) {
          
          // Calculate duration of previous assignment
          const prevStart = new Date(previousShift.valid_from);
          const changeDate = new Date(shift.valid_from);
          const durationDays = Math.ceil((changeDate - prevStart) / (1000 * 60 * 60 * 24));
          
          changes.push({
            date: shift.valid_from,
            fromShift: previousShift.shift_name,
            fromType: previousShift.shift_type,
            toShift: shift.shift_name,
            toType: shift.shift_type,
            duration: `${durationDays} day${durationDays === 1 ? '' : 's'}`
          });
        }
        previousShift = shift;
      }
      
      return changes;
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
    exportToCSV() {
      if (!this.scheduleChanges || this.scheduleChanges.length === 0) return;
      
      let csv = 'Date,From Shift,From Type,To Shift,To Type,Duration\n';
      
      this.scheduleChanges.forEach(change => {
        csv += `${this.formatDate(change.date)},${change.fromShift || ''},${change.fromType || ''},${change.toShift || ''},${change.toType || ''},${change.duration}\n`;
      });
      
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `schedule_changes_${this.empId}_${this.analysisParams.direction}_${this.analysisParams.dateFrom}_${this.analysisParams.dateTo}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    },
    goBack() {
      this.$router.push(`/employee-shifts/${this.companyId}`);
    }
  }
}
</script> 