<script setup>
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

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
          <h1>你好，{{ auth.user?.username }}</h1>
          <p class="quiet">还没有收支记录。记账功能下一步开放。</p>
          <div class="ledger-row">
            <b>本月结余</b>
            <span class="mono">—　尚无账目</span>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>
