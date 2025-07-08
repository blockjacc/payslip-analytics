<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">shift changes period</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-4xl text-center mx-auto">
      <h3 class="text-primary mb-6 text-2xl">company id: {{ companyId }}</h3>
      
      <!-- Info Text -->
      <div class="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4 mb-6 text-sm text-blue-100">
        <p>Select a date range to find employees whose shift assignments changed during that period.</p>
        <p class="mt-2 text-xs opacity-75">Minimum 2 days required • Maximum 7 days allowed</p>
      </div>

      <!-- Date Range Inputs -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label class="block text-white text-sm font-medium mb-2">From Date</label>
          <input 
            type="date" 
            v-model="fromDate"
            class="w-full p-3 bg-white/5 text-white border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
            :max="maxFromDate"
            @change="validateDates"
          />
        </div>
        <div>
          <label class="block text-white text-sm font-medium mb-2">To Date</label>
          <input 
            type="date" 
            v-model="toDate"
            class="w-full p-3 bg-white/5 text-white border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
            :min="minToDate"
            :max="maxToDate"
            @change="validateDates"
          />
        </div>
      </div>

      <!-- Validation Messages -->
      <div v-if="validationMessage" class="mb-6">
        <div 
          :class="[
            'p-3 rounded-lg text-sm',
            validationMessage.type === 'error' ? 'bg-red-500/20 border border-red-500/30 text-red-100' : 'bg-green-500/20 border border-green-500/30 text-green-100'
          ]"
        >
          {{ validationMessage.text }}
        </div>
      </div>

      <!-- Period Summary -->
      <div v-if="isValidPeriod" class="bg-green-500/20 border border-green-500/30 rounded-lg p-4 mb-6 text-sm text-green-100">
        <p>Period: {{ formatDate(fromDate) }} to {{ formatDate(toDate) }}</p>
        <p>Duration: {{ daysDifference }} days</p>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-4 justify-center mt-6">
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
          @click="goBack"
        >
          back
        </button>
        <button 
          :disabled="!isValidPeriod"
          :class="[
            'px-6 py-3 text-base transition flex-1 max-w-[200px]',
            isValidPeriod 
              ? 'bg-primary text-white hover:bg-primary/80' 
              : 'bg-gray-500/20 text-gray-400 cursor-not-allowed'
          ]"
          @click="analyzeChanges"
        >
          analyze changes
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsChangesDatePicker',
  data() {
    return {
      companyId: '',
      fromDate: '',
      toDate: '',
      validationMessage: null,
      isValidPeriod: false,
      daysDifference: 0
    }
  },
  created() {
    this.companyId = this.$route.params.companyId;
    if (!this.companyId) {
      this.$router.push('/');
      return;
    }
    
    // Set default dates (today and yesterday)
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    
    this.toDate = today.toISOString().split('T')[0];
    this.fromDate = yesterday.toISOString().split('T')[0];
    
    this.validateDates();
  },
  computed: {
    minToDate() {
      if (!this.fromDate) return '';
      const fromDate = new Date(this.fromDate);
      fromDate.setDate(fromDate.getDate() + 1); // At least 1 day after fromDate
      return fromDate.toISOString().split('T')[0];
    },
    maxToDate() {
      if (!this.fromDate) return '';
      const fromDate = new Date(this.fromDate);
      fromDate.setDate(fromDate.getDate() + 7); // At most 7 days after fromDate
      return fromDate.toISOString().split('T')[0];
    },
    maxFromDate() {
      const today = new Date();
      return today.toISOString().split('T')[0];
    }
  },
  methods: {
    validateDates() {
      if (!this.fromDate || !this.toDate) {
        this.validationMessage = {
          type: 'error',
          text: 'Please select both start and end dates'
        };
        this.isValidPeriod = false;
        return;
      }

      const fromDate = new Date(this.fromDate);
      const toDate = new Date(this.toDate);
      const timeDiff = toDate - fromDate;
      const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));

      this.daysDifference = daysDiff;

      if (daysDiff < 1) {
        this.validationMessage = {
          type: 'error',
          text: 'Period must span at least 2 days to detect shift changes'
        };
        this.isValidPeriod = false;
        return;
      }

      if (daysDiff > 7) {
        this.validationMessage = {
          type: 'error',
          text: 'Period cannot exceed 7 days'
        };
        this.isValidPeriod = false;
        return;
      }

      this.validationMessage = {
        type: 'success',
        text: `Valid period: ${daysDiff} days`
      };
      this.isValidPeriod = true;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    },
    analyzeChanges() {
      if (!this.isValidPeriod) return;
      
      this.$router.push(`/shifts-changes-results/${this.companyId}/${this.fromDate}/${this.toDate}`);
    },
    goBack() {
      this.$router.push(`/shifts-schedule-type-selection/${this.companyId}`);
    }
  }
}
</script> 