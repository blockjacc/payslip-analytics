<template>
  <div class="mb-6 relative">
    <input 
      type="text" 
      class="text-center text-lg h-12 w-full rounded border border-white/20 bg-white/10 text-white placeholder-white/50 focus:outline-none focus:border-primary transition"
      v-model="searchQuery"
      :placeholder="placeholder"
      @input="debouncedSearch"
    >
    <div class="absolute top-full left-0 right-0 bg-primary/10 border border-primary/20 rounded-lg mt-1 max-h-[200px] overflow-y-auto z-50 backdrop-blur-md shadow-lg" v-if="filteredEmployees.length > 0">
      <div 
        v-for="employee in filteredEmployees" 
        :key="employee.emp_id"
        class="p-3 cursor-pointer transition-all duration-200 text-white border-b border-primary/20 text-left text-lg hover:bg-primary/20 hover:translate-x-1 last:border-b-0"
        @click="selectEmployee(employee)"
      >
        {{ employee.first_name }} {{ employee.last_name }} ({{ employee.emp_id }})
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EmployeeSearch',
  props: {
    companyId: {
      type: [String, Number],
      required: true
    },
    placeholder: {
      type: String,
      default: 'first or last name'
    },
    context: {
      type: String,
      default: 'all',
      validator: value => ['shifts', 'payslip', 'all'].includes(value)
    },
    limit: {
      type: Number,
      default: 10
    }
  },
  data() {
    return {
      searchQuery: '',
      filteredEmployees: [],
      searchTimeout: null
    }
  },
  methods: {
    debouncedSearch() {
      // Clear any existing timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      
      // Set a new timeout
      this.searchTimeout = setTimeout(() => {
        if (this.searchQuery && this.searchQuery.length >= 2) {
          this.searchEmployeesByName();
        } else {
          this.filteredEmployees = [];
        }
      }, 300); // 300ms delay
    },
    async searchEmployeesByName() {
      if (!this.searchQuery || this.searchQuery.length < 2) {
        this.filteredEmployees = [];
        return;
      }
      
      try {
        const response = await axios.get(
          `/api/search-employees-by-name/${this.companyId}/${this.searchQuery}`,
          {
            params: {
              context: this.context,
              limit: this.limit
            }
          }
        );
        
        this.filteredEmployees = response.data.employees || [];
        
      } catch (err) {
        console.error('Failed to search employees:', err);
        this.filteredEmployees = [];
        this.$emit('error', 'Failed to search employees');
      }
    },
    selectEmployee(employee) {
      if (!employee) return;
      
      // Clear search state
      this.filteredEmployees = [];
      this.searchQuery = '';
      
      // Emit the selected employee to parent component
      this.$emit('employee-selected', employee);
    },
    resetSearch() {
      this.searchQuery = '';
      this.filteredEmployees = [];
    }
  },
  // Expose methods for parent components to use
  expose: ['resetSearch']
}
</script> 