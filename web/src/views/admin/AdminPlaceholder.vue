<script setup>
import { useRouter } from "vue-router";

import { useAuthStore } from "../../stores/auth";

const auth = useAuthStore();
const router = useRouter();

async function onLogout() {
  await auth.logout();
  router.push({ name: "login" });
}
</script>

<template>
  <main class="desk">
    <div class="desk-inner">
      <header class="topbar">
        <p class="brand">finsense</p>
        <button class="button-quiet" type="button" @click="onLogout">退出</button>
      </header>
      <section class="sheet sheet-plain">
        <div class="sheet-main">
          <h1>管理</h1>
          <p class="quiet">管理功能在阶段 8 开放。这里不会显示任何用户的账目。</p>
        </div>
      </section>
    </div>
  </main>
</template>
