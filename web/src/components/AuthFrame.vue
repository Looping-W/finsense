<template>
  <main class="auth">
    <section class="sheet">
      <div class="sheet-main">
        <p class="brand">finsense</p>
        <slot />
      </div>
      <aside class="amount-col" aria-hidden="true">
        <span class="col-head">金额</span>
        <span class="seal">可核对</span>
      </aside>
    </section>
  </main>
</template>
