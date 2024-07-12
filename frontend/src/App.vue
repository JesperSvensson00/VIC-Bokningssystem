<script setup>
import {  RouterView } from 'vue-router'
import MainFooter from '@/components/MainFooter.vue'
import NavBar from '@/components/NavBar.vue'
</script>

<template>
  <NavBar />
  <RouterView />
  <MainFooter />
</template>
