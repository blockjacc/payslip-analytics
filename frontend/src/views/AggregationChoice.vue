<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">multiple pay periods detected</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-2xl text-center">
      <div class="mb-8 pb-6 border-b border-white/10">
        <h3 class="text-primary mb-3 text-xl">company: {{ companyName || companyId }}</h3>
        <h3 class="text-primary mb-3 text-xl">employee: {{ employeeName }}</h3>
        <h3 v-if="payrollGroupId" class="text-primary mb-3 text-xl">payroll group: {{ payrollGroupId }}</h3>
        <h3 v-if="filterDisplay" class="text-primary mb-3 text-xl">{{ filterDisplay }}</h3>
        <h3 class="text-primary text-xl">period: {{ formatDate(periodFrom) }} - {{ formatDate(periodTo) }}</h3>
      </div>
      <p class="text-white mb-8 text-lg">
        your selected date range contains multiple pay periods. 
        how would you like to view the data?
      </p>
      <div class="flex flex-col gap-4">
        <button 
          class="p-6 text-xl bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold flex flex-col items-center justify-center w-full transition-transform hover:-translate-y-1"
          @click="selectAggregation('aggregate')"
        >
          aggregate data
          <small class="block text-sm mt-2 opacity-80">view combined totals for all periods</small>
        </button>
        <button 
          class="p-6 text-xl bg-emerald-500 text-white font-semibold flex flex-col items-center justify-center w-full transition-transform hover:-translate-y-1"
          @click="selectAggregation('separate')"
        >
          separate data
          <small class="block text-sm mt-2 opacity-80">view each period individually</small>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AggregationChoice',
  data() {
    return {
      locationName: '',
      companyName: '',
      employeeName: ''
    }
  },
  computed: {
    companyId() {
      return this.$route.params.companyId;
    },
    employeeId() {
      return this.$route.params.employeeId;
    },
    periodFrom() {
      return this.$route.params.periodFrom;
    },
    periodTo() {
      return this.$route.params.periodTo;
    },
    payrollGroupId() {
      return this.$route.query.payroll_group_id || sessionStorage.getItem('selectedPayrollGroup') || '';
    },
    filterDisplay() {
      const filters = [];
      
      if (this.$route.query.department_id) {
        filters.push(`Department ID: ${this.$route.query.department_id}`);
      }
      if (this.$route.query.rank_id) {
        filters.push(`Rank ID: ${this.$route.query.rank_id}`);
      }
      if (this.$route.query.employment_type_id) {
        filters.push(`Employment Type ID: ${this.$route.query.employment_type_id}`);
      }
      if (this.$route.query.position_id) {
        filters.push(`Position ID: ${this.$route.query.position_id}`);
      }
      if (this.$route.query.cost_center_id) {
        filters.push(`Cost Center ID: ${this.$route.query.cost_center_id}`);
      }
      if (this.$route.query.project_id) {
        filters.push(`Project ID: ${this.$route.query.project_id}`);
      }
      if (this.$route.query.location_id) {
        filters.push(this.locationName ? `Location: ${this.locationName}` : `Location ID: ${this.$route.query.location_id}`);
      }
      
      return filters.length > 0 ? filters.join(', ') : '';
    }
  },
  methods: {
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    async fetchLocationName() {
      try {
        const response = await axios.get(`/api/settings-options/${this.companyId}/location_and_offices`);
        const options = response.data.options || [];
        const found = options.find(opt => String(opt.id) === String(this.$route.query.location_id));
        if (found) {
          this.locationName = found.name;
        }
      } catch (err) {
        // fallback: leave as ID
      }
    },
    selectAggregation(type) {
      // Prepare route parameters
      const routeParams = {
        companyId: this.companyId,
        employeeId: this.employeeId,
        periodFrom: this.periodFrom,
        periodTo: this.periodTo,
        aggregationType: type
      };

      // Add query parameters for payroll group if available
      const queryParams = {};
      if (this.payrollGroupId) {
        queryParams.payroll_group_id = this.payrollGroupId;
      }
      
      // Add additional filter parameters
      if (this.$route.query.department_id) {
        queryParams.department_id = this.$route.query.department_id;
      }
      if (this.$route.query.rank_id) {
        queryParams.rank_id = this.$route.query.rank_id;
      }
      if (this.$route.query.employment_type_id) {
        queryParams.employment_type_id = this.$route.query.employment_type_id;
      }
      if (this.$route.query.position_id) {
        queryParams.position_id = this.$route.query.position_id;
      }
      if (this.$route.query.cost_center_id) {
        queryParams.cost_center_id = this.$route.query.cost_center_id;
      }
      if (this.$route.query.project_id) {
        queryParams.project_id = this.$route.query.project_id;
      }
      if (this.$route.query.location_id) {
        queryParams.location_id = this.$route.query.location_id;
      }

      this.$router.push({
        name: 'Analytics',
        params: routeParams,
        query: queryParams
      });
    }
  },
  created() {
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    if (this.$route.query.location_id) {
      this.fetchLocationName();
    }
    // Get employee name from sessionStorage if available
    if (this.$route.params.employeeId && this.$route.params.employeeId !== 'all') {
      const storedEmployee = sessionStorage.getItem('selectedEmployee');
      if (storedEmployee) {
        const emp = JSON.parse(storedEmployee);
        this.employeeName = `${emp.first_name} ${emp.last_name} (${emp.emp_id})`;
      } else {
        this.employeeName = `employee id: ${this.$route.params.employeeId}`;
      }
    } else {
      this.employeeName = 'all employees';
    }
  },
}
</script> 