<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">Select Employee</h1>
    <div v-if="selectedCategory && selectedFields.length > 0" class="mb-6 bg-primary/8 rounded-lg p-2 px-4 text-primary text-lg flex flex-wrap items-center gap-2 max-w-2xl text-left">
      <span class="font-bold">Selected:</span>
      <span class="font-bold text-white">{{ selectedCategoryDisplay }}:</span>
      <span class="text-primary">{{ selectedFieldLabels.join(', ') }}</span>
    </div>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-lg text-center">
      <h3 class="text-primary mb-6 text-2xl">Company ID: {{ companyId }}</h3>
      
      <div class="mb-6 relative">
        <input 
          type="text" 
          class="text-center text-lg h-12 w-full rounded border border-white/20 bg-white/10 text-white placeholder-white/50 focus:outline-none focus:border-primary transition"
          v-model="searchQuery"
          placeholder="Enter employee ID or select 'All Employees'"
          @input="debouncedSearch"
        >
        <div class="absolute top-full left-0 right-0 bg-primary/10 border border-primary/20 rounded-lg mt-1 max-h-[200px] overflow-y-auto z-50 backdrop-blur-md shadow-lg" v-if="filteredEmployees.length > 0">
          <div 
            v-for="employee in filteredEmployees" 
            :key="employee"
            class="p-3 cursor-pointer transition-all duration-200 text-white border-b border-primary/20 text-left text-lg hover:bg-primary/20 hover:translate-x-1 last:border-b-0"
            @click="selectEmployee(employee)"
          >
            {{ employee }}
          </div>
        </div>
      </div>
      <div class="flex gap-4 justify-center mb-4">
        <button 
          class="px-6 py-3 text-base bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold flex-1 max-w-[200px] transition"
          @click="selectAllEmployees"
        >
          All Employees
        </button>
        <button 
          class="px-6 py-3 text-base bg-emerald-500 text-white font-semibold flex-1 max-w-[200px] disabled:opacity-70 disabled:cursor-not-allowed transition"
          @click="selectEmployee(searchQuery)"
          :disabled="!searchQuery"
        >
          Select Employee
        </button>
      </div>
      <div v-if="error" class="text-red-400 text-sm mt-2">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Employees',
  data() {
    return {
      companyId: '',
      selectType: 'all',
      searchQuery: '',
      searchResults: [],
      selectedEmployee: null,
      filteredEmployees: [],
      error: null,
      searchTimeout: null,
      selectedCategory: '',
      selectedFields: [],
      selectedFieldLabels: [],
      selectedCategoryDisplay: ''
    }
  },
  created() {
    // Get company ID from route params and store it
    this.companyId = this.$route.params.companyId;
    
    // Validate company ID exists
    if (!this.companyId) {
      this.error = 'Invalid company ID';
      this.$router.push('/');
    }
    
    // Load selected fields and category from sessionStorage
    this.loadSelectedSummary();
  },
  methods: {
    loadSelectedSummary() {
      // Get selected fields
      const storedFields = sessionStorage.getItem('selectedPayslipFields');
      this.selectedFields = storedFields ? JSON.parse(storedFields) : [];
      // Get selected category
      const storedCategory = sessionStorage.getItem('selectedPayslipCategory');
      this.selectedCategory = storedCategory || '';
      // Get field display names from backend
      axios.get('/api/payslip-fields').then(response => {
        const allFields = {
          ...response.data.amount_fields,
          ...response.data.hour_fields,
          ...response.data.tax_fields
        };
        this.selectedFieldLabels = this.selectedFields.map(f => allFields[f] || f);
        // Set display name for category
        switch (this.selectedCategory) {
          case 'AMOUNTS':
            this.selectedCategoryDisplay = 'Amounts';
            break;
          case 'HOURS':
            this.selectedCategoryDisplay = 'Hours';
            break;
          case 'TAXES':
            this.selectedCategoryDisplay = 'Taxes & Deductions';
            break;
          default:
            this.selectedCategoryDisplay = '';
        }
      });
    },
    selectAllEmployees() {
      this.selectType = 'all';
      this.$router.push(`/dates/${this.companyId}/all`);
    },
    selectSpecific() {
      this.selectType = 'specific';
      this.searchQuery = '';
      this.searchResults = [];
    },
    debouncedSearch() {
      // Clear any existing timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      
      // Set a new timeout
      this.searchTimeout = setTimeout(() => {
        this.searchEmployees();
      }, 300); // 300ms delay
    },
    async searchEmployees() {
      if (!this.searchQuery) {
        this.filteredEmployees = [];
        return;
      }
      
      try {
        const response = await axios.get(`/api/search-employees/${this.companyId}/${this.searchQuery}`);
        this.filteredEmployees = response.data.employees;
      } catch (err) {
        this.error = 'Failed to search employees';
      }
    },
    selectEmployee(empId) {
      if (!empId) return;
      
      this.selectedEmployee = empId;
      this.searchQuery = empId;
      this.filteredEmployees = [];
      this.$router.push(`/dates/${this.companyId}/${empId}`);
    }
  },
  watch: {
    // Watch for route changes to update company ID
    '$route.params.companyId': {
      handler(newCompanyId) {
        this.companyId = newCompanyId;
      },
      immediate: true
    }
  }
}
</script> 