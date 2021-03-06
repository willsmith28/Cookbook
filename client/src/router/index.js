import Vue from "vue";
import VueRouter from "vue-router";
import store from "../store";

Vue.use(VueRouter);

const CreateEditRecipe = () =>
  import(
    /* webpackChunkName: "recipe-create-edit" */ "../views/recipe/CreateEditRecipe.vue"
  );

const routes = [
  {
    path: "/",
    name: "home",
    component: () => import(/* webpackChunkName: "home" */ "../views/Home.vue")
  },
  {
    path: "/login",
    name: "login",
    component: () =>
      import(/* webpackChunkName: "login" */ "../views/Login.vue")
  },
  {
    path: "/recipe/create",
    name: "recipe-create",
    component: CreateEditRecipe,
    beforeEnter: isLoggedIn
  },
  {
    path: "/recipe/:id/edit",
    name: "recipe-edit",
    component: CreateEditRecipe,
    beforeEnter: isLoggedIn,
    props: true
  },
  {
    path: "/recipe/:id/ingredients",
    name: "recipe-edit-ingredients",
    component: CreateEditRecipe,
    beforeEnter: isLoggedIn,
    props: true
  },
  {
    path: "/recipe/:id/steps",
    name: "recipe-edit-steps",
    component: CreateEditRecipe,
    beforeEnter: isLoggedIn,
    props: true
  },
  {
    path: "/recipe/:id",
    name: "recipe-detail",
    component: () =>
      import(
        /* webpackChunkName: "recipe-detail" */ "../views/recipe/RecipeDetail.vue"
      ),
    props: true
  },
  {
    path: "*",
    name: "404",
    component: () =>
      import(/* webpackChunkName: "not-found" */ "../views/NotFound.vue")
  }
];

const router = new VueRouter({
  routes
});

export default router;

const isLoggedIn = (to, from, next) => {
  if (store.getters["user/isLoggedIn"]) {
    next();
  } else {
    next({ name: "login" });
  }
};
