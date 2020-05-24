import Vue from "vue";
import VueRouter from "vue-router";

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
    component: CreateEditRecipe
  },
  {
    path: "/recipe/:recipeId",
    name: "recipe-detail",
    component: () =>
      import(
        /* webpackChunkName: "recipe-detail" */ "../views/recipe/RecipeDetail.vue"
      ),
    props: true,
    children: [
      {
        path: "edit",
        name: "recipe-edit",
        component: CreateEditRecipe,
        children: [
          {
            path: "ingredients",
            name: "recipe-edit-ingredients",
            component: CreateEditRecipe
          },
          {
            path: "steps",
            name: "recipe-edit-steps",
            component: CreateEditRecipe
          }
        ]
      }
    ]
  }
];

const router = new VueRouter({
  routes
});

export default router;
