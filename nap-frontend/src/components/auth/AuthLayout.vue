<template>
  <div class="auth-page">
    <aside class="auth-brand">
      <div class="auth-brand__glow auth-brand__glow--1"></div>
      <div class="auth-brand__glow auth-brand__glow--2"></div>
      <div class="auth-brand__grid"></div>
      <div class="auth-brand__stars auth-brand__stars--a"></div>
      <div class="auth-brand__stars auth-brand__stars--b"></div>

      <div class="auth-brand__inner">
        <div class="auth-brand__logo">
          <span class="auth-brand__ring"></span>
          <AppLogo size="large" :show-text="false" />
        </div>
        <h1 class="auth-brand__title"><span v-for="(ch, i) in titleLetters" :key="i" class="auth-brand__letter"
            :style="{ '--i': i }">{{ ch }}</span></h1>
        <p class="auth-brand__subtitle">{{ typedText }}<span class="auth-brand__cursor"></span></p>
      </div>
    </aside>

    <section class="auth-form">
      <t-space direction="vertical">
        <h2 class="auth-form__heading">{{ heading }}</h2>
        <p class="auth-form__hint">{{ hint }}</p>
        <slot />
      </t-space>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppLogo from '@/components/common/AppLogo.vue'
import '@fontsource-variable/orbitron'

const props = withDefaults(
  defineProps<{
    heading: string
    hint: string
    brandTitle: string
    brandSubtitle: string
  }>(),
  {}
)

const typedChars = ref(0)

typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
const reducedMotion =
  typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
let timer: number | undefined

const typedText = computed(() => props.brandSubtitle.slice(0, typedChars.value))
const titleLetters = computed(() => props.brandTitle.split(''))

function startTyping() {
  if (reducedMotion) {
    typedChars.value = props.brandSubtitle.length
    return
  }
  typedChars.value = 0
  timer = window.setInterval(() => {
    typedChars.value++
    if (typedChars.value >= props.brandSubtitle.length && timer) {
      window.clearInterval(timer)
      timer = undefined
    }
  }, 55)
}

onMounted(startTyping)
watch(() => props.brandSubtitle, startTyping)
onBeforeUnmount(() => timer && window.clearInterval(timer))
</script>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(360px, 5fr) minmax(380px, 4fr);
  height: 100%;
  width: 100%;
  overflow: auto;
}

.auth-brand {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(140deg, #0c3436 0%, #1c4f52 38%, #296266 62%, #29663f 100%);
  background-size: 160% 160%;
  color: #fff;
  animation: auth-brand-shift 14s ease-in-out infinite alternate;
}

@keyframes auth-brand-shift {
  0% {
    background-position: 0% 0%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 100%;
  }
}

.auth-brand__grid {
  position: absolute;
  inset: -50%;
  background-image:
    linear-gradient(rgba(185, 243, 247, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(185, 243, 247, 0.07) 1px, transparent 1px);
  background-size: 56px 56px;
  animation: auth-grid-move 26s linear infinite;
}

@keyframes auth-grid-move {
  from {
    transform: translate3d(0, 0, 0);
  }

  to {
    transform: translate3d(56px, 56px, 0);
  }
}

.auth-brand__stars {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(2px 2px at 8% 18%, rgba(255, 255, 255, 0.9), transparent 100%),
    radial-gradient(1.5px 1.5px at 32% 62%, rgba(255, 255, 255, 0.7), transparent 100%),
    radial-gradient(2px 2px at 52% 12%, rgba(255, 255, 255, 0.8), transparent 100%),
    radial-gradient(1.5px 1.5px at 68% 46%, rgba(255, 255, 255, 0.6), transparent 100%),
    radial-gradient(2px 2px at 86% 78%, rgba(255, 255, 255, 0.75), transparent 100%),
    radial-gradient(1.5px 1.5px at 44% 88%, rgba(255, 255, 255, 0.65), transparent 100%),
    radial-gradient(2px 2px at 20% 48%, rgba(255, 255, 255, 0.5), transparent 100%),
    radial-gradient(1.5px 1.5px at 74% 92%, rgba(255, 255, 255, 0.55), transparent 100%);
  background-size: 260px 260px;
  background-repeat: repeat;
  animation:
    auth-stars-flow 16s linear infinite,
    auth-twinkle 5s ease-in-out infinite;
}

@keyframes auth-stars-flow {
  from {
    background-position: 0 -260px;
  }

  to {
    background-position: 260px 0;
  }
}

@keyframes auth-twinkle {

  0%,
  100% {
    opacity: 0.65;
  }

  50% {
    opacity: 1;
  }
}

.auth-brand__stars--b {
  animation:
    auth-stars-flow-b 22s linear infinite,
    auth-twinkle 7s ease-in-out infinite -2.5s;
}

@keyframes auth-stars-flow-b {
  from {
    background-position: 260px 260px;
  }

  to {
    background-position: -260px -260px;
  }
}

.auth-brand__glow {
  position: absolute;
  border-radius: 9999px;
  filter: blur(70px);
  opacity: 0.55;
  animation: auth-float 9s ease-in-out infinite;
}

.auth-brand__glow--1 {
  width: 340px;
  height: 340px;
  top: 12%;
  left: 16%;
  background: radial-gradient(circle, rgba(185, 243, 247, 0.55), transparent 70%);
}

.auth-brand__glow--2 {
  width: 340px;
  height: 340px;
  bottom: 8%;
  right: 14%;
  background: radial-gradient(circle, rgba(168, 130, 74, 0.6), transparent 70%);
  animation-delay: -4.5s;
}

@keyframes auth-float {

  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }

  50% {
    transform: translate3d(20px, -16px, 0) scale(1.1);
  }
}

.auth-brand__inner {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 48px;
  max-width: 460px;
  animation: auth-enter 0.9s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes auth-enter {
  from {
    opacity: 0;
    transform: translateY(16px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-brand__logo {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 28px;
}

.auth-brand__ring {
  position: absolute;
  inset: -14px;
  border-radius: 9999px;
  border: 2px solid rgba(185, 243, 247, 0.5);
  animation: auth-ring 2.6s ease-out infinite;
}

.auth-brand__logo::after {
  content: '';
  position: absolute;
  inset: -30px;
  border-radius: 9999px;
  background: radial-gradient(circle, rgba(168, 130, 74, 0.3), transparent 68%);
  animation: auth-pulse 2.6s ease-in-out infinite;
}

@keyframes auth-ring {
  0% {
    transform: scale(0.7);
    opacity: 0.9;
  }

  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

@keyframes auth-pulse {

  0%,
  100% {
    opacity: 0.5;
    transform: scale(0.92);
  }

  50% {
    opacity: 1;
    transform: scale(1.06);
  }
}

.auth-brand__title {
  position: relative;
  margin: 0;
  font-family: 'Orbitron Variable', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 64px;
  line-height: 1.1;
  font-weight: 800;
  letter-spacing: -0.01em;
  text-transform: uppercase;
}

.auth-brand__letter {
  display: inline-block;
  animation: auth-letter-in 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: calc(0.12s * var(--i) + 0.25s);
  background: linear-gradient(160deg, #fff 40%, rgba(185, 243, 247, 0.85));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

@keyframes auth-letter-in {
  from {
    opacity: 0;
    transform: translateY(0.5em) rotateX(70deg);
    filter: blur(6px);
  }

  to {
    opacity: 1;
    transform: translateY(0) rotateX(0);
    filter: blur(0);
  }
}

.auth-brand__title::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  font: inherit;
  background: linear-gradient(105deg,
      transparent 10%,
      rgba(185, 243, 247, 0) 32%,
      rgba(185, 243, 247, 0.9) 46%,
      rgba(255, 255, 255, 0.95) 50%,
      rgba(185, 243, 247, 0.9) 54%,
      rgba(185, 243, 247, 0) 68%,
      transparent 90%);
  background-size: 240% 100%;
  background-repeat: no-repeat;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  pointer-events: none;
  animation: auth-sweep 1.6s ease-in-out 0.9s both;
}

@keyframes auth-sweep {
  0% {
    background-position: -120% 0;
    opacity: 1;
  }

  60% {
    opacity: 1;
  }

  100% {
    background-position: 220% 0;
    opacity: 0;
  }
}

.auth-brand__subtitle {
  margin: 18px 0 0;
  font-family: 'Orbitron Variable', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 18px;
  line-height: 1.6;
  font-weight: 500;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.92);
  white-space: nowrap;
  min-height: 1.6em;
}

.auth-brand__cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  margin-left: 3px;
  vertical-align: -0.15em;
  background: rgba(185, 243, 247, 0.95);
  animation: auth-cursor 0.85s steps(1) infinite;
}

@keyframes auth-cursor {

  0%,
  49% {
    opacity: 1;
  }

  50%,
  100% {
    opacity: 0;
  }
}

.auth-form {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: var(--bg-100);
}

.auth-form__card {
  width: 100%;
  max-width: 400px;
}

.auth-form__heading {
  margin: 0;
  font-family: 'Orbitron Variable', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 30px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--nap-ink);
}

.auth-form__hint {
  margin: 10px 0 30px;
  font-size: 15px;
  color: var(--nap-muted);
}

.auth-form__card :deep(.t-form-item) {
  margin-bottom: 20px;
}

.auth-form__card :deep(.t-input) {
  height: 44px;
  font-size: 15px;
}

@media (max-width: 900px) {
  .auth-page {
    grid-template-columns: 1fr;
  }

  .auth-brand {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {

  .auth-brand,
  .auth-brand__glow,
  .auth-brand__grid,
  .auth-brand__stars,
  .auth-brand__stars--b {
    animation: none;
  }

  .auth-brand__letter,
  .auth-brand__title::after,
  .auth-brand__cursor {
    animation: none;
  }

  .auth-brand__cursor {
    display: none;
  }
}
</style>