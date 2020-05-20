import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const CreateEditRecipe = () =>
  import(
    /* webpackChunkName: "recipe-create-edit" */ "../views/CreateEditRecipe.vue"
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
    alias: ["/recipe/create/ingredients", "/recipe/create/steps"]
  },
  {
    path: "/recipe/:id",
    name: "recipe-detail",
    component: () =>
      import(
        /* webpackChunkName: "recipe-detail" */ "../views/RecipeDetail.vue"
      ),
    props: true
  }
];

const router = new VueRouter({
  routes
});

export default router;
