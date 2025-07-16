<template>
  <div class="flex flex-col items-center justify-center min-h-[80vh] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">shifts by start time</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-lg text-center mx-auto">
      <h3 class="text-primary mb-6 text-2xl">company: {{ companyName || companyId }}</h3>
      
      <div class="mb-6">
        <h4 class="text-white mb-4 text-lg">enter start time:</h4>
        <input 
          v-model="startTime"
          type="time"
          @input="validateTime"
          class="w-full p-4 text-xl bg-white/10 border border-white/20 text-white rounded-lg focus:outline-none focus:border-primary transition text-center"
          placeholder="e.g., 08:00"
        />
        <div class="mt-2 text-sm text-white/70">
          format: HH:MM (24-hour format)
        </div>
      </div>

      <!-- Alternative input for those who prefer text input -->
      <div class="mb-6">
        <div class="text-white/50 text-sm mb-2">or enter as text:</div>
        <input 
          v-model="startTimeText"
          type="text"
          @input="validateTextTime"
          class="w-full p-3 text-lg bg-white/5 border border-white/20 text-white rounded-lg focus:outline-none focus:border-primary transition text-center"
          placeholder="e.g., 0800, 08:00, 8:00 AM"
        />
      </div>

      <!-- Validation Message -->
      <div v-if="validationMessage" class="mb-6">
        <div 
          class="p-3 rounded-lg text-sm"
          :class="{
            'bg-red-500/20 text-red-300': validationMessage.type === 'error',
            'bg-green-500/20 text-green-300': validationMessage.type === 'success'
          }"
        >
          {{ validationMessage.text }}
        </div>
      </div>

      <!-- Preview of normalized time -->
      <div v-if="normalizedTime" class="mb-6">
        <div class="text-primary text-lg">
          <p>searching for shifts starting at: <span class="font-bold">{{ normalizedTime }}</span></p>
        </div>
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
          @click="continueToConfigSelection"
          :disabled="!isValidTime"
        >
          continue
        </button>
      </div>

      <div v-if="error" class="text-red-400 text-sm mt-2">{{ error }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsStartTimeInput',
  data() {
    return {
      companyId: '',
      companyName: '',
      startTime: '',
      startTimeText: '',
      normalizedTime: '',
      validationMessage: null,
      isValidTime: false,
      error: null
    }
  },
  created() {
    // Get company ID from route params
    this.companyId = this.$route.params.companyId;
    // Retrieve company name from sessionStorage
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    // Validate company ID exists
    if (!this.companyId) {
      this.error = 'Invalid company ID';
      this.$router.push('/');
      return;
    }
  },
  methods: {
    validateTime() {
      if (!this.startTime) {
        this.normalizedTime = '';
        this.isValidTime = false;
        this.validationMessage = null;
        return;
      }

      try {
        // For time input, format is already HH:MM
        const [hours, minutes] = this.startTime.split(':').map(num => parseInt(num));
        
        if (hours >= 0 && hours <= 23 && minutes >= 0 && minutes <= 59) {
          this.normalizedTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:00`;
          this.isValidTime = true;
          this.validationMessage = {
            type: 'success',
            text: 'Valid time format'
          };
          // Sync with text input
          this.startTimeText = this.startTime;
        } else {
          throw new Error('Invalid time range');
        }
      } catch (e) {
        this.normalizedTime = '';
        this.isValidTime = false;
        this.validationMessage = {
          type: 'error',
          text: 'Please enter a valid time (00:00 to 23:59)'
        };
      }
    },
    validateTextTime() {
      if (!this.startTimeText) {
        this.normalizedTime = '';
        this.isValidTime = false;
        this.validationMessage = null;
        this.startTime = '';
        return;
      }

      try {
        // Remove any non-digit characters except colons and spaces
        let cleanTime = this.startTimeText.toLowerCase().replace(/[^0-9:amp\s]/g, '');
        
        // Handle AM/PM format
        const isAM = cleanTime.includes('am');
        const isPM = cleanTime.includes('pm');
        cleanTime = cleanTime.replace(/[amp\s]/g, '');
        
        let hours, minutes;
        
        if (cleanTime.includes(':')) {
          // Format like "08:00" or "8:00"
          const parts = cleanTime.split(':');
          if (parts.length >= 2) {
            hours = parseInt(parts[0]);
            minutes = parseInt(parts[1]);
          } else {
            throw new Error('Invalid format');
          }
        } else {
          // Format like "0800" or "800"
          if (cleanTime.length === 3) {
            // "800" -> 8:00
            hours = parseInt(cleanTime[0]);
            minutes = parseInt(cleanTime.substring(1, 3));
          } else if (cleanTime.length === 4) {
            // "0800" -> 08:00
            hours = parseInt(cleanTime.substring(0, 2));
            minutes = parseInt(cleanTime.substring(2, 4));
          } else if (cleanTime.length === 1 || cleanTime.length === 2) {
            // "8" or "08" -> assume 00 minutes
            hours = parseInt(cleanTime);
            minutes = 0;
          } else {
            throw new Error('Invalid format');
          }
        }
        
        // Handle AM/PM conversion
        if (isPM && hours !== 12) {
          hours += 12;
        } else if (isAM && hours === 12) {
          hours = 0;
        }
        
        // Validate time range
        if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
          throw new Error('Time out of range');
        }
        
        // Set normalized time and sync with time input
        this.normalizedTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:00`;
        this.startTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
        this.isValidTime = true;
        this.validationMessage = {
          type: 'success',
          text: 'Valid time format'
        };
        
      } catch (e) {
        this.normalizedTime = '';
        this.isValidTime = false;
        this.startTime = '';
        this.validationMessage = {
          type: 'error',
          text: 'Please enter a valid time (examples: 0800, 08:00, 8:00 AM)'
        };
      }
    },
    continueToConfigSelection() {
      if (!this.isValidTime) {
        this.error = 'Please enter a valid start time';
        return;
      }
      
      // Store selected start time in sessionStorage following existing patterns
      sessionStorage.setItem('selectedStartTime', this.normalizedTime);
      sessionStorage.setItem('selectedStartTimeInput', this.startTimeText || this.startTime);
      
      // Navigate to configuration selection
      this.$router.push(`/shifts-start-time-config-selection/${this.companyId}`);
    },
    goBack() {
      this.$router.push(`/shifts-selection/${this.companyId}`);
    }
  }
}
</script> 