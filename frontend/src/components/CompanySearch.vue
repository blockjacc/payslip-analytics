<template>
  <div class="mb-6 relative">
    <input 
      type="text" 
      class="text-center text-lg h-12 w-full rounded border border-white/20 bg-white/10 text-white placeholder-white/50 focus:outline-none focus:border-primary transition"
      v-model="searchQuery"
      :placeholder="placeholder"
      @input="debouncedSearch"
    >
    <div class="absolute top-full left-0 right-0 bg-primary/10 border border-primary/20 rounded-lg mt-1 max-h-[200px] overflow-y-auto z-50 backdrop-blur-md shadow-lg" v-if="filteredCompanies.length > 0">
      <div 
        v-for="company in filteredCompanies" 
        :key="company.company_id"
        class="p-3 cursor-pointer transition-all duration-200 text-white border-b border-primary/20 text-left text-lg hover:bg-primary/20 hover:translate-x-1 last:border-b-0"
        @click="selectCompany(company)"
      >
        {{ company.company_name }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CompanySearch',
  props: {
    placeholder: {
      type: String,
      default: 'search company name...'
    }
  },
  data() {
    return {
      searchQuery: '',
      allCompanies: [],
      filteredCompanies: [],
      searchTimeout: null
    }
  },
  created() {
    this.fetchCompanies();
  },
  methods: {
    async fetchCompanies() {
      try {
        // Try to fetch from backend; fallback to static if needed
        const response = await axios.get('/api/companies');
        this.allCompanies = response.data.companies || [];
      } catch (err) {
        // Fallback: static example list
        this.allCompanies = [
          { company_id: 1, company_name: 'Acme Corporation' },
          { company_id: 2, company_name: 'Globex Inc.' },
          { company_id: 3, company_name: 'Initech' }
        ];
      }
    },
    debouncedSearch() {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      this.searchTimeout = setTimeout(() => {
        this.filterCompanies();
      }, 300);
    },
    filterCompanies() {
      const query = this.searchQuery.trim().toLowerCase();
      if (query.length < 2) {
        this.filteredCompanies = [];
        return;
      }
      this.filteredCompanies = this.allCompanies.filter(company =>
        company.company_name.toLowerCase().includes(query)
      );
    },
    selectCompany(company) {
      if (!company) return;
      this.filteredCompanies = [];
      this.searchQuery = company.company_name;
      this.$emit('company-selected', company);
    },
    resetSearch() {
      this.searchQuery = '';
      this.filteredCompanies = [];
    }
  },
  expose: ['resetSearch']
}
</script> 