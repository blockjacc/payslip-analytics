<template>
  <div class="p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">shifts allocation analytics</h1>
    <div class="bg-white/10 rounded-xl p-8 w-full max-w-4xl text-center mx-auto">
      <h3 class="text-primary mb-6 text-2xl">company id: {{ companyId }}</h3>
      
      <!-- Step 1: Schedule Type Selection -->
      <div v-if="currentStep === 1">
        <h4 class="text-white mb-6 text-lg text-left">select schedule type:</h4>
        <select 
          v-model="selectedScheduleType" 
          @change="onScheduleTypeChange"
          class="w-full p-3 bg-white/5 text-white border border-white/20 rounded-lg focus:outline-none focus:border-primary mb-8"
        >
          <option value="">-- select schedule type --</option>
          <option 
            v-for="type in scheduleTypes" 
            :key="type.work_type_name" 
            :value="type.work_type_name"
          >
            {{ type.work_type_name }} ({{ type.count }})
          </option>
        </select>
        <div class="flex gap-4 justify-center mt-6">
          <button 
            class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition flex-1 max-w-[200px]"
            @click="goBack"
          >
            back
          </button>
          <button 
            class="px-6 py-3 text-base bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold disabled:opacity-70 disabled:cursor-not-allowed transition flex-1 max-w-[200px]"
            @click="goToShiftSelection"
            :disabled="!selectedScheduleType"
          >
            continue
          </button>
        </div>
      </div>

      <!-- Step 2: Shift Selection -->
      <div v-if="currentStep === 2">
        <h4 class="text-white mb-6 text-lg text-left">select shifts to analyze</h4>
        <div class="flex flex-col gap-2 max-h-[300px] overflow-y-auto pr-2 mb-6">
          <div 
            v-for="shift in schedules" 
            :key="shift.work_schedule_id"
            class="p-3 cursor-pointer transition-all duration-200 text-white bg-white/5 rounded-md text-left text-sm border border-transparent hover:bg-primary/10 hover:translate-x-1"
            :class="{ 'bg-primary/20 border-primary/50 font-bold': isShiftSelected(shift.work_schedule_id) }"
            @click="toggleShift(shift.work_schedule_id)"
          >
            {{ shift.name }} <span class="text-primary">({{ shift.employee_count }})</span>
          </div>
        </div>
        <div class="text-primary text-lg mb-4">
          <p>selected: {{ selectedShifts.length }} shifts</p>
        </div>
        <!-- Selected shifts display with delete options -->
        <div v-if="selectedShifts.length > 0" class="mb-6 text-left">
          <h5 class="text-primary mb-2 text-base">selected shifts:</h5>
          <div class="flex flex-wrap gap-2">
            <div v-for="shiftId in selectedShifts" :key="shiftId" class="flex items-center bg-primary/20 border border-primary/50 rounded-full px-3 py-1 text-sm text-white">
              <span>{{ getShiftName(shiftId) }}</span>
              <button class="bg-none border-none text-white text-lg ml-2 cursor-pointer flex items-center justify-center w-5 h-5 rounded-full p-0 leading-none hover:bg-white/20" @click.stop="removeShift(shiftId)">×</button>
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
            @click="proceedToAnalytics"
            :disabled="selectedShifts.length === 0"
          >
            continue
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsAllocationSelection',
  data() {
    return {
      companyId: '',
      scheduleTypes: [],
      schedules: [],
      selectedScheduleType: '',
      selectedShifts: [],
      currentStep: 1
    }
  },
  async created() {
    this.companyId = this.$route.params.companyId;
    if (!this.companyId) {
      this.$router.push('/');
      return;
    }
    await this.loadScheduleTypes();
  },
  methods: {
    async loadScheduleTypes() {
      try {
        const response = await fetch(`/api/shifts/schedule-type-counts/${this.companyId}`);
        if (response.ok) {
          const data = await response.json();
          this.scheduleTypes = data.schedule_types;
        } else {
          console.error('Failed to load schedule types');
        }
      } catch (error) {
        console.error('Error loading schedule types:', error);
      }
    },
    async onScheduleTypeChange() {
      this.selectedShifts = [];
      this.schedules = [];
      if (this.selectedScheduleType) {
        await this.loadSchedules();
      }
    },
    async loadSchedules() {
      try {
        const response = await fetch(`/api/shifts/schedules/${this.companyId}/${encodeURIComponent(this.selectedScheduleType)}`);
        if (response.ok) {
          const data = await response.json();
          this.schedules = data.schedules;
        } else {
          console.error('Failed to load schedules');
        }
      } catch (error) {
        console.error('Error loading schedules:', error);
      }
    },
    goToShiftSelection() {
      this.currentStep = 2;
    },
    isShiftSelected(shiftId) {
      return this.selectedShifts.includes(shiftId);
    },
    toggleShift(shiftId) {
      const idx = this.selectedShifts.indexOf(shiftId);
      if (idx === -1) {
        this.selectedShifts.push(shiftId);
      } else {
        this.selectedShifts.splice(idx, 1);
      }
    },
    getShiftName(shiftId) {
      const shift = this.schedules.find(s => s.work_schedule_id === shiftId);
      return shift ? shift.name : '';
    },
    removeShift(shiftId) {
      this.selectedShifts = this.selectedShifts.filter(id => id !== shiftId);
    },
    proceedToAnalytics() {
      if (this.selectedShifts.length > 0) {
        this.$router.push(`/shifts-allocation-analytics/${this.companyId}/${this.selectedScheduleType}/${this.selectedShifts.join(',')}`);
      }
    },
    goBack() {
      this.$router.push(`/shifts-selection/${this.companyId}`);
    }
  }
}
</script> 