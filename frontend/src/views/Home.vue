<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">welcome to the ashima analytics portal</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-md text-center">
      <h3 class="text-primary mb-6 text-2xl">enter company</h3>
      <div class="mb-6">
        <CompanySearch 
          placeholder="search company name..."
          @company-selected="onCompanySelected"
        />
        <div v-if="error" class="text-red-400 text-sm mt-2">{{ error }}</div>
      </div>
      <button 
        class="px-8 py-3 text-lg rounded bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold disabled:opacity-70 disabled:cursor-not-allowed transition"
        @click="validateCompany"
        :disabled="!selectedCompany || loading"
      >
        {{ loading ? 'validating...' : 'continue' }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import CompanySearch from '../components/CompanySearch.vue';

export default {
  name: 'Home',
  components: { CompanySearch },
  data() {
    return {
      selectedCompany: null,
      error: '',
      loading: false
    }
  },
  methods: {
    onCompanySelected(company) {
      this.selectedCompany = company;
      this.error = '';
    },
    async validateCompany() {
      if (!this.selectedCompany) return;
      try {
        this.error = '';
        this.loading = true;
        const response = await axios.get(`/api/validate-company/${this.selectedCompany.company_id}`);
        if (response.data.valid) {
          this.$router.push(`/module-selection/${this.selectedCompany.company_id}`);
        } else {
          this.error = 'company does not exist';
        }
      } catch (err) {
        this.error = 'company does not exist';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script> 