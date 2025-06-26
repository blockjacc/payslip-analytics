<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">Multiple Pay Periods Detected</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-2xl text-center">
      <div class="mb-8 pb-6 border-b border-white/10">
        <h3 class="text-primary mb-3 text-xl">Company ID: {{ companyId }}</h3>
        <h3 class="text-primary mb-3 text-xl">Employee ID: {{ employeeId === 'all' ? 'All Employees' : employeeId }}</h3>
        <h3 v-if="payrollGroupId" class="text-primary mb-3 text-xl">Payroll Group: {{ payrollGroupId }}</h3>
        <h3 v-if="filterDisplay" class="text-primary mb-3 text-xl">{{ filterDisplay }}</h3>
        <h3 class="text-primary text-xl">Period: {{ formatDate(periodFrom) }} - {{ formatDate(periodTo) }}</h3>
      </div>
      <p class="text-white mb-8 text-lg">
        Your selected date range contains multiple pay periods. 
        How would you like to view the data?
      </p>
      <div class="flex flex-col gap-4">
        <button 
          class="p-6 text-xl bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold flex flex-col items-center justify-center w-full transition-transform hover:-translate-y-1"
          @click="selectAggregation('aggregate')"
        >
          Aggregate Data
          <small class="block text-sm mt-2 opacity-80">View combined totals for all periods</small>
        </button>
        <button 
          class="p-6 text-xl bg-emerald-500 text-white font-semibold flex flex-col items-center justify-center w-full transition-transform hover:-translate-y-1"
          @click="selectAggregation('separate')"
        >
          Separate Data
          <small class="block text-sm mt-2 opacity-80">View each period individually</small>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AggregationChoice',
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
        filters.push(`Location ID: ${this.$route.query.location_id}`);
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
  }
}
</script> 