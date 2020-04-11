import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "home",
    component: () => import(/* webpackChunkName: "home" */ "../views/Home.vue")
  },
  {
    path: "/login/",
    name: "login",
    component: () =>
      import(/* webpackChunkName: "login" */ "../views/Login.vue")
  },
  {
    path: "/recipe/:id/",
    name: "recipe-detail",
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/RecipeDetail.vue"),
    props: true
  }
];

const router = new VueRouter({
  routes
});

export default router;
