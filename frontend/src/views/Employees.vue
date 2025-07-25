<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">select employee(s)</h1>
    <div v-if="selectedCategory && selectedFields.length > 0" class="mb-6 bg-primary/8 rounded-lg p-2 px-4 text-primary text-lg flex flex-wrap items-center gap-2 max-w-2xl text-left">
      <span class="font-bold">selected:</span>
      <span class="font-bold text-white">{{ selectedCategoryDisplay }}:</span>
      <span class="text-primary">{{ selectedFieldLabels.join(', ') }}</span>
    </div>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-lg text-center">
      <h3 class="text-primary mb-6 text-2xl">company: {{ companyName || companyId }}</h3>
      
      <!-- Employee Search Section -->
      <div v-if="selectType === 'specific'" class="mb-6">
        <EmployeeSearch
          :company-id="companyId"
          context="payslip"
          placeholder="first or last name"
          @employee-selected="selectEmployee"
          @error="handleSearchError"
        />
      </div>

      <!-- Payroll Group Selection Section -->
      <div v-if="selectType === 'payroll_group'" class="mb-6">
        <label class="block mb-2 text-secondary text-sm">select payroll group:</label>
        <select 
          v-model="selectedPayrollGroup"
          class="w-full h-12 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition"
        >
          <option value="">choose a payroll group</option>
          <option 
            v-for="group in payrollGroups" 
            :key="group"
            :value="group"
          >
            payroll group {{ group }}
          </option>
        </select>
      </div>

      <!-- Secondary Filter Section (Only for All Employees) -->
      <div v-if="selectType === 'all'" class="mb-6">
        <label class="block mb-2 text-secondary text-sm">additional filter (optional):</label>
        <select 
          v-model="selectedFilterType"
          class="w-full h-12 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition mb-3"
        >
          <option value="">no additional filter</option>
          <option value="department">department</option>
          <option value="rank">rank</option>
          <option value="employment_type">employment type</option>
          <option value="position">position</option>
          <option value="cost_center">cost center</option>
          <option value="project">project</option>
          <option value="location_and_offices">location & offices</option>
        </select>

        <!-- Filter Options Dropdown -->
        <div v-if="selectedFilterType && filterOptions.length > 0" class="mb-3">
          <label class="block mb-2 text-secondary text-sm">select {{ getFilterDisplayName(selectedFilterType) }}:</label>
          <select 
            v-model="selectedFilterValue"
            class="w-full h-12 text-base bg-white/10 border border-white/20 text-white rounded focus:outline-none focus:border-primary transition"
          >
            <option 
              v-for="option in filterOptions" 
              :key="option.id"
              :value="option.id"
            >
              {{ option.name }}
            </option>
          </select>
        </div>

        <!-- No Options Message -->
        <div v-if="selectedFilterType && filterOptions.length === 0 && !loadingFilterOptions" class="mb-3 p-3 bg-yellow-500/20 border border-yellow-500/30 rounded text-yellow-300 text-sm">
          no {{ getFilterDisplayName(selectedFilterType) }} defined for this company.
        </div>

        <!-- Loading Message -->
        <div v-if="loadingFilterOptions" class="mb-3 p-3 bg-blue-500/20 border border-blue-500/30 rounded text-blue-300 text-sm">
          loading {{ getFilterDisplayName(selectedFilterType) }}...
        </div>
      </div>

      <!-- Selection Buttons -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center mb-4">
        <button 
          :class="[
            'px-6 py-3 text-base font-semibold w-full transition border-2',
            selectType === 'all' 
              ? 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white border-blue-400 ring-4 ring-blue-300' 
              : 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white border-transparent hover:border-blue-300 hover:ring-2 hover:ring-blue-200'
          ]"
          @click="selectAllEmployees"
        >
          all employees
        </button>
        <button 
          :class="[
            'px-6 py-3 text-base font-semibold w-full transition border-2',
            selectType === 'payroll_group' 
              ? 'bg-purple-500 text-white border-purple-400 ring-4 ring-purple-300' 
              : 'bg-purple-500 text-white border-transparent hover:border-purple-300 hover:ring-2 hover:ring-purple-200'
          ]"
          @click="selectPayrollGroup"
        >
          payroll group
        </button>
        <button 
          :class="[
            'px-6 py-3 text-base font-semibold w-full transition border-2',
            selectType === 'specific' 
              ? 'bg-emerald-500 text-white border-emerald-400 ring-4 ring-emerald-300' 
              : 'bg-emerald-500 text-white border-transparent hover:border-emerald-300 hover:ring-2 hover:ring-emerald-200'
          ]"
          @click="selectSpecificEmployee"
        >
          specific employee
        </button>
      </div>

      <!-- Action Buttons -->
      <div v-if="selectType === 'specific'" class="flex gap-4 justify-center mb-4">
        <button 
          class="px-6 py-3 text-base bg-emerald-500 text-white font-semibold flex-1 max-w-[200px] disabled:opacity-70 disabled:cursor-not-allowed transition"
          @click="selectEmployee(searchQuery)"
          :disabled="!searchQuery"
        >
          select employee
        </button>
      </div>

      <div v-if="selectType === 'payroll_group'" class="flex gap-4 justify-center mb-4">
        <button 
          class="px-6 py-3 text-base bg-emerald-500 text-white font-semibold flex-1 max-w-[200px] disabled:opacity-70 disabled:cursor-not-allowed transition"
          @click="selectPayrollGroupEmployee"
          :disabled="!selectedPayrollGroup"
        >
          select group
        </button>
      </div>

      <!-- Continue Button for All Employees -->
      <div v-if="selectType === 'all'" class="flex gap-4 justify-center mb-4">
        <button 
          class="px-6 py-3 text-base bg-emerald-500 text-white font-semibold flex-1 max-w-[200px] disabled:opacity-70 disabled:cursor-not-allowed transition"
          @click="continueAllEmployees"
        >
          continue
        </button>
      </div>

      <div v-if="error" class="text-red-400 text-sm mt-2">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import EmployeeSearch from '../components/EmployeeSearch.vue'

export default {
  name: 'Employees',
  components: {
    EmployeeSearch
  },
  data() {
    return {
      companyId: '',
      companyName: '',
      selectType: '',
      selectedEmployee: null,
      payrollGroups: [],
      selectedPayrollGroup: '',
      error: null,
      selectedCategory: '',
      selectedFields: [],
      selectedFieldLabels: [],
      selectedCategoryDisplay: '',
      selectedFilterType: '',
      selectedFilterValue: '',
      filterOptions: [],
      loadingFilterOptions: false
    }
  },
  created() {
    // Get company ID from route params and store it
    this.companyId = this.$route.params.companyId;
    // Retrieve company name from sessionStorage
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    // Validate company ID exists
    if (!this.companyId) {
      this.error = 'Invalid company ID';
      this.$router.push('/');
    }
    // Load selected fields and category from sessionStorage
    this.loadSelectedSummary();
    // Load payroll groups
    this.loadPayrollGroups();
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
    async loadPayrollGroups() {
      try {
        const response = await axios.get(`/api/payroll-groups/${this.companyId}`);
        this.payrollGroups = response.data.payroll_groups;
      } catch (err) {
        this.error = 'Failed to load payroll groups';
      }
    },
    selectAllEmployees() {
      this.selectType = 'all';
      // Do not navigate here! Navigation happens on Continue button click.
    },
    continueAllEmployees() {
      // Build query parameters for filters
      const queryParams = {};
      if (this.selectedFilterType && this.selectedFilterValue) {
        const paramName = this.selectedFilterType === 'location_and_offices' ? 'location_id' : `${this.selectedFilterType}_id`;
        queryParams[paramName] = this.selectedFilterValue;
      }
      // Navigate with filter parameters
      this.$router.push({
        path: `/dates/${this.companyId}/all`,
        query: queryParams
      });
    },
    selectSpecificEmployee() {
      this.selectType = 'specific';
    },
    selectPayrollGroup() {
      this.selectType = 'payroll_group';
      this.selectedPayrollGroup = '';
    },
    selectPayrollGroupEmployee() {
      if (!this.selectedPayrollGroup) return;
      
      // Store the payroll group selection in sessionStorage
      sessionStorage.setItem('selectedPayrollGroup', this.selectedPayrollGroup);
      
      // Navigate to dates with payroll group parameter
      this.$router.push(`/dates/${this.companyId}/all?payroll_group_id=${this.selectedPayrollGroup}`);
    },
    handleSearchError(errorMessage) {
      this.error = errorMessage;
    },
    selectEmployee(employee) {
      if (!employee) return;
      
      // Store the selected employee object for consistency
      this.selectedEmployee = employee;
      
      // Store in sessionStorage for access in other views
      sessionStorage.setItem('selectedEmployee', JSON.stringify(employee));
      
      // Navigate to dates using the employee ID
      this.$router.push(`/dates/${this.companyId}/${employee.emp_id}`);
    },
    async loadFilterOptions() {
      this.loadingFilterOptions = true;
      try {
        const response = await axios.get(`/api/settings-options/${this.companyId}/${this.selectedFilterType}`);
        this.filterOptions = response.data.options;
        // Auto-select the first option if available and nothing is selected
        if (this.filterOptions.length > 0 && !this.selectedFilterValue) {
          this.selectedFilterValue = this.filterOptions[0].id;
        }
      } catch (err) {
        this.error = 'Failed to load filter options';
        this.filterOptions = [];
      } finally {
        this.loadingFilterOptions = false;
      }
    },
    getFilterDisplayName(type) {
      const filterNames = {
        department: 'Department',
        rank: 'Rank',
        employment_type: 'Employment Type',
        position: 'Position',
        cost_center: 'Cost Center',
        project: 'Project',
        location_and_offices: 'Location & Offices'
      };
      return filterNames[type] || type;
    }
  },
  watch: {
    // Watch for route changes to update company ID
    '$route.params.companyId': {
      handler(newCompanyId) {
        this.companyId = newCompanyId;
      },
      immediate: true
    },
    // Watch for filter type changes to load options
    selectedFilterType(newType) {
      this.selectedFilterValue = '';
      this.filterOptions = [];
      if (newType) {
        this.loadFilterOptions();
      }
    }
  }
}
</script> 