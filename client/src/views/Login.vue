<template>
  <v-container>
    <v-row>
      <v-col>
        <v-text-field
          v-model="formData.username"
          label="User Name"
          :rules="[v => !!v || 'This field is required']"
        />
      </v-col>
      <v-col>
        <v-text-field
          v-model="formData.password"
          label="Password"
          :rules="[v => !!v || 'This field is required']"
        />
      </v-col>
      <v-col>
        <v-btn
          :disabled="!formData.username || !formData.password"
          @click="login(formData.username, formData.password)"
        >login</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      formData: { username: null, password: null }
    };
  },
  methods: {
    login(username, password) {
      this.$store.dispatch("user/login", { username, password });
    }
  }
};
</script>

<style>
</style>