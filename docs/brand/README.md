# NAP 品牌标识

**手写的 N。** N 是躺下的 Z，也是品牌名首字母；它由三笔手写笔画叠成，整体向右倾斜 12°，
颜色从左下角的**夜青**一路流到右上角的**灯金** —— 渐变取代了硬切，交接没有接缝。

预览：浏览器打开 [`showcase.html`](./showcase.html)。

## 颜色

| 名称 | 色值 | 用途 |
|------|------|------|
| Night Teal | `#124A4E` | 渐变起点、字标 |
| Harbor | `#296266` | 辅助色、界面悬停 |
| Paper | `#F7F1E4` | 图标底、浅底 |
| Lamp | `#D2A054` | 渐变终点、金色句点 |
| Midnight | `#0E2B2E` | 深色模式底色 |

### 渐变

45°，左下 → 右上。渐变用 `gradientUnits="userSpaceOnUse"` 铺在整枚标记上，
三笔共用同一道坡，所以笔画之间看不出分段：

| 位置 | 色值 |
|------|------|
| 0% | `#124A4E` Night Teal |
| 45% | `#2C6668` Harbor |
| 80% | `#7C7B57` Patina |
| 100% | `#D2A054` Lamp |

深色底上整体提亮一档，起点换成 `#3F8080`，否则起点会消失在底色里。

## 构成

- 图标：96 × 96 网格，圆角 26，三笔手写笔画（竖 / 斜 / 竖），右倾 12°，中段最重、两端收细，收笔圆头。
- 三笔在接缝处轻微重叠，肉眼读成一笔；笔画中心线略弯，避免几何感。
- 小尺寸（≤24px）：`icon-small.svg` 把笔画加粗约 1.5，终点压深到 `#B8863C`。
- 字标：156 × 80 网格，线宽 8，金色句点。几何单线，与手写图标形成松紧对比。
- 横版组合：图标 80 + 字标，字标线宽落到 7.5，与图标视觉等重。

## 文件

| 文件 | 用途 |
|------|------|
| `icon.svg` | 主图标：纸白方 + 完整渐变 |
| `icon-small.svg` | ≤24px 用：终点压深到 `#B8863C`，防止金色端糊掉 |
| `icon-circle.svg` | 圆形头像、社交头像 |
| `icon-midnight.svg` | 深色界面里的图标（午夜底 + 提亮渐变） |
| `mark-reversed.svg` | 无底反白，压在任意深色背景上 |
| `lockup.svg` | 图标 + 字标（浅底） |
| `lockup-reversed.svg` | 图标 + 字标（深底） |
| `wordmark.svg` / `wordmark-reversed.svg` | 只有字标 |

## 使用规则

**留白**：四周至少留出图标高度的 1/4；横版里图标与字标间距固定为图标宽度的 30%。

**最小尺寸**
- 方图标：24px 用 `icon-small.svg`，16px 也可读
- 圆章：24px
- 字标：80px 宽
- 横版组合：120px 宽

**可以**
- 深底用 `icon-midnight.svg` / `mark-reversed.svg` / `*-reversed.svg`
- 单色印刷时整枚标记用 Night Teal 或纯黑，渐变视为一色
- 搭配 Paper 或纯白底

**不可以**
- 拉伸、旋转、加阴影或发光
- 反转渐变方向，或把渐变拆成两条独立色带
- 在深色底上直接用 `icon.svg`（纸白方会变成一块亮补丁）
- 在花纹背景上不加留白直接使用

## 接入前端

1. 用 `icon.svg` 覆盖 `nap-frontend/public/nap-logo.svg`（`index.html` 已经引用，不用改代码）。
2. 侧边栏头部：`icon.svg` 38px + `wordmark.svg` 30px。
3. 需要 PNG：

```bash
magick -background none docs/brand/icon.svg -resize 512x512 icon-512.png
```

## 文件结构

```
docs/brand/
  showcase.html          标识总览：主标 / 渐变 / 变体 / 字标 / 应用模拟
  icon.svg               主图标
  icon-small.svg         小尺寸图标
  icon-circle.svg        圆章
  icon-midnight.svg      深色底图标
  mark-reversed.svg      无底反白
  lockup.svg             横版组合
  lockup-reversed.svg    横版组合 · 反白
  wordmark.svg           字标
  wordmark-reversed.svg  字标 · 反白
```
