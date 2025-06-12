<template>
  <div class="analytics-container">
    <h1 class="page-title">Payroll Analytics</h1>
    <div class="analytics-content">
      <div class="analytics-card">
        <div class="period-info">
          <h3>Employee ID: {{ employeeId }}</h3>
          <h4>Period: {{ formatDate(periodFrom) }} - {{ formatDate(periodTo) }}</h4>
        </div>
        <div class="download-btn-container">
          <button class="btn btn-download" @click="downloadCSV">Download CSV</button>
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
      selectedFields: [],
      fieldDisplayNames: {},
      baseYAxisMax: 40000,
      // Color mapping from payslip_field_colors.txt
      fieldColors: {
        // Amounts
        basic_pay: '#4a90e2',
        regular_pay: '#24c2ab',
        night_diff: '#f1c40f',
        overtime_pay: '#e74c3c',
        sunday_holiday: '#9b59b6',
        allowances: '#2ecc71',
        nt_allowances: '#e67e22',
        hazard_pay: '#8e44ad',
        cola: '#b1bacd',
        service_charge_taxable: '#c0392b',
        service_charge_non_taxable: '#f39c12',
        bonuses: '#1abc9c',
        other_compensation: '#3498db',
        gross_pay: '#e67e22',
        net_amount: '#16a085',
        de_minimis: '#e84393',
        leave_conversion_taxable: '#fdcb6e',
        leave_conversion_non_taxable: '#00b894',
        paid_leave_amount: '#636e72',
        retroactive_total_amount: '#fd79a8',
        absences: '#00cec9',
        employee_boost_amount: '#6c5ce7',
        tardiness_pay: '#d35400',
        undertime_pay: '#00b894',
        advance_amount: '#fdcb6e',
        // Hours
        regular_days: '#00b894',
        days_absent: '#fdcb6e',
        ot_no_hours: '#e17055',
        retroactive_total_hours: '#00b894',
        employee_total_hours_service_charge_val: '#00cec9',
        // Taxes & Deductions
        pp_sss: '#636e72',
        pp_philhealth: '#00b894',
        pp_pagibig: '#fdcb6e',
        pp_withholding_tax: '#e17055',
        pp_other_deductions: '#e84393',
        voluntary_contributions: '#6c5ce7'
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
        const periods = this.analytics.periods;
        // Use only selected fields
        const components = this.selectedFields.filter(field =>
          periods.some(period => period.analytics[field] > 0)
        );
        const datasets = components.map(field => ({
          label: this.formatLabel(field),
          data: periods.map(period => period.analytics[field] || 0),
          backgroundColor: this.fieldColors[field] || '#24c2ab',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          order: periods[0].analytics[field] || 0
        }));
        return {
          labels: periods.map(period =>
            `${this.formatDate(period.period.from)} - ${this.formatDate(period.period.to)}`
          ),
          datasets
        };
      } else {
        // For single period or aggregated view
        const components = this.selectedFields.filter(field =>
          this.analytics[field] > 0
        );
        return {
          labels: components.map(field => this.formatLabel(field)),
          datasets: [{
            data: components.map(field => this.analytics[field] || 0),
            backgroundColor: components.map(field => this.fieldColors[field] || '#24c2ab'),
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1
          }]
        };
      }
    },
    salaryData() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      if (aggregationType === 'separate' && this.analytics.periods) {
        // Sum up only selected fields
        const sums = {};
        this.selectedFields.forEach(field => { sums[field] = 0; });
        this.analytics.periods.forEach(period => {
          this.selectedFields.forEach(field => {
            sums[field] += period.analytics[field] || 0;
          });
        });
        return sums;
      } else {
        // Use analytics directly, only for selected fields
        const result = {};
        this.selectedFields.forEach(field => {
          result[field] = this.analytics[field] || 0;
        });
        return result;
      }
    },
    totalSalary() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      if (aggregationType === 'separate' && this.analytics.periods) {
        return this.selectedFields.reduce((sum, field) => {
          return sum + this.analytics.periods.reduce((pSum, period) => pSum + (period.analytics[field] || 0), 0);
        }, 0);
      } else {
        return this.selectedFields.reduce((sum, field) => sum + (this.analytics[field] || 0), 0);
      }
    },
    dynamicYAxisMax() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      let maxValue = 0;
      if (aggregationType === 'separate' && this.analytics.periods) {
        // Find the highest value among all selected fields and all periods
        this.analytics.periods.forEach(period => {
          this.selectedFields.forEach(field => {
            const value = period.analytics[field] || 0;
            if (value > maxValue) maxValue = value;
          });
        });
      } else {
        // Find the highest value among all selected fields in the current analytics
        this.selectedFields.forEach(field => {
          const value = this.analytics[field] || 0;
          if (value > maxValue) maxValue = value;
        });
      }
      // If maxValue is 0, set a default (e.g., 1000) to avoid log scale issues
      return maxValue > 0 ? maxValue : 1000;
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
    async fetchFieldDisplayNames() {
      try {
        const response = await fetch('/api/payslip-fields');
        const data = await response.json();
        
        // Combine all field display names
        this.fieldDisplayNames = {
          ...data.amount_fields,
          ...data.hour_fields,
          ...data.tax_fields
        };
      } catch (err) {
        console.error('Failed to fetch field display names:', err);
      }
    },
    formatLabel(key) {
      // If we have a display name from the backend, use it
      if (this.fieldDisplayNames[key]) {
        return this.fieldDisplayNames[key];
      }
      
      // Otherwise fall back to the hardcoded labels
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
        // Get selected fields from sessionStorage or use defaults
        const selectedFields = this.selectedFields.length > 0 
          ? this.selectedFields 
          : ['basic_pay', 'regular_pay', 'gross_pay', 'net_amount'];
        
        // Create URL with selected fields as query parameter
        const fieldsParam = encodeURIComponent(JSON.stringify(selectedFields));
        const url = `/api/analytics/${this.companyId}/${this.employeeId}/${this.periodFrom}/${this.periodTo}/${this.$route.params.aggregationType || 'single'}?fields=${fieldsParam}`;
        
        const response = await fetch(url);
        
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
    },
    downloadCSV() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      let csv = '';
      // Header row
      if (aggregationType === 'separate' && this.analytics.periods) {
        csv += 'Period From,Period To';
        this.selectedFields.forEach(field => {
          csv += ',' + this.formatLabel(field);
        });
        csv += '\n';
        // Data rows
        this.analytics.periods.forEach(period => {
          csv += `${period.period.from},${period.period.to}`;
          this.selectedFields.forEach(field => {
            csv += ',' + (period.analytics[field] !== undefined ? period.analytics[field] : '');
          });
          csv += '\n';
        });
      } else {
        // Single/Aggregate view
        csv += 'Field,Value\n';
        this.selectedFields.forEach(field => {
          csv += `${this.formatLabel(field)},${this.analytics[field] !== undefined ? this.analytics[field] : ''}\n`;
        });
      }
      // Download logic
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_${this.companyId}_${this.employeeId}_${this.periodFrom}_${this.periodTo}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }
  },
  mounted() {
    // Load selected fields from sessionStorage
    const storedFields = sessionStorage.getItem('selectedPayslipFields');
    if (storedFields) {
      this.selectedFields = JSON.parse(storedFields);
    } else {
      // Default to some basic fields if nothing was selected
      this.selectedFields = ['basic_pay', 'regular_pay', 'gross_pay', 'net_amount'];
    }
    
    // Fetch field display names
    this.fetchFieldDisplayNames();
    
    // Fetch analytics data
    this.fetchAnalytics();
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

.download-btn-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.btn-download {
  background: #24c2ab;
  color: #fff;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-download:hover {
  background: #1abc9c;
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