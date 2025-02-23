<script setup lang="ts">
import { onMounted, ref } from 'vue'

// const props = defineProps<{
//   entry: any
//   isFavourite: boolean
// }>()

const el = ref<HTMLDivElement>()

onMounted(() => {
  const containerWidth = el.value?.offsetWidth as number
  const titleElement = el.value?.querySelector('.entry-left') as HTMLDivElement
  const titleWidth = titleElement?.offsetWidth
  const keywordBasis = 100 - (containerWidth - titleWidth) / containerWidth // Adjust as needed
  // Set keywordBasis for this entry
  el.value?.style.setProperty('--keyword-basis', `${keywordBasis}%`)
  // if (props.isFavourite) {
  //   this.favourites.push(this.entry.id)
  // }
})
</script>

<template>
  <!-- <div class="result-entry" @click="displayPopup" ref="el">
    <div class="entry-left">
      <div class="entry-title">{{ entry.title }}</div>
      <div class="entry-author">{{ entry.author }}</div>
    </div>
    <div class="entry-keywords">
      <span v-for="keyword in entry.keywords" class="keyword">{{ keyword }}</span>
    </div>
    <span
      @click.stop="toggleFavourite"
      :class="{ 'fav-star': isFavourite, 'non-fav-star': !isFavourite }"
      >{{ isFavourite ? '⭐' : '☆' }}</span
    >
  </div> -->
  <div></div>
</template>
