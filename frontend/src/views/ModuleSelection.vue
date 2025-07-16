<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">select analytics module</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-4xl text-center mx-auto">
      <h3 class="text-primary mb-6 text-2xl">company: {{ companyName || companyId }}</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <!-- Workforce Module -->
        <div class="relative">
          <button 
            class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
            disabled
            @mouseenter="showTooltip = 'workforce'"
            @mouseleave="showTooltip = null"
          >
            <div class="text-3xl mb-3">👥</div>
            <div class="font-semibold">workforce</div>
          </button>
          <div v-if="showTooltip === 'workforce'" class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-black/80 text-white text-sm rounded whitespace-nowrap z-10">
            coming soon
          </div>
        </div>

        <!-- Payslip Module -->
        <div class="relative">
          <button 
            class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 hover:-translate-y-1 rounded-xl"
            @click="selectModule('payslip')"
          >
            <div class="text-3xl mb-3">💰</div>
            <div class="font-semibold">payslip</div>
          </button>
        </div>

        <!-- Time and Attendance Module -->
        <div class="relative">
          <button 
            class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
            disabled
            @mouseenter="showTooltip = 'time'"
            @mouseleave="showTooltip = null"
          >
            <div class="text-3xl mb-3">⏰</div>
            <div class="font-semibold">time and attendance</div>
          </button>
          <div v-if="showTooltip === 'time'" class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-black/80 text-white text-sm rounded whitespace-nowrap z-10">
            coming soon
          </div>
        </div>

        <!-- Shifts Module -->
        <div class="relative">
          <button 
            class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 hover:-translate-y-1 rounded-xl"
            @click="selectModule('shifts')"
          >
            <div class="text-3xl mb-3">🔄</div>
            <div class="font-semibold">shifts</div>
          </button>
        </div>

        <!-- Leaves Module -->
        <div class="relative">
          <button 
            class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
            disabled
            @mouseenter="showTooltip = 'leaves'"
            @mouseleave="showTooltip = null"
          >
            <div class="text-3xl mb-3">🌴</div>
            <div class="font-semibold">leaves</div>
          </button>
          <div v-if="showTooltip === 'leaves'" class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-black/80 text-white text-sm rounded whitespace-nowrap z-10">
            coming soon
          </div>
        </div>

        <!-- Deep Dive Module -->
        <div class="relative">
          <button 
            class="w-full p-8 text-lg bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-white/10 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
            disabled
            @mouseenter="showTooltip = 'deepdive'"
            @mouseleave="showTooltip = null"
          >
            <div class="text-3xl mb-3">🔍</div>
            <div class="font-semibold">deep dive</div>
          </button>
          <div v-if="showTooltip === 'deepdive'" class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-black/80 text-white text-sm rounded whitespace-nowrap z-10">
            coming soon
          </div>
        </div>
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
  name: 'ModuleSelection',
  data() {
    return {
      companyId: '',
      companyName: '',
      showTooltip: null
    }
  },
  created() {
    // Get company ID from route params
    this.companyId = this.$route.params.companyId;
    // Retrieve company name from sessionStorage
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    // Validate company ID exists
    if (!this.companyId) {
      this.$router.push('/');
      return;
    }
  },
  methods: {
    selectModule(module) {
      if (module === 'payslip') {
        this.$router.push(`/field-selection/${this.companyId}`);
      } else if (module === 'shifts') {
        this.$router.push(`/shifts-selection/${this.companyId}`);
      }
      // Other modules will be handled when they're implemented
    },
    goBack() {
      this.$router.push('/');
    }
  }
}
</script> 