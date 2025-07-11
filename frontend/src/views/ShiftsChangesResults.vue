<template>
  <div class="min-h-screen w-full p-8">
    <div class="flex flex-col items-center justify-start">
      <h1 class="font-serif text-white mb-8 text-4xl text-center">shift changes results</h1>
      
      <!-- Period Summary -->
      <div class="mb-6 bg-primary/8 rounded-lg p-2 px-4 text-primary text-lg flex flex-wrap items-center gap-2 max-w-4xl text-left">
        <span class="font-bold">period:</span>
        <span class="text-white">{{ formatDate(fromDate) }} to {{ formatDate(toDate) }}</span>
        <span class="mx-2">•</span>
        <span class="font-bold">company:</span>
        <span class="text-white">{{ companyId }}</span>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white/10 rounded-xl p-8 w-full max-w-6xl text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p class="text-white text-lg">analyzing shift changes...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-500/20 border border-red-500/30 rounded-xl p-8 w-full max-w-6xl text-center">
        <div class="text-red-300 text-lg mb-4">{{ error }}</div>
        <button 
          class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
          @click="goBack"
        >
          back
        </button>
      </div>

      <!-- No Results -->
      <div v-else-if="!allChanges.length" class="bg-white/10 rounded-xl p-8 w-full max-w-6xl text-center">
        <div class="text-white text-lg mb-4">no shift changes found</div>
        <div class="text-white/70 text-sm mb-6">All employees maintained their shift assignments during this period.</div>
        <div class="flex gap-4 justify-center">
          <button 
            class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
            @click="goBack"
          >
            back
          </button>
          <button 
            class="px-6 py-3 text-base bg-primary text-white hover:bg-primary/80 transition"
            @click="newSearch"
          >
            new search
          </button>
        </div>
      </div>

      <!-- Results Table -->
      <PaginatedTable 
        v-else
        :data="allChanges"
        :items-per-page="15"
        record-type="shift changes"
        :subtitle-text="`${totalEmployees} employees had changes`"
      >
        <template #table="{ paginatedData }">
          <table class="w-full text-white">
            <thead>
              <tr class="border-b border-white/20 text-left">
                <th class="pb-3 pr-4 text-sm font-semibold text-white/70">employee</th>
                <th class="pb-3 pr-4 text-sm font-semibold text-white/70">change date</th>
                <th class="pb-3 pr-4 text-sm font-semibold text-white/70">from shift</th>
                <th class="pb-3 pr-4 text-sm font-semibold text-white/70">to shift</th>
                <th class="pb-3 text-sm font-semibold text-white/70">shift type</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(change, index) in paginatedData" 
                :key="index"
                class="border-b border-white/10 hover:bg-white/5 transition-colors"
              >
                <td class="py-3 pr-4 text-sm">
                  <div class="font-medium">{{ change.first_name }} {{ change.last_name }}</div>
                  <div class="text-white/50 text-xs">ID: {{ change.emp_id }}</div>
                </td>
                <td class="py-3 pr-4 text-sm">
                  <div class="font-medium">{{ formatDate(change.change_date) }}</div>
                  <div class="text-white/50 text-xs">{{ formatDateShort(change.change_date) }}</div>
                </td>
                <td class="py-3 pr-4 text-sm">
                  <div class="font-medium">{{ change.from_shift_name }}</div>
                  <div class="text-white/50 text-xs">{{ change.from_shift_type }}</div>
                </td>
                <td class="py-3 pr-4 text-sm">
                  <div class="font-medium">{{ change.to_shift_name }}</div>
                  <div class="text-white/50 text-xs">{{ change.to_shift_type }}</div>
                </td>
                <td class="py-3 text-sm">
                  <span 
                    class="px-2 py-1 rounded text-xs font-medium bg-primary/20 text-primary"
                  >
                    {{ change.to_shift_type }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </template>
        
        <template #actions>
          <button 
            class="px-6 py-3 text-base bg-white/10 text-white border border-white/20 hover:bg-white/20 transition"
            @click="goBack"
          >
            back
          </button>
          <button 
            class="px-6 py-3 text-base bg-primary text-white hover:bg-primary/80 transition"
            @click="newSearch"
          >
            new search
          </button>
          <button 
            @click="exportToCSV"
            class="px-6 py-3 bg-green-500/20 text-green-100 border border-green-500/30 hover:bg-green-500/30 transition"
          >
            📋 export CSV
          </button>
        </template>
      </PaginatedTable>
    </div>
  </div>
</template>

<script>
import PaginatedTable from '../components/PaginatedTable.vue';

export default {
  name: 'ShiftsChangesResults',
  components: {
    PaginatedTable
  },
  data() {
    return {
      companyId: '',
      fromDate: '',
      toDate: '',
      loading: false,
      error: null,
      allChanges: [],
      totalEmployees: 0,
      totalChanges: 0
    }
  },
  created() {
    this.companyId = this.$route.params.companyId;
    this.fromDate = this.$route.params.fromDate;
    this.toDate = this.$route.params.toDate;
    
    if (!this.companyId || !this.fromDate || !this.toDate) {
      this.$router.push('/');
      return;
    }
    
    this.fetchChanges();
  },
  methods: {
    async fetchChanges() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await fetch(`http://localhost:5002/api/shifts-changes-by-period/${this.companyId}/${this.fromDate}/${this.toDate}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        this.totalEmployees = data.total_employees;
        this.totalChanges = data.total_changes;
        
        // Sort changes by employee name, then by date
        this.allChanges = data.employees_with_changes.sort((a, b) => {
          if (a.last_name !== b.last_name) {
            return a.last_name.localeCompare(b.last_name);
          }
          if (a.first_name !== b.first_name) {
            return a.first_name.localeCompare(b.first_name);
          }
          return new Date(a.change_date) - new Date(b.change_date);
        });
        
      } catch (err) {
        this.error = `Failed to fetch shift changes: ${err.message}`;
        console.error('Error fetching shift changes:', err);
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    },
    
    formatDateShort(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        weekday: 'short'
      });
    },
    
    exportToCSV() {
      const csvRows = [];
      
      // Header
      csvRows.push('Employee ID,First Name,Last Name,Change Date,From Shift,From Shift Type,To Shift,To Shift Type');
      
      // Data rows
      this.allChanges.forEach(change => {
        csvRows.push([
          change.emp_id,
          change.first_name,
          change.last_name,
          change.change_date,
          `"${change.from_shift_name}"`,
          `"${change.from_shift_type}"`,
          `"${change.to_shift_name}"`,
          `"${change.to_shift_type}"`
        ].join(','));
      });
      
      // Create and download file
      const csvContent = csvRows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `shift-changes-${this.fromDate}-to-${this.toDate}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    
    goBack() {
      this.$router.push(`/shifts-changes-date-picker/${this.companyId}`);
    },
    
    newSearch() {
      this.$router.push(`/shifts-changes-date-picker/${this.companyId}`);
    }
  }
}
</script> 