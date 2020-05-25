<template>
  <div>
    <md-list>
      <md-list-item :to="{ name: 'home' }">
        <md-icon>home</md-icon>
        <span class="md-list-item-text">Recipes</span>
      </md-list-item>

      <md-list-item v-if="isLoggedIn" :to="{ name: 'recipe-create' }">
        <md-icon>library_add</md-icon>
        <span class="md-list-item-text">Create Recipe</span>
      </md-list-item>

      <md-list-item v-if="!isLoggedIn" :to="{ name: 'login' }">
        <md-icon>account_box</md-icon>
        <span class="md-list-item-text">Login</span>
      </md-list-item>

      <md-list-item v-else @click="logout">
        <md-icon>arrow_back</md-icon>
        <span class="md-list-item-text">Logout</span>
      </md-list-item>
    </md-list>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
export default {
  name: "NavigationList",
  computed: {
    ...mapGetters("user", ["isLoggedIn"])
  },
  methods: {
    ...mapActions("user", ["logout"])
  }
};
</script>
