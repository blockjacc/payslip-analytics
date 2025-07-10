<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">select shift characteristics</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-4xl text-center mx-auto">
      <h3 class="text-primary mb-6 text-2xl">company id: {{ companyId }}</h3>
      <h4 class="text-primary mb-6 text-lg">shifts starting at: {{ startTime }}</h4>
      
      <!-- Step 1: Category Selection -->
      <div v-if="currentStep === 1" class="category-selection">
        <h4 class="text-white mb-6 text-lg">select a category to analyze:</h4>
        <div class="flex justify-center gap-6 mb-8 flex-col md:flex-row items-center">
          <button 
            class="px-6 py-6 text-lg min-w-[180px] bg-white/5 text-white border border-white/20 transition-all duration-300 hover:bg-primary/10 hover:-translate-y-1"
            :class="{ 'bg-primary/20 border-primary/50 font-bold': selectedCategory === 'BREAK_TIME' }"
            @click="selectCategory('BREAK_TIME')"
          >
            break & time management
          </button>
          <button 
            class="px-6 py-6 text-lg min-w-[180px] bg-white/5 text-white border border-white/20 transition-all duration-300 opacity-50 cursor-not-allowed"
            disabled
          >
            premium pay & compensation
          </button>
          <button 
            class="px-6 py-6 text-lg min-w-[180px] bg-white/5 text-white border border-white/20 transition-all duration-300 opacity-50 cursor-not-allowed"
            disabled
          >
            holiday & rest day policies
          </button>
        </div>
        
        <div class="flex gap-4 justify-center mt-6">
          <button 
            class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
            @click="goBack"
          >
            back
          </button>
          <button 
            class="px-6 py-3 text-base bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold disabled:opacity-70 disabled:cursor-not-allowed transition flex-1 max-w-[200px]"
            @click="goToFieldSelection"
            :disabled="!selectedCategory"
          >
            continue
          </button>
        </div>
      </div>
      
      <!-- Step 2: Field Selection -->
      <div v-if="currentStep === 2" class="field-selection">
        <h4 class="text-white mb-6 text-lg">select characteristics to analyze from {{ getCategoryDisplayName(selectedCategory) }}:</h4>
        
        <div class="flex flex-col gap-2 max-h-[300px] overflow-y-auto pr-2 mb-6">
          <div 
            v-for="(displayName, fieldName) in getCurrentCategoryFields()" 
            :key="fieldName"
            class="p-3 cursor-pointer transition-all duration-200 text-white bg-white/5 rounded-md text-left text-sm border border-transparent hover:bg-primary/10 hover:translate-x-1"
            :class="{ 'bg-primary/20 border-primary/50 font-bold': isFieldSelected(fieldName) }"
            @click="toggleField(fieldName)"
          >
            {{ displayName }}
          </div>
        </div>
        
        <div class="text-primary text-lg mb-4">
          <p>selected: {{ selectedFields.length }} characteristics</p>
        </div>
        
        <!-- Selected fields display with delete options -->
        <div v-if="selectedFields.length > 0" class="mb-6 text-left">
          <h5 class="text-primary mb-2 text-base">selected characteristics:</h5>
          <div class="flex flex-wrap gap-2">
            <div v-for="fieldName in selectedFields" :key="fieldName" class="flex items-center bg-primary/20 border border-primary/50 rounded-full px-3 py-1 text-sm text-white">
              <span>{{ getFieldDisplayName(fieldName) }}</span>
              <button class="bg-none border-none text-white text-lg ml-2 cursor-pointer flex items-center justify-center w-5 h-5 rounded-full p-0 leading-none hover:bg-white/20" @click.stop="removeField(fieldName)">×</button>
            </div>
          </div>
        </div>
        
        <div class="flex gap-4 justify-center mt-6">
          <button 
            class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
            @click="currentStep = 1"
          >
            back
          </button>
          <button 
            class="px-6 py-3 text-base bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold disabled:opacity-70 disabled:cursor-not-allowed transition flex-1 max-w-[200px]"
            @click="continueToAnalytics"
            :disabled="selectedFields.length === 0"
          >
            continue
          </button>
        </div>
      </div>
      
      <div v-if="error" class="text-red-400 text-sm mt-2">{{ error }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsStartTimeConfigSelection',
  data() {
    return {
      companyId: '',
      startTime: '',
      currentStep: 1,
      selectedCategory: null,
      selectedFields: [],
      breakTimeFields: {
        'lunch_break_duration': 'Lunch Break Duration',
        'additional_breaks_schedule': 'Additional Breaks Schedule',
        'shift_threshold_minutes': 'Shift Threshold Minutes',
        'grace_period_settings': 'Grace Period Settings',
        'advanced_break_rules': 'Advanced Break Rules'
      },
      error: null
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
    
    // Get selected start time from sessionStorage
    this.startTime = sessionStorage.getItem('selectedStartTime');
    if (!this.startTime) {
      this.error = 'No start time selected';
      this.$router.push(`/shifts-start-time-input/${this.companyId}`);
      return;
    }
  },
  methods: {
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
        case 'BREAK_TIME':
          return this.breakTimeFields;
        default:
          return {};
      }
    },
    getCategoryDisplayName(category) {
      switch (category) {
        case 'BREAK_TIME':
          return 'Break & Time Management';
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
      this.$router.push(`/shifts-start-time-input/${this.companyId}`);
    },
    continueToAnalytics() {
      if (this.selectedFields.length === 0) {
        this.error = 'Please select at least one characteristic to analyze';
        return;
      }
      
      // Store selected fields and category in sessionStorage
      sessionStorage.setItem('selectedShiftCharacteristics', JSON.stringify(this.selectedFields));
      sessionStorage.setItem('selectedShiftCategory', this.selectedCategory);
      
      // Navigate to analytics - convert time format for URL
      const startTimeForUrl = this.startTime.replace(':', '').substring(0, 4);
      this.$router.push(`/shifts-start-time-analytics/${this.companyId}/${startTimeForUrl}`);
    },
    getFieldDisplayName(fieldName) {
      // Find the display name based on the field's category
      switch (this.selectedCategory) {
        case 'BREAK_TIME':
          return this.breakTimeFields[fieldName] || fieldName;
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