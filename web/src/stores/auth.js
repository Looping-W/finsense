import { defineStore } from "pinia";

import { http } from "../api/http";

const TOKEN_KEY = "finsense_token";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || "",
    user: null,
    ready: false,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token && state.user),
  },
  actions: {
    async restore() {
      if (this.ready) return;
      if (!this.token) {
        this.ready = true;
        return;
      }
      try {
        const { data } = await http.get("/auth/me");
        this.user = data;
      } catch {
        this.clear();
      } finally {
        this.ready = true;
      }
    },
    async login(username, password) {
      const { data } = await http.post("/auth/login", { username, password });
      this.token = data.access_token;
      this.user = data.user;
      this.ready = true;
      localStorage.setItem(TOKEN_KEY, data.access_token);
    },
    async register(username, password) {
      await http.post("/auth/register", { username, password });
      await this.login(username, password);
    },
    async logout() {
      try {
        await http.post("/auth/logout");
      } catch {
        // 本地仍要清掉 token，避免退出按钮失效。
      }
      this.clear();
    },
    clear() {
      this.token = "";
      this.user = null;
      localStorage.removeItem(TOKEN_KEY);
    },
  },
});
