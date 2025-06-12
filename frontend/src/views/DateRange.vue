<template>
  <div class="date-range-container">
    <h1 class="page-title">Select Date Range</h1>
    <div class="content-card">
      <div class="info-section">
        <h3>Company ID: {{ companyId }}</h3>
        <h3>Employee ID: {{ employeeId === 'all' ? 'All Employees' : employeeId }}</h3>
      </div>
      <h3>Choose Period</h3>
      <div class="form-group">
        <label>From:</label>
        <select 
          class="form-control"
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
      <div class="form-group">
        <label>To:</label>
        <select 
          class="form-control"
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
        class="btn btn-grad-blue"
        @click="submitDateRange"
        :disabled="!selectedFromDate || !selectedToDate"
      >
        View Analytics
      </button>
      <div v-if="error" class="error-message">{{ error }}</div>
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

<style scoped>
.date-range-container {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
}

.page-title {
  font-family: 'Zilla Slab', serif;
  color: #fff;
  margin-bottom: 2rem;
  font-size: 2.5rem;
  text-align: center;
}

.content-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.content-card h3 {
  color: #24c2ab;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #b1bacd;
  font-size: 0.9rem;
}

.form-control {
  font-size: 1rem;
  height: 48px;
}

.error-message {
  color: #ff6060;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.btn {
  padding: 12px 32px;
  font-size: 1rem;
  width: 100%;
  max-width: 200px;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.info-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-section h3 {
  color: #24c2ab;
  margin-bottom: 0.75rem;
  font-size: 1.25rem;
}

.info-section h3:last-child {
  margin-bottom: 0;
}
</style> 