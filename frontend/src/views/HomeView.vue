<script setup></script>

<template>
  <main>
    <header>
      <h1>The Visualization Studio</h1>
    </header>
    <LoginView></LoginView>
    
  </main>
</template>
<script>
import LoginView from './LoginView.vue';
export default {
  components: {
    LoginView
  }
}
</script>
<style scoped>
.menu {
  padding-top: 10rem;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.divider {
  border-left: 2px solid rgb(0, 0, 0);
  height: 50px;
}
</style>
