<template>
  <NNotificationProvider :max="3">
    <NConfigProvider :theme-overrides="themeOverrides">
      <NuxtPage />
    </NConfigProvider>
  </NNotificationProvider>
</template>

<script setup lang="ts">
import { NConfigProvider, NNotificationProvider, GlobalThemeOverrides } from 'naive-ui';

const themeOverrides: GlobalThemeOverrides = {
  Card: {
    titleFontSizeHuge: '36px',
  },
};
</script>
