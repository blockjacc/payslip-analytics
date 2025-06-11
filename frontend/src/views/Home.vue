<template>
  <div class="home-container">
    <h1 class="page-title">Welcome to Payslip Analytics</h1>
    <div class="content-card">
      <h3>Enter Company ID</h3>
      <div class="form-group">
        <input 
          type="text" 
          class="form-control"
          v-model="companyId"
          placeholder="Enter company ID"
          @keyup.enter="validateCompany"
        >
        <div v-if="error" class="error-message">{{ error }}</div>
      </div>
      <button 
        class="btn btn-grad-blue"
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
          this.$router.push(`/employees/${this.companyId}`);
        } else {
          this.error = 'Company does not exist';
        }
      } catch (err) {
        this.error = 'Company does not exist';
        console.error('Error validating company:', err);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.home-container {
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
  max-width: 400px;
  text-align: center;
}

.content-card h3 {
  color: #24c2ab;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-control {
  text-align: center;
  font-size: 1.2rem;
  height: 48px;
}

.error-message {
  color: #ff6060;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.btn {
  padding: 12px 32px;
  font-size: 1rem;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style> 