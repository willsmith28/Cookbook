<template>
  <div id="app">
    <md-app class="fill-viewport">
      <md-app-toolbar class="md-primary">
        <md-button
          v-show="!menuVisible"
          class="md-icon-button"
          @click="toggleMenu"
        >
          <md-icon>menu</md-icon>
        </md-button>
        <md-button class="md-title" :to="{ name: 'home' }">Cookbook</md-button>
      </md-app-toolbar>

      <md-app-drawer :md-active.sync="menuVisible" md-persistent="full">
        <md-toolbar class="md-transparent" md-elevation="0">
          Navigation
          <div class="md-toolbar-section-end">
            <md-button class="md-icon-button md-dense" @click="toggleMenu">
              <md-icon>keyboard_arrow_left</md-icon>
            </md-button>
          </div>
        </md-toolbar>

        <navigation-list />
      </md-app-drawer>

      <md-app-content>
        <router-view />
      </md-app-content>
    </md-app>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import NavigationList from "@/components/NavigationList";
export default {
  components: { NavigationList },
  data: () => ({
    menuVisible: false
  }),
  computed: {
    ...mapGetters("user", ["isLoggedIn"])
  },
  created() {
    this.checkLocalStorageForUser();
  },
  methods: {
    toggleMenu() {
      this.menuVisible = !this.menuVisible;
    },
    ...mapActions("user", ["logout", "checkLocalStorageForUser"])
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

.fill-viewport {
  min-height: 100vh;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
