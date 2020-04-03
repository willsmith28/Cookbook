<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon></v-app-bar-nav-icon>

      <v-toolbar-title>Cookbook</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn v-if="!loggedIn" :to="{name: 'login'}">Login</v-btn>
    </v-app-bar>

    <v-content>
      <router-view></router-view>
    </v-content>
  </v-app>
</template>

<script>
export default {
  name: "App",

  data: () => ({
    //
  }),
  computed: {
    loggedIn() {
      return this.$store.getters["user/loggedIn"];
    }
  },

  methods: {}
};
</script>
