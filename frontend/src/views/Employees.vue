<template>
  <div class="employees-container">
    <h1 class="page-title">Select Employee</h1>
    <div class="content-card">
      <h3>Company ID: {{ companyId }}</h3>
      <div class="form-group">
        <input 
          type="text" 
          class="form-control"
          v-model="searchQuery"
          placeholder="Enter employee ID or select 'All Employees'"
          @input="debouncedSearch"
        >
        <div class="employee-list" v-if="filteredEmployees.length > 0">
          <div 
            v-for="employee in filteredEmployees" 
            :key="employee"
            class="employee-item"
            @click="selectEmployee(employee)"
          >
            {{ employee }}
          </div>
        </div>
      </div>
      <div class="buttons">
        <button 
          class="btn btn-grad-blue"
          @click="selectAllEmployees"
        >
          All Employees
        </button>
        <button 
          class="btn btn-green"
          @click="selectEmployee(searchQuery)"
          :disabled="!searchQuery"
        >
          Select Employee
        </button>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
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
      searchTimeout: null
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
  },
  methods: {
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

<style scoped>
.employees-container {
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
  position: relative;
}

.form-control {
  text-align: center;
  font-size: 1.2rem;
  height: 48px;
}

.employee-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(36, 194, 171, 0.1);
  border: 1px solid rgba(36, 194, 171, 0.2);
  border-radius: 8px;
  margin-top: 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.employee-item {
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #fff;
  border-bottom: 1px solid rgba(36, 194, 171, 0.2);
  text-align: left;
  font-size: 1.1rem;
}

.employee-item:last-child {
  border-bottom: none;
}

.employee-item:hover {
  background: rgba(36, 194, 171, 0.2);
  transform: translateX(5px);
}

.buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.error-message {
  color: #ff6060;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.btn {
  padding: 12px 24px;
  font-size: 1rem;
  flex: 1;
  max-width: 200px;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style> 