<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">Welcome to Payslip Analytics</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-md text-center">
      <h3 class="text-primary mb-6 text-2xl">Enter Company ID</h3>
      <div class="mb-6">
        <input 
          type="text" 
          class="text-center text-lg h-12 w-full rounded border border-white/20 bg-white/10 text-white placeholder-white/50 focus:outline-none focus:border-primary transition" 
          v-model="companyId"
          placeholder="Enter company ID"
          @keyup.enter="validateCompany"
        >
        <div v-if="error" class="text-red-400 text-sm mt-2">{{ error }}</div>
      </div>
      <button 
        class="px-8 py-3 text-lg rounded bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold disabled:opacity-70 disabled:cursor-not-allowed transition"
        @click="validateCompany"
        :disabled="!companyId || loading"
      >
        {{ loading ? 'Validating...' : 'Continue' }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Home',
  data() {
    return {
      companyId: '',
      error: '',
      loading: false
    }
  },
  methods: {
    async validateCompany() {
      if (!this.companyId) return;
      
      try {
        this.error = '';
        this.loading = true;
        const response = await axios.get(`/api/validate-company/${this.companyId}`);
        if (response.data.valid) {
          this.$router.push(`/field-selection/${this.companyId}`);
        } else {
          this.error = 'Company does not exist';
        }
      } catch (err) {
        this.error = 'Company does not exist';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script> 