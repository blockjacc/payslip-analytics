<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">Multiple Pay Periods Detected</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-2xl text-center">
      <div class="mb-8 pb-6 border-b border-white/10">
        <h3 class="text-primary mb-3 text-xl">Company ID: {{ companyId }}</h3>
        <h3 class="text-primary mb-3 text-xl">Employee ID: {{ employeeId === 'all' ? 'All Employees' : employeeId }}</h3>
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
      this.$router.push({
        name: 'Analytics',
        params: {
          companyId: this.companyId,
          employeeId: this.employeeId,
          periodFrom: this.periodFrom,
          periodTo: this.periodTo,
          aggregationType: type
        }
      });
    }
  }
}
</script> 