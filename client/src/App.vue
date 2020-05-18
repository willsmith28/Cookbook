<template>
  <div id="app">
    <md-app>
      <md-app-toolbar class="md-primary">
        <md-button
          v-show="!menuVisible"
          class="md-icon-button"
          @click="toggleMenu"
        >
          <md-icon>menu</md-icon>
        </md-button>
        <span class="md-title">Cookbook</span>
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

        <md-list>
          <md-list-item :to="{ name: 'home' }">
            <md-icon>home</md-icon>
            <span class="md-list-item-text">Recipes</span>
          </md-list-item>

          <md-list-item v-if="!loggedIn" :to="{ name: 'login' }">
            <md-icon>account_box</md-icon>
            <span class="md-list-item-text">Login</span>
          </md-list-item>

          <md-list-item v-else @click="logout">
            <md-icon>account_box</md-icon>
            <span class="md-list-item-text">Logout</span>
          </md-list-item>
        </md-list>
      </md-app-drawer>

      <md-app-content>
        <router-view />
      </md-app-content>
    </md-app>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
export default {
  data() {
    return {
      menuVisible: false
    };
  },
  computed: {
    ...mapGetters("user", ["loggedIn"])
  },
  created() {
    const username = localStorage.getItem("username");

    if (username) {
      this.setUsername(username);
    }

    Promise.resolve(this.initState());
  },
  methods: {
    toggleMenu() {
      this.menuVisible = !this.menuVisible;
    },
    ...mapActions("recipe", ["initState"]),
    ...mapActions("user", ["setUsername", "logout"])
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
