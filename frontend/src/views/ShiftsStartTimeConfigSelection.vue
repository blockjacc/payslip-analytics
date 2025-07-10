<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">shift configuration filters</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-4xl text-center mx-auto">
      <h3 class="text-primary mb-6 text-2xl">company id: {{ companyId }}</h3>
      
      <!-- Single category: break time management -->
      <div class="mb-8">
        <h4 class="text-white mb-6 text-xl">break time management</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            v-for="(displayName, configKey) in configCategories['break time management']"
            :key="configKey"
            class="p-4 text-base border transition-all duration-300 rounded-lg"
            :class="{
              'bg-primary/20 border-primary text-primary': selectedConfigs.includes(configKey),
              'bg-white/5 text-white border-white/20 hover:bg-white/10 hover:border-white/40': !selectedConfigs.includes(configKey)
            }"
            @click="toggleConfig(configKey)"
          >
            {{ displayName }}
          </button>
        </div>
      </div>

      <!-- Selected filters display -->
      <div v-if="selectedConfigs.length > 0" class="mb-6 bg-primary/8 rounded-lg p-4">
        <h5 class="text-primary mb-3 text-lg font-bold">selected filters:</h5>
        <div class="flex flex-wrap gap-2 justify-center">
          <span v-for="config in selectedConfigs" :key="config" class="bg-primary/20 border border-primary/50 rounded-full px-3 py-1 text-sm text-white">
            {{ getConfigDisplayName(config) }}
            <button @click="removeConfig(config)" class="ml-2 text-red-300 hover:text-red-100">&times;</button>
          </span>
        </div>
      </div>

      <div class="flex gap-4 justify-center mt-6">
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
          @click="goBack"
        >
          back
        </button>
        <button 
          class="px-6 py-3 text-base bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold transition flex-1 max-w-[200px]"
          @click="continueToAnalytics"
        >
          view results
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsStartTimeConfigSelection',
  data() {
    return {
      companyId: '',
      selectedConfigs: [],
      
      // Only break time management category with 5 fields
      configCategories: {
        'break time management': {
          enable_lunch_break: 'lunch break',
          enable_additional_breaks: 'additional breaks', 
          enable_shift_threshold: 'shift threshold',
          enable_grace_period: 'grace period',
          enable_advance_break_rules: 'advance break rules'
        }
      }
    }
  },
  created() {
    // Get company ID from route params
    this.companyId = this.$route.params.companyId;
    
    // Validate company ID exists
    if (!this.companyId) {
      this.error = 'Invalid company ID';
      this.$router.push('/');
      return;
    }
    
    // Get selected start time from sessionStorage
    this.selectedStartTime = sessionStorage.getItem('selectedStartTime');
    if (!this.selectedStartTime) {
      this.error = 'No start time selected';
      this.$router.push(`/shifts-start-time-input/${this.companyId}`);
      return;
    }
  },
  methods: {
    toggleConfig(configName) {
      const index = this.selectedConfigs.indexOf(configName);
      if (index > -1) {
        this.selectedConfigs.splice(index, 1);
      } else {
        this.selectedConfigs.push(configName);
      }
    },
    removeConfig(configName) {
      const index = this.selectedConfigs.indexOf(configName);
      if (index > -1) {
        this.selectedConfigs.splice(index, 1);
      }
    },
    getConfigDisplayName(configName) {
      return this.configCategories['break time management'][configName] || configName;
    },
    continueToAnalytics() {
      // Store selected configs in sessionStorage
      sessionStorage.setItem('selectedShiftConfigs', JSON.stringify(this.selectedConfigs));
      sessionStorage.setItem('selectedShiftConfigCategory', 'break time management');
      
      // Navigate to analytics view
      const startTime = sessionStorage.getItem('selectedStartTime') || '0800';
      this.$router.push(`/shifts-start-time-analytics/${this.companyId}/${startTime}`);
    },
    goBack() {
      this.$router.push(`/shifts-start-time-input/${this.companyId}`);
    }
  }
}
</script> 