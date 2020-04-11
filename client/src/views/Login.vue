<template>
  <div>
    <form nonvalidate class="md-layout" @submit.prevent="login">
      <md-card class="md-layout-item md-size-50 md-small-size-100">
        <md-card-header>
          <div class="md-title">Login</div>
        </md-card-header>

        <md-card-content>
          <div class="md-layout md-gutter">
            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('username')">
                <label for="username">Username</label>
                <md-input
                  id="username"
                  v-model.trim="form.username"
                  autocomplete="username"
                  name="username"
                />
                <span v-if="!$v.form.username.required" class="md-error">
                  Username is required
                </span>
              </md-field>
            </div>

            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('password')">
                <label for="password">Password</label>
                <md-input
                  id="password"
                  v-model.trim="form.password"
                  autocomplete="current-password"
                  type="password"
                  name="password"
                />
                <span v-if="!$v.form.password.required" class="md-error">
                  Password is required
                </span>
              </md-field>
            </div>
          </div>
        </md-card-content>

        <md-card-actions>
          <md-button type="submit" class="md-primary">Login</md-button>
        </md-card-actions>
      </md-card>
    </form>
  </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
export default {
  name: "Login",
  mixins: [validationMixin],
  data() {
    return {
      form: {
        username: null,
        password: null
      }
    };
  },
  validations: {
    form: {
      username: { required },
      password: { required }
    }
  },
  methods: {
    getValidationClass(fieldName) {
      const field = this.$v.form[fieldName];

      if (field) {
        return { "md-invalid": field.$invalid && field.$dirty };
      }
    },
    async login() {
      try {
        this.$v.$touch();

        if (!this.$v.$invalid) {
          await this.$store.dispatch("user/login", {
            username: this.form.username,
            password: this.form.password
          });
          this.$router.push({ name: "home" });
        }
      } catch (error) {
        console.log(error.response.data);
      }
    }
  }
};
</script>
