<template>
  <div class="aggregation-container">
    <h1 class="page-title">Multiple Pay Periods Detected</h1>
    <div class="content-card">
      <div class="info-section">
        <h3>Company ID: {{ companyId }}</h3>
        <h3>Employee ID: {{ employeeId === 'all' ? 'All Employees' : employeeId }}</h3>
        <h3>Period: {{ formatDate(periodFrom) }} - {{ formatDate(periodTo) }}</h3>
      </div>
      <p class="description">
        Your selected date range contains multiple pay periods. 
        How would you like to view the data?
      </p>
      <div class="buttons">
        <button 
          class="btn btn-grad-blue"
          @click="selectAggregation('aggregate')"
        >
          Aggregate Data
          <small>View combined totals for all periods</small>
        </button>
        <button 
          class="btn btn-green"
          @click="selectAggregation('separate')"
        >
          Separate Data
          <small>View each period individually</small>
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

<style scoped>
.aggregation-container {
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
  max-width: 600px;
  text-align: center;
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

.description {
  color: #fff;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn {
  padding: 1.5rem;
  font-size: 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  transition: transform 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn small {
  display: block;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  opacity: 0.8;
}
</style> 