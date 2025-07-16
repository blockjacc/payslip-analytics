<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">schedule type analysis</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-4xl text-center mx-auto">
      <h3 class="text-primary mb-6 text-2xl">company: {{ companyName || companyId }}</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <!-- Type Distribution Option -->
        <button 
          class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 hover:-translate-y-1 rounded-xl"
          @click="goToTypeDistribution"
        >
          <div class="text-3xl mb-3">📊</div>
          <div class="font-semibold">type distribution</div>
          <div class="text-sm opacity-70 mt-2">analyze distribution of schedule types</div>
        </button>
        <!-- Shift Changes Option -->
        <button 
          class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 hover:-translate-y-1 rounded-xl"
          @click="goToShiftChanges"
        >
          <div class="text-3xl mb-3">🔄</div>
          <div class="font-semibold">shift changes</div>
          <div class="text-sm opacity-70 mt-2">find employees with shift changes during period</div>
        </button>
      </div>
      <div class="flex gap-4 justify-center mt-6">
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
          @click="goBack"
        >
          back
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsScheduleTypeSelection',
  data() {
    return {
      companyId: '',
      companyName: '',
      currentStep: 1,
      selectedScheduleType: '',
      scheduleTypes: [],
      error: null
    }
  },
  created() {
    this.companyId = this.$route.params.companyId;
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    if (!this.companyId) {
      this.$router.push('/');
      return;
    }
  },
  methods: {
    goToTypeDistribution() {
      this.$router.push(`/shifts-schedule-type-analytics/${this.companyId}`);
    },
    goToShiftChanges() {
      this.$router.push(`/shifts-changes-date-picker/${this.companyId}`);
    },
    goBack() {
      this.$router.push(`/shifts-selection/${this.companyId}`);
    }
  }
}
</script> 