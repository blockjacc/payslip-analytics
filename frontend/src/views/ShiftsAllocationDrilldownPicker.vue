<template>
  <div class="min-h-screen w-full bg-gradient-to-br from-[#0f2027] via-[#2c5364] to-[#232526] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">
      select a shift to drill down
    </h1>
    <div v-if="loading" class="text-white text-center">loading...</div>
    <div v-if="error" class="text-red-400 text-center">error: {{ error }}</div>
    <div v-if="!loading && !error && shifts.length" class="flex justify-center">
      <div class="bg-white/10 rounded-xl p-8 w-full max-w-3xl">
        <div class="mb-8 text-center">
          <h3 class="text-primary mb-2 text-2xl">company id: {{ companyId }}</h3>
          <h3 class="text-primary mb-2 text-xl">schedule type: {{ scheduleType }}</h3>
          <h4 class="text-secondary text-lg">selected shifts: {{ shifts.length }}</h4>
        </div>
        <div class="flex flex-col gap-4">
          <button v-for="shift in shifts" :key="shift.work_schedule_id"
            class="bg-primary/20 hover:bg-primary/40 text-white rounded-lg p-4 text-lg font-semibold flex justify-between items-center transition-colors"
            @click="goToShift(shift.work_schedule_id)">
            <span>{{ shift.name }}</span>
            <span class="text-primary text-base">({{ shift.employee_count }} employees)</span>
          </button>
        </div>
        <div class="mt-8 flex justify-center">
          <button class="bg-white/10 text-white border border-white/20 px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-white/20" @click="goBack">
            back to analytics
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsAllocationDrilldownPicker',
  data() {
    return {
      loading: true,
      error: '',
      shifts: []
    }
  },
  computed: {
    companyId() {
      return this.$route.params.companyId;
    },
    scheduleType() {
      return this.$route.params.scheduleType;
    },
    shiftIds() {
      return this.$route.params.shiftIds;
    },
    selectedShiftIds() {
      return this.shiftIds.split(',').map(id => id.trim());
    }
  },
  methods: {
    async fetchShifts() {
      this.loading = true;
      this.error = '';
      try {
        const response = await fetch(`/api/shifts/schedules/${this.companyId}/${encodeURIComponent(this.scheduleType)}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        const data = await response.json();
        // Only include selected shifts
        this.shifts = (data.schedules || []).filter(s => this.selectedShiftIds.includes(String(s.work_schedule_id)));
      } catch (err) {
        this.error = err.message || 'Failed to fetch shifts';
        this.shifts = [];
      } finally {
        this.loading = false;
      }
    },
    goToShift(shiftId) {
      this.$router.push(`/shifts-allocation-drilldown/${this.companyId}/${this.scheduleType}/${this.shiftIds}/${shiftId}`);
    },
    goBack() {
      this.$router.push(`/shifts-allocation-analytics/${this.companyId}/${this.scheduleType}/${this.shiftIds}`);
    }
  },
  mounted() {
    this.fetchShifts();
  }
}
</script> 