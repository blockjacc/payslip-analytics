<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">select shifts option</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-4xl text-center mx-auto">
      <h3 class="text-primary mb-6 text-2xl">company id: {{ companyId }}</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Schedule Type Option -->
        <button 
          class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 hover:-translate-y-1 rounded-xl"
          @click="goToScheduleType"
        >
          <div class="text-3xl mb-3">📅</div>
          <div class="font-semibold">schedule type</div>
        </button>
        <!-- Allocation Option -->
        <button 
          class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 hover:-translate-y-1 rounded-xl"
          @click="goToAllocation"
        >
          <div class="text-3xl mb-3">🗂️</div>
          <div class="font-semibold">allocation</div>
        </button>
        <!-- By Employee Option -->
        <button 
          class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 hover:-translate-y-1 rounded-xl"
          @click="goToByEmployee"
        >
          <div class="text-3xl mb-3">👤</div>
          <div class="font-semibold">by employee</div>
        </button>
        <!-- By Start Time Option -->
        <button 
          class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 hover:-translate-y-1 rounded-xl"
          @click="goToByStartTime"
        >
          <div class="text-3xl mb-3">🕐</div>
          <div class="font-semibold">by start time</div>
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
  name: 'ShiftsSelection',
  data() {
    return {
      companyId: ''
    }
  },
  created() {
    this.companyId = this.$route.params.companyId;
    if (!this.companyId) {
      this.$router.push('/');
      return;
    }
  },
  methods: {
    goToScheduleType() {
      this.$router.push(`/shifts-schedule-type-selection/${this.companyId}`);
    },
    goToAllocation() {
      this.$router.push(`/shifts-allocation-selection/${this.companyId}`);
    },
    goToByEmployee() {
      this.$router.push(`/employee-shifts/${this.companyId}`);
    },
    goToByStartTime() {
      this.$router.push(`/shifts-start-time-input/${this.companyId}`);
    },
    goBack() {
      this.$router.push('/');
    }
  }
}
</script> 