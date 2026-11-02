<template>
  <div ref="rootEl" class="landing" @scroll="onScroll">
    <!-- ===== 导航 ===== -->
    <t-header class="landing__nav" :class="{ 'is-scrolled': scrolled }">
      <div class="landing__nav-inner">
        <a class="landing__brand" href="#top" @click.prevent="scrollTop">
          <img src="/brand/lockup-reversed.svg" alt="NAP" />
        </a>

        <nav class="landing__nav-links">
          <a href="#capabilities" @click.prevent="goToSection('capabilities')">能力</a>
          <a href="#workflow" @click.prevent="goToSection('workflow')">工作方式</a>
        </nav>

        <t-space class="landing__nav-actions" :size="10" align="center">
          <t-button variant="text" class="landing__nav-login" @click="start">
            {{ auth.token ? '工作台' : '登录' }}
          </t-button>
          <t-button theme="primary" shape="round" class="btn-gold" @click="start">
            开始使用
          </t-button>
        </t-space>
      </div>
    </t-header>

    <t-content class="landing__content">
      <!-- ===== Hero ===== -->
      <section id="top" class="hero">
        <div class="hero__stars hero__stars--a"></div>
        <div class="hero__stars hero__stars--b"></div>
        <div class="hero__dawn"></div>
        <div class="hero__spotlight"></div>

        <div class="hero__copy">
          <span class="hero__eyebrow">
            <i class="hero__dot"></i>
            NAP · Next Agents Platform
          </span>

          <h1 class="hero__title">
            把任务交给 NAP，<br />
            <em>安心去打个盹。</em>
          </h1>

          <p class="hero__lead">
            从创建智能体，到接上知识、工具与 MCP。NAP 在你睡着的时候继续工作，
            天亮时，你只需要看结果。
          </p>

          <t-space class="hero__actions" :size="14" align="center">
            <t-button theme="primary" shape="round" size="large" class="btn-gold" @click="start">
              开始使用
              <template #suffix>
                <t-icon name="arrow-right" />
              </template>
            </t-button>
            <t-button variant="outline" shape="round" size="large" class="btn-ghost" @click="goToSection('workflow')">
              看看怎么用
            </t-button>
          </t-space>
          <br>
          <t-space class="hero__tags" :size="8" break-line>
            <t-tag v-for="tag in heroTags" :key="tag" shape="round" theme="primary">
              {{ tag }}
            </t-tag>
          </t-space>
        </div>

        <div class="hero__visual" aria-hidden="true">
          <div class="orbit">
            <span class="orbit__halo"></span>

            <div class="orbit__ring orbit__ring--1">
              <span class="orbit__node orbit__node--1"><t-icon name="robot" size="20px" /></span>
            </div>
            <div class="orbit__ring orbit__ring--2">
              <span class="orbit__node orbit__node--2"><t-icon name="book" size="20px" /></span>
            </div>
            <div class="orbit__ring orbit__ring--3">
              <span class="orbit__node orbit__node--3"><t-icon name="tools" size="20px" /></span>
            </div>

            <div class="orbit__core">
              <span class="orbit__pulse"></span>
              <img src="/brand/mark-reversed.svg" alt="" />
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 能力 ===== -->
      <section id="capabilities" class="section section--light">
        <header class="section__head reveal">
          <span class="section__label">What it does</span>
          <h2 class="section__title">一个人的团队，<br />整晚都在工作。</h2>
          <p class="section__sub">
            模型、知识、工具和观测被放进同一个平台。你不必在四五个控制台之间来回切换，
            只需要描述目标。
          </p>
        </header>

        <t-row :gutter="[20, 20]">
          <t-col v-for="(item, i) in capabilities" :key="item.title" :xs="12" :sm="6" :md="3">
            <t-card :bordered="false" class="feature-card reveal" :class="`reveal--d${i + 1}`">
              <div class="feature-card__top">
                <span class="feature-card__icon">
                  <t-icon :name="item.icon" size="24px" />
                </span>
                <span class="feature-card__index">{{ item.index }}</span>
              </div>
              <h3 class="feature-card__title">{{ item.title }}</h3>
              <p class="feature-card__desc">{{ item.desc }}</p>
            </t-card>
          </t-col>
        </t-row>
      </section>

      <!-- ===== 工作方式 ===== -->
      <section id="workflow" class="section section--night">
        <header class="section__head reveal">
          <span class="section__label">How it works</span>
          <h2 class="section__title">从一句话，<br />到一件做完的事。</h2>
          <p class="section__sub">
            不需要复杂的配置。把目标和边界讲清楚，剩下的交给智能体自己规划、调用和执行。
          </p>
        </header>

        <div class="workflow__steps reveal">
          <t-steps :layout="isNarrow ? 'vertical' : 'horizontal'" theme="default" readonly>
            <t-step-item v-for="step in steps" :key="step.title" :title="step.title" :content="step.content" />
          </t-steps>
        </div>

        <div class="workflow__foot reveal">
          <t-space :size="10" align="center">
            <t-icon name="moon" class="workflow__foot-icon" />
            <span>你睡觉的这段时间，正是它最忙的时候。</span>
          </t-space>
        </div>
      </section>

      <!-- ===== CTA ===== -->
      <section class="cta">
        <div class="cta__card reveal">
          <span class="cta__glow"></span>
          <span class="cta__label">Hand it over</span>
          <h2 class="cta__title">今晚，把任务留给 NAP。</h2>
          <p class="cta__sub">你负责睡觉，它负责交付。</p>
          <t-space :size="14" align="center">
            <t-button theme="primary" shape="round" size="large" class="btn-gold" @click="start">
              {{ auth.token ? '进入工作台' : '免费开始' }}
              <template #suffix>
                <t-icon name="arrow-right" />
              </template>
            </t-button>
            <t-button variant="text" size="large" class="cta__more" @click="goToSection('workflow')">
              了解工作方式
            </t-button>
          </t-space>
        </div>
      </section>
    </t-content>

    <!-- ===== Footer ===== -->
    <t-footer class="landing__footer">
      <div class="landing__footer-inner">
        <div class="landing__footer-brand">
          <img src="/brand/lockup-reversed.svg" alt="NAP" />
          <p>把任务交给我们，安心打个盹。</p>
        </div>

        <t-space class="landing__footer-links" :size="28" align="center">
          <a href="#capabilities" @click.prevent="goToSection('capabilities')">能力</a>
          <a href="#workflow" @click.prevent="goToSection('workflow')">工作方式</a>
          <a href="#top" @click.prevent="start">进入工作台</a>
        </t-space>
      </div>

      <t-divider class="landing__footer-rule" />

      <div class="landing__footer-base">
        <span>© {{ year }} NAP · Next Agents Platform</span>
        <span class="landing__footer-mono">HAND IT OVER. TAKE A NAP.</span>
      </div>
    </t-footer>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMediaQuery } from '@vueuse/core'
import '@fontsource-variable/orbitron'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const rootEl = ref<HTMLElement | null>(null)
const scrolled = ref(false)
const year = new Date().getFullYear()

const isNarrow = useMediaQuery('(max-width: 860px)')
const reducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)')

let observer: IntersectionObserver | undefined
let heroEl: HTMLElement | null = null
let rafId = 0

const heroTags = ['多模型接入', '知识库增强', '工具与 MCP', '实时观测']

const capabilities = [
  {
    index: '01',
    icon: 'robot',
    title: '智能体编排',
    desc: '选择模型、写下指令，几分钟内搭好一个真正能用的智能体。',
  },
  {
    index: '02',
    icon: 'book',
    title: '知识库增强',
    desc: '上传文档或网页，让回答有据可依，而不是凭空猜测。',
  },
  {
    index: '03',
    icon: 'tools',
    title: '工具与 MCP',
    desc: '接上搜索、数据库和自定义 MCP 服务，把对话变成行动。',
  },
  {
    index: '04',
    icon: 'chart-bar',
    title: '运行监控',
    desc: '调用、Token 与延迟一目了然，问题在变贵之前被发现。',
  },
]

const steps = [
  { title: '创建智能体', content: '选模型、写指令，划定它能做什么。' },
  { title: '接上知识与工具', content: '导入文档，挂载工具与 MCP 服务。' },
  { title: '交给 NAP', content: '发起对话，它自己规划、调用、执行。' },
  { title: '天亮看结果', content: '会话、用量、延迟，都留有记录。' },
]

function start() {
  router.push(auth.token ? '/dashboard' : '/login')
}

function scrollTop() {
  rootEl.value?.scrollTo({ top: 0, behavior: reducedMotion.value ? 'auto' : 'smooth' })
}

function goToSection(id: string) {
  document.getElementById(id)?.scrollIntoView({
    behavior: reducedMotion.value ? 'auto' : 'smooth',
    block: 'start',
  })
}

function onScroll() {
  scrolled.value = (rootEl.value?.scrollTop ?? 0) > 16
}

function onPointerMove(event: PointerEvent) {
  if (!heroEl || reducedMotion.value) return
  const rect = heroEl.getBoundingClientRect()
  if (rafId) return
  rafId = window.requestAnimationFrame(() => {
    rafId = 0
    if (!heroEl) return
    heroEl.style.setProperty('--mx', `${((event.clientX - rect.left) / rect.width) * 100}%`)
    heroEl.style.setProperty('--my', `${((event.clientY - rect.top) / rect.height) * 100}%`)
  })
}

onMounted(() => {
  heroEl = rootEl.value?.querySelector('.hero') ?? null
  heroEl?.addEventListener('pointermove', onPointerMove)

  const reveals = rootEl.value?.querySelectorAll<HTMLElement>('.reveal') ?? []
  if (reducedMotion.value || !('IntersectionObserver' in window)) {
    reveals.forEach((el) => el.classList.add('is-visible'))
    return
  }

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return
        entry.target.classList.add('is-visible')
        observer?.unobserve(entry.target)
      })
    },
    { root: rootEl.value, threshold: 0.14, rootMargin: '0px 0px -6% 0px' },
  )
  reveals.forEach((el) => observer?.observe(el))
})

onBeforeUnmount(() => {
  observer?.disconnect()
  heroEl?.removeEventListener('pointermove', onPointerMove)
  if (rafId) window.cancelAnimationFrame(rafId)
})
</script>

<style scoped>
.landing {
  --lp-ink: #07282a;
  --lp-ink-2: #0b3437;
  --lp-teal: #296266;
  --lp-teal-soft: #4a8185;
  --lp-gold: #d2a054;
  --lp-gold-deep: #a8824a;
  --lp-cream: #f7f1e4;
  --lp-paper: #fffbf2;

  position: relative;
  height: 100%;
  width: 100%;
  overflow-x: hidden;
  overflow-y: auto;
  scroll-behavior: smooth;
  background: var(--lp-paper);
  color: var(--lp-ink);
  font-family: var(--font-display);
  -webkit-font-smoothing: antialiased;
}

/* ===== 导航 ===== */
.landing__nav {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 30;
  height: auto;
  background: transparent;
  transition:
    background 0.35s ease,
    box-shadow 0.35s ease,
    backdrop-filter 0.35s ease;
}

.landing__nav.is-scrolled {
  background: rgba(6, 31, 33, 0.78);
  backdrop-filter: blur(16px) saturate(140%);
  box-shadow: 0 1px 0 rgba(210, 160, 84, 0.16);
}

.landing__nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  height: 76px;
  padding: 0 clamp(20px, 5vw, 72px);
}

.landing__brand {
  display: inline-flex;
  align-items: center;
  flex: none;
}

.landing__brand img {
  height: 34px;
  display: block;
}

.landing__nav-links {
  display: flex;
  align-items: center;
  gap: clamp(20px, 3vw, 40px);
  font-family: var(--font-body);
  font-size: 14px;
  letter-spacing: 0.02em;
}

.landing__nav-links a {
  position: relative;
  color: rgba(247, 241, 228, 0.66);
  text-decoration: none;
  padding: 6px 0;
  transition: color 0.25s ease;
}

.landing__nav-links a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, var(--lp-gold), transparent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.landing__nav-links a:hover {
  color: #fff;
}

.landing__nav-links a:hover::after {
  transform: scaleX(1);
}

.landing__nav-actions :deep(.t-button--variant-text) {
  color: rgba(247, 241, 228, 0.72);
  font-family: var(--font-body);
}

.landing__nav-actions :deep(.t-button--variant-text:hover) {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
}

/* ===== 按钮 ===== */
.btn-gold.t-button {
  position: relative;
  border-color: transparent;
  background: linear-gradient(120deg, #e7bd73 0%, #d2a054 48%, #c08f43 100%);
  color: #08292b;
  font-weight: 600;
  letter-spacing: 0.01em;
  box-shadow: 0 12px 30px -12px rgba(210, 160, 84, 0.7);
  overflow: hidden;
}

.btn-gold.t-button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 32%, rgba(255, 255, 255, 0.55) 50%, transparent 68%);
  transform: translateX(-120%);
  animation: btn-shine 5s ease-in-out infinite;
  pointer-events: none;
}

.btn-gold.t-button:hover {
  background: linear-gradient(120deg, #f0ca83 0%, #dcae60 48%, #cc9a4c 100%);
  color: #07282a;
  box-shadow: 0 16px 38px -12px rgba(210, 160, 84, 0.85);
}

.btn-gold.t-button:active {
  background: linear-gradient(120deg, #d2a054 0%, #bd8d42 100%);
}

.btn-ghost.t-button {
  border: 1px solid rgba(247, 241, 228, 0.24);
  background: rgba(255, 255, 255, 0.03);
  color: rgba(247, 241, 228, 0.86);
  font-weight: 500;
}

.btn-ghost.t-button:hover {
  border-color: rgba(210, 160, 84, 0.6);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

/* ===== Hero ===== */
.hero {
  position: relative;
  isolation: isolate;
  display: grid;
  grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.98fr);
  align-items: center;
  gap: clamp(24px, 4vw, 56px);
  min-height: 100vh;
  padding: clamp(90px, 12vh, 150px) clamp(20px, 5vw, 72px) clamp(120px, 16vh, 190px);
  overflow: hidden;
  color: #fff;
  background:
    radial-gradient(110% 80% at 82% 6%, rgba(41, 98, 102, 0.55), transparent 62%),
    radial-gradient(90% 80% at 4% 96%, rgba(168, 130, 74, 0.16), transparent 58%),
    linear-gradient(158deg, #061f21 0%, #08292b 46%, #0c3538 100%);
}

/* 星空 */
.hero__stars {
  position: absolute;
  inset: -25%;
  z-index: 0;
  pointer-events: none;
  background-repeat: repeat;
  animation: star-drift 90s linear infinite;
}

.hero__stars--a {
  opacity: 0.75;
  background-image:
    radial-gradient(1.4px 1.4px at 12% 22%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1.2px 1.2px at 38% 8%, rgba(185, 243, 247, 0.8), transparent),
    radial-gradient(1px 1px at 66% 34%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1.6px 1.6px at 84% 18%, rgba(210, 160, 84, 0.75), transparent),
    radial-gradient(1px 1px at 24% 58%, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(1.3px 1.3px at 52% 72%, rgba(185, 243, 247, 0.55), transparent),
    radial-gradient(1px 1px at 78% 62%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1.5px 1.5px at 92% 88%, rgba(210, 160, 84, 0.5), transparent),
    radial-gradient(1px 1px at 8% 86%, rgba(255, 255, 255, 0.55), transparent);
  background-size: 340px 340px;
  animation-duration: 120s;
}

.hero__stars--b {
  opacity: 0.45;
  background-image:
    radial-gradient(1px 1px at 16% 44%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1.8px 1.8px at 44% 16%, rgba(255, 255, 255, 0.55), transparent),
    radial-gradient(1px 1px at 72% 50%, rgba(185, 243, 247, 0.6), transparent),
    radial-gradient(1.2px 1.2px at 30% 78%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 88% 36%, rgba(210, 160, 84, 0.55), transparent),
    radial-gradient(1.4px 1.4px at 60% 92%, rgba(255, 255, 255, 0.45), transparent);
  background-size: 520px 520px;
  animation-direction: reverse;
  animation-duration: 160s;
}

.hero__dawn {
  position: absolute;
  right: -12%;
  bottom: -28%;
  z-index: 0;
  width: 70%;
  height: 62%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(210, 160, 84, 0.22) 0%, rgba(210, 160, 84, 0.06) 45%, transparent 68%);
  filter: blur(30px);
  pointer-events: none;
}

.hero__spotlight {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background: radial-gradient(420px circle at var(--mx, 70%) var(--my, 26%),
      rgba(210, 160, 84, 0.14),
      transparent 70%);
}

.hero__copy {
  position: relative;
  z-index: 2;
  max-width: 620px;
}

.hero__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-family: 'Orbitron Variable', var(--font-display);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(247, 241, 228, 0.58);
  animation: rise 0.9s cubic-bezier(0.2, 0.7, 0.3, 1) 0.05s both;
}

.hero__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--lp-gold);
  box-shadow: 0 0 0 2px rgba(210, 160, 84, 0.18);
  animation: blink 2.6s ease-in-out infinite;
}

.hero__title {
  margin: 22px 0 0;
  font-size: clamp(38px, 5.2vw, 74px);
  font-weight: 600;
  line-height: 1.08;
  letter-spacing: -0.025em;
  animation: rise 0.95s cubic-bezier(0.2, 0.7, 0.3, 1) 0.14s both;
}

.hero__title em {
  font-style: normal;
  background: linear-gradient(100deg, #d2a054 0%, #f6dfb2 42%, #d2a054 78%);
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: gold-flow 8s ease-in-out infinite;
}

.hero__lead {
  max-width: 32em;
  margin: 26px 0 0;
  font-family: var(--font-body);
  font-size: clamp(14px, 1.25vw, 16px);
  line-height: 1.9;
  color: rgba(247, 241, 228, 0.64);
  animation: rise 0.95s cubic-bezier(0.2, 0.7, 0.3, 1) 0.24s both;
}

.hero__actions {
  margin-top: 36px;
  animation: rise 0.95s cubic-bezier(0.2, 0.7, 0.3, 1) 0.34s both;
}

.hero__tags {
  margin-top: 34px;
  animation: rise 0.95s cubic-bezier(0.2, 0.7, 0.3, 1) 0.44s both;
}

.hero__tags :deep(.t-tag.t-tag--variant-outline) {
  height: 30px;
  padding: 0 13px;
  border-color: rgba(247, 241, 228, 0.16);
  background: rgba(255, 255, 255, 0.035);
  color: rgba(247, 241, 228, 0.62);
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 400;
}

/* ===== 轨道视觉 ===== */
.hero__visual {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  min-height: min(52vw, 560px);
  animation: visual-in 1.3s cubic-bezier(0.2, 0.7, 0.3, 1) 0.2s both;
}

.orbit {
  position: relative;
  width: min(44vw, 520px);
  aspect-ratio: 1;
}

.orbit__halo {
  position: absolute;
  inset: 8%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(210, 160, 84, 0.16) 0%, rgba(41, 98, 102, 0.18) 42%, transparent 68%);
  filter: blur(28px);
  animation: halo-breathe 7s ease-in-out infinite;
}

.orbit__ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(210, 160, 84, 0.2);
}

.orbit__ring--1 {
  inset: 0;
  animation: spin 30s linear infinite;
}

.orbit__ring--2 {
  inset: 12%;
  border-style: dashed;
  border-color: rgba(185, 243, 247, 0.16);
  animation: spin 44s linear infinite reverse;
}

.orbit__ring--3 {
  inset: 25%;
  border-color: rgba(210, 160, 84, 0.16);
  animation: spin 60s linear infinite;
}

.orbit__node {
  position: absolute;
  top: -21px;
  left: 50%;
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  margin-left: -21px;
  border-radius: 50%;
  border: 1px solid rgba(210, 160, 84, 0.5);
  background: rgba(7, 40, 42, 0.9);
  color: #e6c286;
  box-shadow:
    0 0 0 6px rgba(210, 160, 84, 0.05),
    0 10px 28px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(6px);
}

.orbit__node--1 {
  animation: counter-spin 30s linear infinite;
}

.orbit__node--2 {
  animation: spin 44s linear infinite;
}

.orbit__node--3 {
  animation: counter-spin 60s linear infinite;
}

.orbit__core {
  position: absolute;
  inset: 35%;
  display: grid;
  place-items: center;
  border-radius: 50%;
  border: 1px solid rgba(210, 160, 84, 0.32);
  background: radial-gradient(circle at 32% 26%, #1d5054 0%, #0a3033 48%, #07282a 100%);
  box-shadow:
    inset 0 0 44px rgba(210, 160, 84, 0.14),
    0 0 80px rgba(210, 160, 84, 0.14);
}

.orbit__core img {
  display: block;
  width: 58%;
  filter: drop-shadow(0 0 18px rgba(210, 160, 84, 0.35));
}

.orbit__pulse {
  position: absolute;
  inset: -1px;
  border-radius: 50%;
  border: 1px solid rgba(210, 160, 84, 0.42);
  animation: pulse-ring 4.2s cubic-bezier(0.2, 0.6, 0.3, 1) infinite;
}

/* ===== 通用 section ===== */
.section {
  position: relative;
  scroll-margin-top: 76px;
  padding: clamp(72px, 10vw, 130px) clamp(20px, 5vw, 72px);
}

.section--light {
  background: var(--lp-cream);
}

.section__head {
  max-width: 760px;
  margin-bottom: clamp(36px, 5vw, 64px);
}

.section__label {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-family: 'Orbitron Variable', var(--font-display);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--lp-gold-deep);
}

.section__label::before {
  content: '';
  width: 22px;
  height: 1px;
  background: currentColor;
}

.section__title {
  margin: 16px 0 0;
  font-size: clamp(28px, 3.6vw, 46px);
  font-weight: 600;
  line-height: 1.16;
  letter-spacing: -0.025em;
  color: var(--lp-ink);
}

.section__sub {
  max-width: 56ch;
  margin: 18px 0 0;
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.85;
  color: #5d6b68;
}

/* ===== 能力卡片 ===== */
.feature-card {
  height: 100%;
  border-radius: 18px;
  background: var(--lp-paper);
  border: 1px solid rgba(8, 41, 43, 0.07);
  box-shadow: 0 1px 0 rgba(8, 41, 43, 0.02);
  transition:
    transform 0.4s cubic-bezier(0.2, 0.7, 0.3, 1),
    box-shadow 0.4s ease,
    border-color 0.4s ease;
}

.feature-card:hover {
  transform: translateY(-6px);
  border-color: rgba(210, 160, 84, 0.45);
  box-shadow: 0 26px 50px -28px rgba(8, 41, 43, 0.35);
}

.feature-card :deep(.t-card__body) {
  height: 100%;
  padding: 26px 24px 28px;
}

.feature-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 22px;
}

.feature-card__icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  color: var(--lp-teal);
  background: linear-gradient(142deg, rgba(41, 98, 102, 0.12) 0%, rgba(210, 160, 84, 0.2) 100%);
  transition: transform 0.4s cubic-bezier(0.2, 0.7, 0.3, 1);
}

.feature-card:hover .feature-card__icon {
  transform: rotate(-7deg) scale(1.06);
}

.feature-card__index {
  font-family: 'Orbitron Variable', var(--font-display);
  font-size: 11px;
  letter-spacing: 0.16em;
  color: rgba(8, 41, 43, 0.24);
}

.feature-card__title {
  margin: 0;
  font-size: 19px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--lp-ink);
}

.feature-card__desc {
  margin: 10px 0 0;
  font-family: var(--font-body);
  font-size: 13.5px;
  line-height: 1.8;
  color: #63716e;
}

/* ===== 工作方式 ===== */
.section--night {
  overflow: hidden;
  color: #fff;
  background:
    radial-gradient(85% 100% at 88% 0%, rgba(41, 98, 102, 0.5), transparent 62%),
    radial-gradient(70% 80% at 0% 100%, rgba(168, 130, 74, 0.14), transparent 60%),
    linear-gradient(160deg, #08292b 0%, #061f21 100%);
}

.section--night::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(185, 243, 247, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(185, 243, 247, 0.045) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(80% 80% at 70% 30%, #000 0%, transparent 78%);
  -webkit-mask-image: radial-gradient(80% 80% at 70% 30%, #000 0%, transparent 78%);
  pointer-events: none;
}

.section--night .section__label {
  color: rgba(210, 160, 84, 0.9);
}

.section--night .section__title {
  color: #fff;
}

.section--night .section__sub {
  color: rgba(247, 241, 228, 0.58);
}

.workflow__steps {
  position: relative;
  z-index: 1;
}

.workflow__steps :deep(.t-steps .t-steps-item__icon--number) {
  width: 40px;
  height: 40px;
  border-color: rgba(210, 160, 84, 0.4);
  background: rgba(210, 160, 84, 0.06);
  color: var(--lp-gold);
  font-family: 'Orbitron Variable', var(--font-display);
  font-size: 15px;
}

.workflow__steps :deep(.t-steps .t-steps-item__title) {
  color: #fff;
  font-size: 17px;
  font-weight: 600;
}

.workflow__steps :deep(.t-steps .t-steps-item__description) {
  color: rgba(247, 241, 228, 0.56);
  font-family: var(--font-body);
  font-size: 13px;
  line-height: 1.75;
  max-width: 22em;
}

.workflow__steps :deep(.t-steps--horizontal .t-steps-item:not(:last-child) .t-steps-item__title::after) {
  border-color: rgba(210, 160, 84, 0.22);
}

.workflow__foot {
  position: relative;
  z-index: 1;
  margin-top: clamp(40px, 6vw, 72px);
  font-family: var(--font-body);
  font-size: 13.5px;
  color: rgba(247, 241, 228, 0.44);
}

.workflow__foot-icon {
  color: rgba(210, 160, 84, 0.7);
}

/* ===== CTA ===== */
.cta {
  padding: clamp(72px, 11vw, 140px) clamp(20px, 5vw, 72px);
  background: var(--lp-cream);
}

.cta__card {
  position: relative;
  max-width: 960px;
  margin: 0 auto;
  padding: clamp(40px, 6vw, 76px) clamp(28px, 5vw, 64px);
  overflow: hidden;
  border-radius: 28px;
  text-align: center;
  color: #fff;
  background:
    radial-gradient(120% 140% at 50% 130%, rgba(210, 160, 84, 0.4) 0%, transparent 58%),
    linear-gradient(145deg, #0c3538 0%, #08292b 55%, #061f21 100%);
  box-shadow: 0 48px 100px -56px rgba(8, 41, 43, 0.9);
}

.cta__card::after {
  content: '';
  position: absolute;
  top: -40%;
  right: -18%;
  width: 55%;
  aspect-ratio: 1;
  border-radius: 50%;
  border: 1px solid rgba(210, 160, 84, 0.18);
  box-shadow:
    0 0 0 40px rgba(210, 160, 84, 0.04),
    0 0 0 80px rgba(210, 160, 84, 0.03);
  pointer-events: none;
}

.cta__glow {
  position: absolute;
  left: 50%;
  bottom: -46%;
  width: 70%;
  aspect-ratio: 1;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(circle, rgba(210, 160, 84, 0.28) 0%, transparent 62%);
  filter: blur(24px);
  pointer-events: none;
}

.cta__label {
  position: relative;
  font-family: 'Orbitron Variable', var(--font-display);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(210, 160, 84, 0.85);
}

.cta__title {
  position: relative;
  margin: 18px 0 0;
  font-size: clamp(28px, 4vw, 50px);
  font-weight: 600;
  line-height: 1.14;
  letter-spacing: -0.025em;
}

.cta__sub {
  position: relative;
  margin: 14px 0 32px;
  font-family: var(--font-body);
  font-size: 15px;
  color: rgba(247, 241, 228, 0.58);
}

.cta__more.t-button {
  color: rgba(247, 241, 228, 0.66);
  font-family: var(--font-body);
}

.cta__more.t-button:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.06);
}

/* ===== Footer ===== */
.landing__footer {
  height: auto;
  padding: 52px clamp(20px, 5vw, 72px) 30px;
  color: rgba(247, 241, 228, 0.56);
  background: #061f21;
}

.landing__footer-inner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 32px;
  flex-wrap: wrap;
}

.landing__footer-brand img {
  display: block;
  height: 34px;
}

.landing__footer-brand p {
  margin: 14px 0 0;
  font-family: var(--font-body);
  font-size: 13px;
  color: rgba(247, 241, 228, 0.42);
}

.landing__footer-links a {
  color: rgba(247, 241, 228, 0.6);
  font-family: var(--font-body);
  font-size: 13.5px;
  text-decoration: none;
  transition: color 0.25s ease;
}

.landing__footer-links a:hover {
  color: var(--lp-gold);
}

.landing__footer-rule {
  margin: 34px 0 22px;
}

.landing__footer-rule.t-divider {
  border-color: rgba(247, 241, 228, 0.1);
}

.landing__footer-base {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  font-family: var(--font-body);
  font-size: 12px;
  color: rgba(247, 241, 228, 0.36);
}

.landing__footer-mono {
  font-family: 'Orbitron Variable', var(--font-display);
  font-size: 10px;
  letter-spacing: 0.22em;
  color: rgba(210, 160, 84, 0.55);
}

/* ===== 滚动显现 ===== */
.reveal {
  opacity: 0;
  transform: translateY(26px);
  transition:
    opacity 0.85s ease,
    transform 0.85s cubic-bezier(0.2, 0.7, 0.3, 1);
}

.reveal.is-visible {
  opacity: 1;
  transform: none;
}

.reveal--d1 {
  transition-delay: 0.06s;
}

.reveal--d2 {
  transition-delay: 0.13s;
}

.reveal--d3 {
  transition-delay: 0.2s;
}

.reveal--d4 {
  transition-delay: 0.27s;
}

/* ===== 动画 ===== */
@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(24px);
  }

  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes visual-in {
  from {
    opacity: 0;
    transform: scale(0.94) translateY(18px);
  }

  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes star-drift {
  from {
    transform: translate3d(0, 0, 0);
  }

  to {
    transform: translate3d(-180px, 120px, 0);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

@keyframes counter-spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(-360deg);
  }
}

@keyframes pulse-ring {
  0% {
    opacity: 0.7;
    transform: scale(1);
  }

  70% {
    opacity: 0;
    transform: scale(1.55);
  }

  100% {
    opacity: 0;
    transform: scale(1.55);
  }
}

@keyframes halo-breathe {

  0%,
  100% {
    opacity: 0.7;
    transform: scale(0.97);
  }

  50% {
    opacity: 1;
    transform: scale(1.04);
  }
}

@keyframes blink {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.3;
  }
}

@keyframes gold-flow {

  0%,
  100% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }
}

@keyframes btn-shine {

  0%,
  62% {
    transform: translateX(-120%);
  }

  82%,
  100% {
    transform: translateX(120%);
  }
}

/* ===== 响应式 ===== */
@media (max-width: 1100px) {
  .hero {
    grid-template-columns: 1fr;
    gap: 12px;
    padding-top: clamp(80px, 11vh, 120px);
  }

  .hero__copy {
    max-width: 680px;
  }

  .hero__visual {
    min-height: 0;
    margin-top: 8px;
  }

  .orbit {
    width: min(74vw, 440px);
  }
}

@media (max-width: 760px) {
  .landing__nav-links {
    display: none;
  }

  .landing__nav-inner {
    height: 66px;
  }

  .landing__nav-actions :deep(.t-button--variant-text) {
    display: none;
  }

  .hero {
    min-height: auto;
    padding-bottom: 96px;
  }

  .hero__title {
    font-size: clamp(34px, 9vw, 48px);
  }

  .hero__lead {
    margin-top: 20px;
  }

  .hero__actions :deep(.t-button) {
    flex: 1 1 auto;
  }

  .hero__visual {
    display: none;
  }

  .feature-card :deep(.t-card__body) {
    padding: 22px 20px 24px;
  }

  .landing__footer-inner {
    flex-direction: column;
    gap: 24px;
  }

  .landing__footer-base {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .landing {
    scroll-behavior: auto;
  }

  .hero__stars,
  .hero__eyebrow,
  .hero__dot,
  .hero__title,
  .hero__title em,
  .hero__lead,
  .hero__actions,
  .hero__tags,
  .hero__visual,
  .orbit__halo,
  .orbit__ring,
  .orbit__node,
  .orbit__pulse,
  .btn-gold.t-button::before {
    animation: none !important;
  }

  .reveal {
    opacity: 1 !important;
    transform: none !important;
    transition: none !important;
  }
}
</style>
