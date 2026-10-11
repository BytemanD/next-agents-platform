/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'markdown-it' {
  export interface Options {
    html?: boolean
    linkify?: boolean
    breaks?: boolean
    highlight?: (str: string, lang: string) => string
    [key: string]: unknown
  }
  export default class MarkdownIt {
    constructor(options?: Options)
    render(src: string, env?: unknown): string
  }
}
