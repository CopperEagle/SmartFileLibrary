import type { QueryType } from '@/utils/types'
import { defineStore } from 'pinia'

export const useQueryStore = defineStore('query', {
  state: () => ({
    query: '' as string,
    type: 'all' as QueryType,
  }),
  getters: {
    getQuery(): string {
      return this.query
    },
  },
  actions: {
    setType(t: QueryType) {
      this.type = t
    },

    setQuery(q: string) {
      this.query = q
    },
  },
})
