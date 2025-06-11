<template>
  <div class="analytics-container">
    <h1 class="page-title">Payroll Analytics</h1>
    <div class="analytics-content">
      <div class="analytics-card">
        <h3>Salary Breakdown</h3>
        <div class="chart-container">
          <Pie :data="chartData" :options="chartOptions" />
        </div>
        <div class="salary-details">
          <div class="salary-item">
            <span class="label">Basic Pay:</span>
            <span class="amount">₱{{ formatCurrency(salaryData.basic || 0) }}</span>
          </div>
          <div class="salary-item">
            <span class="label">Night Differential:</span>
            <span class="amount">₱{{ formatCurrency(salaryData.nsd || 0) }}</span>
          </div>
          <div class="salary-item">
            <span class="label">Overtime:</span>
            <span class="amount">₱{{ formatCurrency(salaryData.ot || 0) }}</span>
          </div>
          <div class="salary-item">
            <span class="label">Holiday Pay:</span>
            <span class="amount">₱{{ formatCurrency(salaryData.holiday || 0) }}</span>
          </div>
          <div class="salary-item">
            <span class="label">Retro Pay:</span>
            <span class="amount">₱{{ formatCurrency(salaryData.retro || 0) }}</span>
          </div>
          <div class="salary-item">
            <span class="label">Adjustments:</span>
            <span class="amount">₱{{ formatCurrency(salaryData.adj || 0) }}</span>
          </div>
          <div class="salary-item total">
            <span class="label">Total:</span>
            <span class="amount">₱{{ formatCurrency(totalSalary) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

export default defineComponent({
  name: 'Analytics',
  components: { Pie },
  data() {
    return {
      loading: true,
      error: null,
      analytics: {
        basic: 0,
        nsd: 0,
        ot: 0,
        holiday: 0,
        retro: 0,
        adj: 0,
        total_salary: 0,
        gross_pay: 0,
        payslip_count: 0,
        is_verified: false
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#fff',
              font: {
                family: "'Open Sans', sans-serif",
                size: 12
              }
            }
          }
        }
      }
    }
  },
  computed: {
    companyId() {
      return this.$route.params.companyId
    },
    employeeId() {
      return this.$route.params.employeeId
    },
    periodFrom() {
      return this.$route.params.periodFrom
    },
    periodTo() {
      return this.$route.params.periodTo
    },
    chartData() {
      return {
        labels: ['Basic Pay', 'Night Differential', 'Overtime', 'Holiday Pay', 'Retro Pay', 'Adjustments'],
        datasets: [{
          data: [
            this.analytics.basic,
            this.analytics.nsd,
            this.analytics.ot,
            this.analytics.holiday,
            this.analytics.retro,
            this.analytics.adj
          ],
          backgroundColor: [
            '#24c2ab',  // Green
            '#6693fa',  // Blue
            '#fe8dab',  // Pink
            '#faae72',  // Orange
            '#c88eff',  // Purple
            '#b1bacd'   // Gray
          ]
        }]
      }
    },
    salaryData() {
      return {
        basic: this.analytics.basic,
        nsd: this.analytics.nsd,
        ot: this.analytics.ot,
        holiday: this.analytics.holiday,
        retro: this.analytics.retro,
        adj: this.analytics.adj
      }
    },
    totalSalary() {
      return this.analytics.total_salary
    }
  },
  methods: {
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'PHP'
      }).format(value)
    },
    async fetchAnalytics() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch(`/api/analytics/${this.companyId}/${this.employeeId}/${this.periodFrom}/${this.periodTo}`)
        if (!response.ok) {
          throw new Error('Failed to fetch analytics data')
        }
        this.analytics = await response.json()
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    this.fetchAnalytics()
  },
  watch: {
    '$route.params': {
      handler() {
        this.fetchAnalytics()
      },
      deep: true
    }
  }
})
</script>

<style scoped>
.analytics-container {
  padding: 2rem;
}

.page-title {
  font-family: 'Zilla Slab', serif;
  color: #fff;
  margin-bottom: 2rem;
  font-size: 2.5rem;
}

.analytics-content {
  display: flex;
  justify-content: center;
}

.analytics-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 800px;
}

.analytics-card h3 {
  color: #24c2ab;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.chart-container {
  margin-bottom: 2rem;
  max-width: 400px;
  margin: 0 auto;
}

.salary-details {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.salary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  color: #b1bacd;
}

.salary-item .label {
  font-size: 0.9rem;
}

.salary-item .amount {
  font-family: 'Open Sans', sans-serif;
  font-weight: 600;
  color: #fff;
}

.salary-item.total {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.salary-item.total .label,
.salary-item.total .amount {
  font-size: 1.1rem;
  font-weight: 700;
  color: #24c2ab;
}
</style> 