<script setup lang="ts">
import { useQueryStore } from '@/stores/query'
const query = useQueryStore()

function displayResults() {
  const queryUrl = `http://localhost:5000/query?kw=${encodeURIComponent(query.query)}&form=${query.type}`
  fetch(queryUrl)
    .then((response) => {
      if (response.status >= 500) {
        // setStatusError()
      } else if (response.status >= 400) {
        // setStatusClientError()
      }
      return response.json()
    })
    .then(() => {
      // setStatusRunning()
      // this.results = data
    })
    .catch((error) => {
      console.error('Error fetching data:', error)
      // setStatusOffline()
    })
}
</script>

<template>
  <div id="query-box">
    <select id="form-dropdown" v-model="query.type">
      <option value="all">All</option>
      <option value="book">Book</option>
      <option value="website">Website</option>
      <option value="data">Dataset</option>
      <option value="code">Code</option>
      <option value="collection">Collection</option>
      <option value="research article">Research Article</option>
    </select>
    <input
      v-model="query.query"
      @keyup.enter="displayResults"
      type="text"
      id="query-input"
      placeholder="Enter your keyword or '*' for wildcard"
    />
    <button @click="displayResults">🔍</button>
  </div>
</template>

<style lang="css">
#query-box {
  background-color: #ababab00 !important;
  position: absolute;
  top: 20px;
  height: 60px;
  width: 70%;
  left: 60%;
  transform: translateX(-50%);
  background-color: #fff;
  padding: 10px;
  border-radius: 5px;
  flex-direction: column;
  align-items: flex-start;
  min-width: 300px;
}
#form-dropdown {
  border: 2px solid black;
  border-radius: 5px;
  height: 140%;
  width: 10% !important;
  min-width: 60px;
}

#query-box input[type='text'] {
  width: 50%;
  border: 2px solid black;
  border-radius: 5px;
  padding: 12px;
  font-size: 18px;
}

#query-box button {
  border: 2px solid black;
  border-radius: 5px;
  width: 10%;
  height: 135%;
  padding: 10px;
  font-size: 18px;
  min-width: 60px;
}
</style>
