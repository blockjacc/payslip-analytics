<template>
  <div class="field-selection-container">
    <h1 class="page-title">Select Fields to Analyze</h1>
    <div class="content-card">
      <h3>Company ID: {{ companyId }}</h3>
      
      <!-- Step 1: Category Selection -->
      <div v-if="currentStep === 1" class="category-selection">
        <h4>Select a category to analyze:</h4>
        <div class="category-buttons">
          <button 
            class="btn category-btn"
            :class="{ 'selected': selectedCategory === 'AMOUNTS' }"
            @click="selectCategory('AMOUNTS')"
          >
            Amounts
          </button>
          <button 
            class="btn category-btn"
            :class="{ 'selected': selectedCategory === 'HOURS' }"
            @click="selectCategory('HOURS')"
          >
            Hours
          </button>
          <button 
            class="btn category-btn"
            :class="{ 'selected': selectedCategory === 'TAXES' }"
            @click="selectCategory('TAXES')"
          >
            Taxes & Deductions
          </button>
        </div>
        
        <div class="buttons">
          <button 
            class="btn btn-back"
            @click="goBack"
          >
            Back
          </button>
          <button 
            class="btn btn-grad-blue"
            @click="goToFieldSelection"
            :disabled="!selectedCategory"
          >
            Continue
          </button>
        </div>
      </div>
      
      <!-- Step 2: Field Selection -->
      <div v-if="currentStep === 2" class="field-selection">
        <h4>Select fields to analyze from {{ getCategoryDisplayName(selectedCategory) }}:</h4>
        
        <div class="field-list">
          <div 
            v-for="(displayName, fieldName) in getCurrentCategoryFields()" 
            :key="fieldName"
            class="field-item"
            :class="{ 'selected': isFieldSelected(fieldName) }"
            @click="toggleField(fieldName)"
          >
            {{ displayName }}
          </div>
        </div>
        
        <div class="selection-summary">
          <p>Selected: {{ selectedFields.length }} fields</p>
        </div>
        
        <!-- Selected fields display with delete options -->
        <div v-if="selectedFields.length > 0" class="selected-fields-display">
          <h5>Selected Fields:</h5>
          <div class="selected-fields-list">
            <div v-for="fieldName in selectedFields" :key="fieldName" class="selected-field-tag">
              <span>{{ getFieldDisplayName(fieldName) }}</span>
              <button class="delete-btn" @click.stop="removeField(fieldName)">×</button>
            </div>
          </div>
        </div>
        
        <div class="buttons">
          <button 
            class="btn btn-back"
            @click="currentStep = 1"
          >
            Back
          </button>
          <button 
            class="btn btn-grad-blue"
            @click="continueToEmployees"
            :disabled="selectedFields.length === 0"
          >
            Continue
          </button>
        </div>
      </div>
      
      <div v-if="error" class="error-message">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'FieldSelection',
  data() {
    return {
      companyId: '',
      currentStep: 1,
      selectedCategory: null,
      selectedFields: [],
      amountFields: {},
      hourFields: {},
      taxFields: {},
      error: null,
      loading: false
    }
  },
  created() {
    // Get company ID from route params
    this.companyId = this.$route.params.companyId;
    
    // Validate company ID exists
    if (!this.companyId) {
      this.error = 'Invalid company ID';
      this.$router.push('/');
      return;
    }
    
    // Load field definitions
    this.loadFieldDefinitions();
  },
  methods: {
    async loadFieldDefinitions() {
      try {
        this.loading = true;
        // Fetch field definitions from the backend
        const response = await axios.get('/api/payslip-fields');
        
        // Populate field categories
        this.amountFields = response.data.amount_fields || {};
        this.hourFields = response.data.hour_fields || {};
        this.taxFields = response.data.tax_fields || {};
      } catch (err) {
        this.error = 'Failed to load field definitions';
        console.error('Error loading field definitions:', err);
      } finally {
        this.loading = false;
      }
    },
    selectCategory(category) {
      this.selectedCategory = category;
    },
    goToFieldSelection() {
      if (!this.selectedCategory) {
        this.error = 'Please select a category';
        return;
      }
      
      // Clear any previously selected fields
      this.selectedFields = [];
      
      // Move to field selection step
      this.currentStep = 2;
    },
    getCurrentCategoryFields() {
      switch (this.selectedCategory) {
        case 'AMOUNTS':
          return this.amountFields;
        case 'HOURS':
          return this.hourFields;
        case 'TAXES':
          return this.taxFields;
        default:
          return {};
      }
    },
    getCategoryDisplayName(category) {
      switch (category) {
        case 'AMOUNTS':
          return 'Amounts';
        case 'HOURS':
          return 'Hours';
        case 'TAXES':
          return 'Taxes & Deductions';
        default:
          return '';
      }
    },
    toggleField(fieldName) {
      const index = this.selectedFields.indexOf(fieldName);
      if (index === -1) {
        // Field is not selected, add it
        this.selectedFields.push(fieldName);
      } else {
        // Field is already selected, remove it
        this.selectedFields.splice(index, 1);
      }
    },
    isFieldSelected(fieldName) {
      return this.selectedFields.includes(fieldName);
    },
    goBack() {
      this.$router.push('/');
    },
    continueToEmployees() {
      if (this.selectedFields.length === 0) {
        this.error = 'Please select at least one field to analyze';
        return;
      }
      
      // Store selected fields and category in sessionStorage
      sessionStorage.setItem('selectedPayslipFields', JSON.stringify(this.selectedFields));
      sessionStorage.setItem('selectedPayslipCategory', this.selectedCategory);
      
      // Navigate to employees selection
      this.$router.push(`/employees/${this.companyId}`);
    },
    getFieldDisplayName(fieldName) {
      // Find the display name based on the field's category
      switch (this.selectedCategory) {
        case 'AMOUNTS':
          return this.amountFields[fieldName] || fieldName;
        case 'HOURS':
          return this.hourFields[fieldName] || fieldName;
        case 'TAXES':
          return this.taxFields[fieldName] || fieldName;
        default:
          return fieldName;
      }
    },
    removeField(fieldName) {
      const index = this.selectedFields.indexOf(fieldName);
      if (index !== -1) {
        this.selectedFields.splice(index, 1);
      }
    }
  }
}
</script>

<style scoped>
.field-selection-container {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
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
  max-width: 800px;
  text-align: center;
}

.content-card h3 {
  color: #24c2ab;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.content-card h4 {
  color: #fff;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
}

.category-buttons {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.category-btn {
  padding: 1.5rem 1rem;
  font-size: 1.2rem;
  min-width: 180px;
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.category-btn:hover {
  background: rgba(36, 194, 171, 0.1);
  transform: translateY(-5px);
}

.category-btn.selected {
  background: rgba(36, 194, 171, 0.2);
  border: 1px solid rgba(36, 194, 171, 0.5);
  font-weight: bold;
}

.field-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 0.5rem;
  margin-bottom: 1.5rem;
}

.field-item {
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  text-align: left;
  font-size: 0.9rem;
  border: 1px solid transparent;
}

.field-item:hover {
  background: rgba(36, 194, 171, 0.1);
  transform: translateX(5px);
}

.field-item.selected {
  background: rgba(36, 194, 171, 0.2);
  border: 1px solid rgba(36, 194, 171, 0.5);
  font-weight: bold;
}

.selection-summary {
  margin: 1rem 0;
  color: #24c2ab;
  font-size: 1.1rem;
}

.buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
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

.btn-back {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Scrollbar styling */
.field-list::-webkit-scrollbar {
  width: 6px;
}

.field-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.field-list::-webkit-scrollbar-thumb {
  background: rgba(36, 194, 171, 0.3);
  border-radius: 10px;
}

.field-list::-webkit-scrollbar-thumb:hover {
  background: rgba(36, 194, 171, 0.5);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .category-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .category-btn {
    width: 100%;
    max-width: 300px;
  }
}

.selected-fields-display {
  margin: 1.5rem 0;
  text-align: left;
}

.selected-fields-display h5 {
  color: #24c2ab;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.selected-fields-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selected-field-tag {
  display: flex;
  align-items: center;
  background: rgba(36, 194, 171, 0.2);
  border: 1px solid rgba(36, 194, 171, 0.5);
  border-radius: 50px;
  padding: 0.25rem 0.75rem;
  font-size: 0.9rem;
  color: #fff;
}

.delete-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.2rem;
  margin-left: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  padding: 0;
  line-height: 1;
}

.delete-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style> 