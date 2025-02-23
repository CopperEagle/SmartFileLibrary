<template>
  <svg xmlns="http://www.w3.org/2000/svg" class="d-none">
    <symbol id="home" viewBox="0 0 16 16">
      <path
        d="M8.354 1.146a.5.5 0 0 0-.708 0l-6 6A.5.5 0 0 0 1.5 7.5v7a.5.5 0 0 0 .5.5h4.5a.5.5 0 0 0 .5-.5v-4h2v4a.5.5 0 0 0 .5.5H14a.5.5 0 0 0 .5-.5v-7a.5.5 0 0 0-.146-.354L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293L8.354 1.146zM2.5 14V7.707l5.5-5.5 5.5 5.5V14H10v-4a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v4H2.5z"
      />
    </symbol>
    <symbol id="speedometer2" viewBox="0 0 16 16">
      <path
        d="M8 4a.5.5 0 0 1 .5.5V6a.5.5 0 0 1-1 0V4.5A.5.5 0 0 1 8 4zM3.732 5.732a.5.5 0 0 1 .707 0l.915.914a.5.5 0 1 1-.708.708l-.914-.915a.5.5 0 0 1 0-.707zM2 10a.5.5 0 0 1 .5-.5h1.586a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 10zm9.5 0a.5.5 0 0 1 .5-.5h1.5a.5.5 0 0 1 0 1H12a.5.5 0 0 1-.5-.5zm.754-4.246a.389.389 0 0 0-.527-.02L7.547 9.31a.91.91 0 1 0 1.302 1.258l3.434-4.297a.389.389 0 0 0-.029-.518z"
      />
      <path
        fill-rule="evenodd"
        d="M0 10a8 8 0 1 1 15.547 2.661c-.442 1.253-1.845 1.602-2.932 1.25C11.309 13.488 9.475 13 8 13c-1.474 0-3.31.488-4.615.911-1.087.352-2.49.003-2.932-1.25A7.988 7.988 0 0 1 0 10zm8-7a7 7 0 0 0-6.603 9.329c.203.575.923.876 1.68.63C4.397 12.533 6.358 12 8 12s3.604.532 4.923.96c.757.245 1.477-.056 1.68-.631A7 7 0 0 0 8 3z"
      />
    </symbol>
    <symbol id="table" viewBox="0 0 16 16">
      <path
        d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm15 2h-4v3h4V4zm0 4h-4v3h4V8zm0 4h-4v3h3a1 1 0 0 0 1-1v-2zm-5 3v-3H6v3h4zm-5 0v-3H1v2a1 1 0 0 0 1 1h3zm-4-4h4V8H1v3zm0-4h4V4H1v3zm5-3v3h4V4H6zm4 4H6v3h4V8z"
      />
    </symbol>
    <symbol id="people-circle" viewBox="0 0 16 16">
      <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z" />
      <path
        fill-rule="evenodd"
        d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z"
      />
    </symbol>
    <symbol id="grid" viewBox="0 0 16 16">
      <path
        d="M1 2.5A1.5 1.5 0 0 1 2.5 1h3A1.5 1.5 0 0 1 7 2.5v3A1.5 1.5 0 0 1 5.5 7h-3A1.5 1.5 0 0 1 1 5.5v-3zM2.5 2a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zm6.5.5A1.5 1.5 0 0 1 10.5 1h3A1.5 1.5 0 0 1 15 2.5v3A1.5 1.5 0 0 1 13.5 7h-3A1.5 1.5 0 0 1 9 5.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zM1 10.5A1.5 1.5 0 0 1 2.5 9h3A1.5 1.5 0 0 1 7 10.5v3A1.5 1.5 0 0 1 5.5 15h-3A1.5 1.5 0 0 1 1 13.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zm6.5.5A1.5 1.5 0 0 1 10.5 9h3a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-3A1.5 1.5 0 0 1 9 13.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3z"
      />
    </symbol>
  </svg>
  <!-- <BButton class="m-2" @click="click('start')">Show start</BButton>
  <BButton class="m-2" @click="click('end')">Show end</BButton>
  <BButton class="m-2" @click="click('bottom')">Show bottom</BButton>
  <BButton class="m-2" @click="click('top')">Show top</BButton>
 -->
  <button id="menubuttonid" class="btn btn-primary menu-button" type="button" @click="showSidebar">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      fill="currentColor"
      class="bi bi-list"
      viewBox="0 0 16 16"
    >
      <path
        fill-rule="evenodd"
        d="M2.5 11.5A.5.5 0 0 1 3 11h10a.5.5 0 0 1 0 1H2a.5.5 0 0 1-.5-.5zm0-4A.5.5 0 0 1 3 7h10a.5.5 0 0 1 0 1H2a.5.5 0 0 1-.5-.5zm0-4A.5.5 0 0 1 3 3h10a.5.5 0 0 1 0 1H2a.5.5 0 0 1-.5-.5z"
      />
    </svg>
  </button>
  <BOffcanvas v-model="show" :placement="placement">
    <div class="d-flex flex-column">
      <div class="d-flex flex-column">
        <a
          href="index.html"
          class="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-black text-decoration-none"
        >
          <img src="/assets/icon.svg" width="48px" class="m-2" />
          <span class="fs-4"> SmartFileLibrary</span>
        </a>
        <hr />
        <ul class="nav nav-pills flex-column mb-auto">
          <li class="nav-item">
            <a onclick="doswitch()" href="index.html" class="nav-link active" aria-current="page">
              <svg class="bi pe-none me-2" width="16" height="16"><use xlink:href="#home" /></svg>
              Home
            </a>
          </li>
          <li>
            <a onclick="doswitch()" href="dashboard.html" class="nav-link text-black">
              <svg class="bi pe-none me-2" width="16" height="16">
                <use xlink:href="#speedometer2" />
              </svg>
              Dashboard
            </a>
          </li>
          <li>
            <a onclick="doswitch()" href="doc_analysis.html" class="nav-link text-black">
              <svg class="bi pe-none me-2" width="16" height="16"><use xlink:href="#table" /></svg>
              Document Analysis
            </a>
          </li>
          <li>
            <a onclick="doswitch()" href="plugins.html" class="nav-link text-black">
              <svg class="bi pe-none me-2" width="16" height="16"><use xlink:href="#grid" /></svg>
              Plugins
            </a>
          </li>
          <li>
            <a onclick="doswitch()" href="settings.html" class="nav-link text-black">
              <svg class="bi pe-none me-2" width="16" height="16">
                <use xlink:href="#people-circle" />
              </svg>
              Settings
            </a>
          </li>
        </ul>
        <hr />
        <!-- <BDropdown>Hello</BDropdown> -->
        <div class="inline">
          <a
            href="#"
            class="d-flex align-items-center text-black text-decoration-none inline"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <img
              src="https://cdn-icons-png.flaticon.com/512/5705/5705372.png"
              alt=""
              width="32"
              height="32"
              class="rounded-circle me-2"
            />
            <!-- <strong id="user-name">Username</strong> -->

            <BDropdown
              text="Username"
              class="d-flex align-items-center text-black text-decoration-none"
            >
              <!-- <ul class="dropdown-menu text-small shadow"> -->
              <a class="dropdown-item" href="#">New Entry... (TBD)</a>
              <a class="dropdown-item" href="settings.html">Settings</a>
              <hr class="dropdown-divider" />
              <a class="dropdown-item" onclick="sendServerOff();">Turn off</a>
              <!-- </ul> -->
            </BDropdown></a
          >
        </div>
        <div style="position: absolute; bottom: 10px">
          <a href="attribution.txt" style="color: grey"> Icon attribution </a>
        </div>
      </div>
    </div>
  </BOffcanvas>
</template>

<script setup lang="ts">
import { BDropdown, type Placement } from 'bootstrap-vue-next';
import { ref } from 'vue';

const props = defineProps<{
  place: Placement;
}>();
const show = ref(false);
const placement = ref<Placement>(props.place); //'start')

const showSidebar = () => {
  show.value = true;
};

// const click = () => {
//   placement.value = props.place
//   show.value = !show.value
// }
</script>

<style lang="css" scoped>
.menu-button {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 1000;
  padding: 10px 20px;
  font-size: 24px;
  background-color: #3399ccaa;
  color: white;
  border: none;
  border-radius: 10px;
  /*border-radius: 50%;*/
  box-shadow: 0px 0px 5px 0px rgba(1, 1, 1, 0.9);
  cursor: pointer;
}
</style>
