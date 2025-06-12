<template>
  <div class="analytics-container">
    <h1 class="page-title">Payroll Analytics</h1>
    <div class="analytics-content">
      <div class="analytics-card">
        <div class="period-info">
          <h3>Employee ID: {{ employeeId }}</h3>
          <h4>Period: {{ formatDate(periodFrom) }} - {{ formatDate(periodTo) }}</h4>
        </div>
        <div class="chart-container">
          <Bar :data="chartData" :options="chartOptions" />
        </div>
        <div class="salary-details">
          <div v-for="(value, key) in salaryData" :key="key" class="salary-item" v-if="value > 0">
            <span class="label">{{ formatLabel(key) }}:</span>
            <span class="amount">{{ formatCurrency(value) }}</span>
          </div>
          <div class="salary-item total">
            <span class="label">Total:</span>
            <span class="amount">{{ formatCurrency(totalSalary) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, LogarithmicScale } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, LogarithmicScale, BarElement, Title, Tooltip, Legend)

export default defineComponent({
  name: 'Analytics',
  components: { Bar },
  data() {
    return {
      loading: true,
      error: null,
      analytics: {
        basic: 0,
        nsd: 0,
        ot: 0,
        holiday: 0,
        paid_leave: 0,
        allowances: 0,
        deminimis: 0,
        bonuses: 0,
        other_comp: 0,
        hazard_pay: 0,
        retro: 0,
        adj: 0,
        total_salary: 0,
        gross_pay: 0,
        payslip_count: 0,
        is_verified: false
      },
      baseYAxisMax: 40000,
      componentColors: {
        basic: '#9b59b6',      // Purple
        nsd: '#4a90e2',        // Blue
        ot: '#24c2ab',         // Teal
        holiday: '#e74c3c',    // Red
        paid_leave: '#f1c40f', // Yellow
        allowances: '#2ecc71', // Green
        deminimis: '#e67e22',  // Orange
        bonuses: '#1abc9c',    // Light Teal
        other_comp: '#3498db', // Light Blue
        hazard_pay: '#8e44ad', // Dark Purple
        retro: '#c0392b',      // Dark Red
        adj: '#f39c12'         // Dark Yellow
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
      const aggregationType = this.$route.params.aggregationType || 'single';
      
      if (aggregationType === 'separate' && this.analytics.periods) {
        // For separate view, create period-based stacked bars
        const periods = this.analytics.periods;
        
        // Get all components that have non-zero values in any period
        const components = Object.keys(this.componentColors).filter(component => 
          periods.some(period => 
            period.analytics[component] > 0
          )
        );
        
        // Create datasets (one for each component)
        const datasets = components.map(component => ({
          label: this.formatLabel(component),
          data: periods.map(period => period.analytics[component] || 0),
          backgroundColor: this.componentColors[component],
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          // Set order based on the first period's values (can be adjusted if needed)
          order: periods[0].analytics[component] || 0
        }));
        
        return {
          labels: periods.map(period => 
            `${this.formatDate(period.period.from)} - ${this.formatDate(period.period.to)}`
          ),
          datasets
        };
      } else {
        // For single period or aggregated view
        const components = Object.entries(this.analytics)
          .filter(([key, value]) => 
            key !== 'total_salary' && 
            value > 0 && 
            typeof value === 'number' &&
            key in this.componentColors
          )
          .sort((a, b) => a[1] - b[1]);

        return {
          labels: components.map(([key]) => this.formatLabel(key)),
          datasets: [{
            data: components.map(([_, value]) => value),
            backgroundColor: components.map(([key]) => this.componentColors[key]),
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1
          }]
        };
      }
    },
    salaryData() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      
      if (aggregationType === 'separate' && this.analytics.periods) {
        // For separate view, sum up all periods
        const sums = {
          basic: 0,
          nsd: 0,
          ot: 0,
          holiday: 0,
          paid_leave: 0,
          allowances: 0,
          deminimis: 0,
          bonuses: 0,
          other_comp: 0,
          hazard_pay: 0,
          retro: 0,
          adj: 0
        };
        
        this.analytics.periods.forEach(period => {
          Object.entries(period.analytics).forEach(([key, value]) => {
            if (key !== 'total_salary') {
              sums[key] = (sums[key] || 0) + value;
            }
          });
        });
        
        return sums;
      } else {
        // For single/aggregate view, use analytics directly
        return {
          basic: this.analytics.basic,
          nsd: this.analytics.nsd,
          ot: this.analytics.ot,
          holiday: this.analytics.holiday,
          paid_leave: this.analytics.paid_leave,
          allowances: this.analytics.allowances,
          deminimis: this.analytics.deminimis,
          bonuses: this.analytics.bonuses,
          other_comp: this.analytics.other_comp,
          hazard_pay: this.analytics.hazard_pay,
          retro: this.analytics.retro,
          adj: this.analytics.adj
        };
      }
    },
    totalSalary() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      
      if (aggregationType === 'separate' && this.analytics.periods) {
        return this.analytics.periods.reduce((sum, period) => 
          sum + period.analytics.total_salary, 0
        );
      } else {
        return this.analytics.total_salary;
      }
    },
    dynamicYAxisMax() {
      const fromDate = new Date(this.periodFrom);
      const toDate = new Date(this.periodTo);
      const aggregationType = this.$route.params.aggregationType || 'single';
      
      // For single period view, always use base scale
      if (aggregationType === 'single') {
        return this.baseYAxisMax;
      }
      
      // For aggregate/separate views, calculate number of periods
      const daysDiff = Math.ceil((toDate - fromDate) / (1000 * 60 * 60 * 24));
      const numPeriods = Math.ceil(daysDiff / 14); // Each period is roughly 2 weeks
      
      // Linear scaling: 40k per period
      return this.baseYAxisMax * numPeriods;
    },
    chartOptions() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      
      const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            type: 'logarithmic',
            display: true,
            min: 0,
            max: this.dynamicYAxisMax,
            ticks: {
              color: '#fff',
              font: {
                family: "'Open Sans', sans-serif",
                size: 12
              }
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          x: {
            ticks: {
              color: '#fff',
              font: {
                family: "'Open Sans', sans-serif",
                size: 12
              },
              maxRotation: 45,
              minRotation: 45
            },
            grid: {
              display: false
            }
          }
        },
        plugins: {
          legend: {
            display: aggregationType === 'separate',
            position: 'right',
            labels: {
              color: '#fff',
              font: {
                family: "'Open Sans', sans-serif",
                size: 12
              }
            }
          },
          tooltip: {
            enabled: true,
            mode: aggregationType === 'separate' ? 'nearest' : 'index',
            intersect: false,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            titleFont: {
              family: "'Open Sans', sans-serif",
              size: 12
            },
            bodyColor: '#fff',
            bodyFont: {
              family: "'Open Sans', sans-serif",
              size: 12
            },
            padding: 10,
            callbacks: {
              label: function(context) {
                const label = context.dataset.label || '';
                const value = context.raw.toLocaleString('en-US');
                return `${label}: ${value}`;
              }
            }
          }
        }
      };

      if (aggregationType === 'separate') {
        baseOptions.scales.x.stacked = true;
        baseOptions.scales.y.stacked = true;
      }

      return baseOptions;
    }
  },
  methods: {
    formatLabel(key) {
      const labels = {
        basic: 'Basic Pay',
        nsd: 'Night Differential',
        ot: 'Overtime',
        holiday: 'Holiday Pay',
        paid_leave: 'Paid Leave',
        allowances: 'Allowances',
        deminimis: 'De Minimis',
        bonuses: 'Bonuses',
        other_comp: 'Other Compensation',
        hazard_pay: 'Hazard Pay',
        retro: 'Retro Pay',
        adj: 'Adjustments'
      };
      return labels[key] || key;
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US').format(value)
    },
    async fetchAnalytics() {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetch(`/api/analytics/${this.companyId}/${this.employeeId}/${this.periodFrom}/${this.periodTo}/${this.$route.params.aggregationType || 'single'}`);
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to fetch analytics data');
        }
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        this.analytics = data;
      } catch (err) {
        this.error = err.message;
        this.analytics = {
          basic: 0,
          nsd: 0,
          ot: 0,
          holiday: 0,
          paid_leave: 0,
          allowances: 0,
          deminimis: 0,
          bonuses: 0,
          other_comp: 0,
          hazard_pay: 0,
          retro: 0,
          adj: 0,
          total_salary: 0
        };
      } finally {
        this.loading = false;
      }
    },
    getStackedDatasets() {
      // Get non-zero components sorted by value
      const components = Object.entries(this.analytics)
        .filter(([key, value]) => 
          key !== 'total_salary' && 
          value > 0 && 
          typeof value === 'number'
        )
        .sort((a, b) => a[1] - b[1]); // Sort by value ascending

      const colors = this.getColors(components.length);
      
      return components.map(([key, value], index) => ({
        label: this.formatLabel(key),
        data: [value],
        backgroundColor: colors[index],
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1
      }));
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
  max-width: 1200px;
}

.period-info {
  text-align: center;
  margin-bottom: 2rem;
}

.period-info h3 {
  color: #24c2ab;
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
}

.period-info h4 {
  color: #b1bacd;
  font-size: 1.2rem;
}

.chart-container {
  height: 60vh;
  margin-bottom: 3rem;
}

.salary-details {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.salary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.salary-item .label {
  font-size: 0.9rem;
  color: #b1bacd;
}

.salary-item .amount {
  font-family: 'Open Sans', sans-serif;
  font-weight: 600;
  color: #fff;
}

.salary-item.total {
  grid-column: 1 / -1;
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(36, 194, 171, 0.1);
  border: 1px solid rgba(36, 194, 171, 0.2);
}

.salary-item.total .label,
.salary-item.total .amount {
  font-size: 1.2rem;
  font-weight: 700;
  color: #24c2ab;
}
</style> 