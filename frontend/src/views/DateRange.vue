<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">Select Date Range</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-lg text-center">
      <div class="mb-8 pb-6 border-b border-white/10">
        <h3 class="text-primary mb-3 text-xl">Company ID: {{ companyId }}</h3>
        <h3 class="text-primary text-xl">Employee ID: {{ employeeId === 'all' ? 'All Employees' : employeeId }}</h3>
      </div>
      <h3 class="text-primary mb-6 text-2xl">Choose Period</h3>
      <div class="mb-6 text-left">
        <label class="block mb-2 text-secondary text-sm">From:</label>
        <select 
          class="w-full h-12 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition"
          v-model="selectedFromDate"
          @change="updateToDateOptions"
        >
          <option value="">Select start date</option>
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
        <label class="block mb-2 text-secondary text-sm">To:</label>
        <select 
          class="w-full h-12 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition disabled:opacity-50"
          v-model="selectedToDate"
          :disabled="!selectedFromDate"
        >
          <option value="">Select end date</option>
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
        View Analytics
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
      selectedFromDate: '',
      selectedToDate: '',
      error: '',
      fromDates: [],
      toDates: [],
      loading: false
    }
  },
  created() {
    this.companyId = this.$route.params.companyId;
    this.employeeId = this.$route.params.employeeId;
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
        
        const response = await axios.get(endpoint);
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
        
        const response = await axios.get(endpoint);
        const periodFromDates = response.data.period_from_dates;
        
        // Find if there's any period_from date that falls between our selected range
        const selectedFromDate = new Date(this.selectedFromDate);
        const selectedToDate = new Date(this.selectedToDate);
        
        const hasMultiplePeriods = periodFromDates.some(date => {
          const periodFrom = new Date(date);
          return periodFrom > selectedFromDate && periodFrom <= selectedToDate;
        });

        if (hasMultiplePeriods) {
          // Navigate to aggregation choice page
          await this.router.push({
            name: 'AggregationChoice',
            params: {
              companyId: this.companyId,
              employeeId: this.employeeId,
              periodFrom: this.selectedFromDate,
              periodTo: this.selectedToDate
            }
          });
        } else {
          // Navigate directly to analytics
          await this.router.push({
            name: 'Analytics',
            params: {
              companyId: this.companyId,
              employeeId: this.employeeId,
              periodFrom: this.selectedFromDate,
              periodTo: this.selectedToDate,
              aggregationType: 'single'
            }
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