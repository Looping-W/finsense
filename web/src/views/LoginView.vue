<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { errorMessage } from "../api/http";
import AuthFrame from "../components/AuthFrame.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const username = ref("");
const password = ref("");
const error = ref("");
const pending = ref(false);

async function onSubmit() {
  error.value = "";
  pending.value = true;
  try {
    await auth.login(username.value, password.value);
    const redirect = route.query.redirect;
    if (typeof redirect === "string" && redirect.startsWith("/") && !redirect.startsWith("//")) {
      router.push(redirect);
    } else {
      router.push({ name: "home" });
    }
  } catch (err) {
    error.value = errorMessage(err, "登录失败，请稍后再试");
  } finally {
    pending.value = false;
  }
}
</script>

<template>
  <AuthFrame>
    <h1>登录</h1>
    <p class="lede">登录后只能查看和记录自己的账。</p>
    <form @submit.prevent="onSubmit">
      <label class="field">
        <span>用户名</span>
        <input v-model="username" name="username" autocomplete="username" required />
      </label>
      <label class="field">
        <span>密码</span>
        <input
          v-model="password"
          name="password"
          type="password"
          autocomplete="current-password"
          required
        />
      </label>
      <p class="form-error" role="alert">{{ error }}</p>
      <button class="button" type="submit" :disabled="pending">
        {{ pending ? "正在登录" : "登录" }}
      </button>
    </form>
    <p class="switch">没有账号，<router-link to="/register">去注册</router-link></p>
  </AuthFrame>
</template>
