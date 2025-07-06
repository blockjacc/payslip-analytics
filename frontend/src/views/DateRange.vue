<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">select date range</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-lg text-center">
      <div class="mb-8 pb-6 border-b border-white/10">
        <h3 class="text-primary mb-3 text-xl">company id: {{ companyId }}</h3>
        <h3 class="text-primary text-xl">employee id: {{ employeeId === 'all' ? 'all employees' : employeeId }}</h3>
        <h3 v-if="payrollGroupId" class="text-primary text-xl">payroll group: {{ payrollGroupId }}</h3>
        <h3 v-if="filterDisplay" class="text-primary text-xl">{{ filterDisplay }}</h3>
      </div>
      <h3 class="text-primary mb-6 text-2xl">choose period</h3>
      <div class="mb-6 text-left">
        <label class="block mb-2 text-secondary text-sm">from:</label>
        <select 
          class="w-full h-12 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition"
          v-model="selectedFromDate"
          @change="updateToDateOptions"
        >
          <option value="">select start date</option>
          <option 
            v-for="date in fromDates" 
            :key="date"
            :value="date"
          >
            {{ formatDate(date) }}
          </option>
        </select>
      </div>
      <div class="mb-6 text-left">
        <label class="block mb-2 text-secondary text-sm">to:</label>
        <select 
          class="w-full h-12 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition disabled:opacity-50"
          v-model="selectedToDate"
          :disabled="!selectedFromDate"
        >
          <option value="">select end date</option>
          <option 
            v-for="date in availableToDates" 
            :key="date"
            :value="date"
          >
            {{ formatDate(date) }}
          </option>
        </select>
      </div>
      <button 
        class="w-full max-w-[200px] px-8 py-3 text-base bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold disabled:opacity-70 disabled:cursor-not-allowed transition"
        @click="submitDateRange"
        :disabled="!selectedFromDate || !selectedToDate"
      >
        view analytics
      </button>
      <div v-if="error" class="text-red-400 text-sm mt-2">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  name: 'DateRange',
  setup() {
    const router = useRouter();
    return { router };
  },
  data() {
    return {
      companyId: '',
      employeeId: '',
      payrollGroupId: '',
      selectedFromDate: '',
      selectedToDate: '',
      error: '',
      fromDates: [],
      toDates: [],
      loading: false,
      // Additional filter parameters
      departmentId: '',
      rankId: '',
      employmentTypeId: '',
      positionId: '',
      costCenterId: '',
      projectId: '',
      locationId: '',
      filterDisplay: '',
      locationName: '',
    }
  },
  created() {
    this.companyId = this.$route.params.companyId;
    this.employeeId = this.$route.params.employeeId;
    
    // Get payroll group ID from query parameters or sessionStorage
    this.payrollGroupId = this.$route.query.payroll_group_id || sessionStorage.getItem('selectedPayrollGroup') || '';
    
    // Get additional filter parameters from query
    this.departmentId = this.$route.query.department_id || '';
    this.rankId = this.$route.query.rank_id || '';
    this.employmentTypeId = this.$route.query.employment_type_id || '';
    this.positionId = this.$route.query.position_id || '';
    this.costCenterId = this.$route.query.cost_center_id || '';
    this.projectId = this.$route.query.project_id || '';
    this.locationId = this.$route.query.location_id || '';
    
    if (this.locationId) {
      this.fetchLocationName();
    }
    
    // Build filter display text
    this.buildFilterDisplay();
    
    this.fetchDates();
  },
  computed: {
    isValidDateRange() {
      if (!this.selectedFromDate || !this.selectedToDate) return false;
      return new Date(this.selectedFromDate) <= new Date(this.selectedToDate);
    },
    availableToDates() {
      if (!this.selectedFromDate) return [];
      return this.toDates.filter(date => new Date(date) >= new Date(this.selectedFromDate));
    }
  },
  methods: {
    async fetchDates() {
      try {
        const endpoint = this.employeeId === 'all' 
          ? `/api/dates/${this.companyId}`
          : `/api/dates/${this.companyId}/${this.employeeId}`;
        
        // Add payroll group parameter if available
        const params = {};
        if (this.payrollGroupId) {
          params.payroll_group_id = this.payrollGroupId;
        }
        
        const response = await axios.get(endpoint, { params });
        this.fromDates = response.data.period_from_dates;
        this.toDates = response.data.period_to_dates;
        this.updateToDateOptions();
      } catch (err) {
        this.error = 'Failed to fetch dates';
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    async submitDateRange() {
      if (!this.isValidDateRange) {
        this.error = 'Period from must be earlier than period to';
        return;
      }
      
      this.loading = true;
      try {
        // Check if this is a multiple pay period using the appropriate endpoint
        const endpoint = this.employeeId === 'all' 
          ? `/api/dates/${this.companyId}`
          : `/api/dates/${this.companyId}/${this.employeeId}`;
        
        // Add payroll group parameter if available
        const params = {};
        if (this.payrollGroupId) {
          params.payroll_group_id = this.payrollGroupId;
        }
        
        const response = await axios.get(endpoint, { params });
        const periodFromDates = response.data.period_from_dates;
        
        // Find if there's any period_from date that falls between our selected range
        const selectedFromDate = new Date(this.selectedFromDate);
        const selectedToDate = new Date(this.selectedToDate);
        
        const hasMultiplePeriods = periodFromDates.some(date => {
          const periodFrom = new Date(date);
          return periodFrom > selectedFromDate && periodFrom <= selectedToDate;
        });

        // Prepare route parameters
        const routeParams = {
          companyId: this.companyId,
          employeeId: this.employeeId,
          periodFrom: this.selectedFromDate,
          periodTo: this.selectedToDate
        };

        // Add query parameters for payroll group if available
        const queryParams = {};
        if (this.payrollGroupId) {
          queryParams.payroll_group_id = this.payrollGroupId;
        }
        
        // Add additional filter parameters
        if (this.departmentId) {
          queryParams.department_id = this.departmentId;
        }
        if (this.rankId) {
          queryParams.rank_id = this.rankId;
        }
        if (this.employmentTypeId) {
          queryParams.employment_type_id = this.employmentTypeId;
        }
        if (this.positionId) {
          queryParams.position_id = this.positionId;
        }
        if (this.costCenterId) {
          queryParams.cost_center_id = this.costCenterId;
        }
        if (this.projectId) {
          queryParams.project_id = this.projectId;
        }
        if (this.locationId) {
          queryParams.location_id = this.locationId;
        }

        if (hasMultiplePeriods) {
          // Navigate to aggregation choice page
          await this.router.push({
            name: 'AggregationChoice',
            params: routeParams,
            query: queryParams
          });
        } else {
          // Navigate directly to analytics
          await this.router.push({
            name: 'Analytics',
            params: {
              ...routeParams,
              aggregationType: 'single'
            },
            query: queryParams
          });
        }
      } catch (err) {
        this.error = 'Failed to navigate. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    updateToDateOptions() {
      // Reset selectedToDate when selectedFromDate changes
      this.selectedToDate = '';
      this.error = '';
    },
    async fetchLocationName() {
      try {
        const response = await axios.get(`/api/settings-options/${this.companyId}/location_and_offices`);
        const options = response.data.options || [];
        const found = options.find(opt => String(opt.id) === String(this.locationId));
        if (found) {
          this.locationName = found.name;
          this.buildFilterDisplay();
        }
      } catch (err) {
        // fallback: leave as ID
      }
    },
    buildFilterDisplay() {
      const filters = [];
      if (this.departmentId) filters.push(`department id: ${this.departmentId}`);
      if (this.rankId) filters.push(`rank id: ${this.rankId}`);
      if (this.employmentTypeId) filters.push(`employment type id: ${this.employmentTypeId}`);
      if (this.positionId) filters.push(`position id: ${this.positionId}`);
      if (this.costCenterId) filters.push(`cost center id: ${this.costCenterId}`);
      if (this.projectId) filters.push(`project id: ${this.projectId}`);
      if (this.locationId) {
        filters.push(this.locationName ? `location: ${this.locationName}` : `location id: ${this.locationId}`);
      }
      this.filterDisplay = filters.join(' | ');
    }
  },
  watch: {
    selectedFromDate() {
      // Reset selectedToDate when selectedFromDate changes
      this.selectedToDate = '';
      this.error = '';
    }
  }
}
</script> 