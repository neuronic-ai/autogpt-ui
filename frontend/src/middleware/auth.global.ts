export default defineNuxtRouteMiddleware(async () => {
  if (process.client) return;
  const config = useRuntimeConfig();
  const nuxtApp = useNuxtApp();
  const headers = useRequestHeaders(['cookie']);
  const { error } = await useFetch(`${config.apiBase}/api/v1/sessions/check`, { headers });
  if (error.value?.status && [403, 401].includes(error.value.status)) {
    await navigateTo(`http://${nuxtApp.ssrContext?.event.node.req.headers.host}/auth/`, { external: true });
  }
});
