import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "../stores/auth";
import AdminPlaceholder from "../views/admin/AdminPlaceholder.vue";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView, meta: { title: "登录" } },
    { path: "/register", name: "register", component: RegisterView, meta: { title: "注册" } },
    { path: "/", name: "home", component: HomeView, meta: { title: "首页", requiresAuth: true } },
    {
      path: "/admin",
      name: "admin",
      component: AdminPlaceholder,
      meta: { title: "管理", requiresAuth: true, requiresAdmin: true },
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  await auth.restore();
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.meta.requiresAdmin && auth.user?.role !== "admin") {
    return { name: "home" };
  }
  if ((to.name === "login" || to.name === "register") && auth.isLoggedIn) {
    return { name: "home" };
  }
  return true;
});

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · finsense` : "finsense";
});

export default router;
