<template>
  <div class="bg-white/10 rounded-xl p-8 w-full max-w-6xl">
    <!-- Summary Info -->
    <div class="mb-6 text-center">
      <div class="text-white text-lg font-semibold">{{ totalRecords }} {{ recordType }}</div>
      <div class="text-white/70 text-sm" v-if="subtitleText">{{ subtitleText }}</div>
    </div>

    <!-- Pagination Controls (Top) -->
    <div v-if="totalPages > 1" class="flex justify-between items-center mb-6">
      <button 
        v-if="hasPrevPage" 
        @click="currentPage--" 
        class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600 transition"
      >
        &larr; previous
      </button>
      <div v-else class="w-20"></div>
      
      <div class="text-white text-sm">
        page {{ currentPage }} of {{ totalPages }} 
        <span class="text-white/70">(showing {{ (currentPage - 1) * itemsPerPage + 1 }}-{{ Math.min(currentPage * itemsPerPage, totalRecords) }} of {{ totalRecords }})</span>
      </div>
      
      <button 
        v-if="hasNextPage" 
        @click="currentPage++" 
        class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600 transition"
      >
        next &rarr;
      </button>
      <div v-else class="w-20"></div>
    </div>

    <!-- Table Content -->
    <div class="overflow-x-auto">
      <slot name="table" :paginatedData="paginatedData"></slot>
    </div>

    <!-- Pagination Controls (Bottom) -->
    <div v-if="totalPages > 1" class="flex justify-between items-center mt-6">
      <button 
        v-if="hasPrevPage" 
        @click="currentPage--" 
        class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600 transition"
      >
        &larr; previous
      </button>
      <div v-else class="w-20"></div>
      
      <div class="text-white text-sm">
        page {{ currentPage }} of {{ totalPages }}
      </div>
      
      <button 
        v-if="hasNextPage" 
        @click="currentPage++" 
        class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600 transition"
      >
        next &rarr;
      </button>
      <div v-else class="w-20"></div>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-4 justify-center mt-8">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaginatedTable',
  props: {
    data: {
      type: Array,
      required: true
    },
    itemsPerPage: {
      type: Number,
      default: 20
    },
    recordType: {
      type: String,
      default: 'records'
    },
    subtitleText: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      currentPage: 1
    }
  },
  computed: {
    totalRecords() {
      return this.data.length;
    },
    totalPages() {
      return Math.ceil(this.totalRecords / this.itemsPerPage);
    },
    paginatedData() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.data.slice(start, end);
    },
    hasPrevPage() {
      return this.currentPage > 1;
    },
    hasNextPage() {
      return this.currentPage < this.totalPages;
    }
  },
  watch: {
    data() {
      // Reset pagination when data changes
      this.currentPage = 1;
    }
  },
  methods: {
    resetPagination() {
      this.currentPage = 1;
    }
  }
}
</script> 