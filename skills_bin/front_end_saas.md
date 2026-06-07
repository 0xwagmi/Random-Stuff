# SaaS Landing Page Design System

Production-grade CSS values extracted from top-tier SaaS landing pages.
Use this to avoid generic AI-generated CSS patterns.

---

## Typography

| Element | Font | Size | Weight | Line-height | Letter-spacing |
|---------|------|------|--------|-------------|----------------|
| H1 hero | Display/bold sans | 60px | 700 | 70px | -1px |
| H2 section | Display/bold sans | 40px | 700 | 48px | -0.5px |
| Body | Clean sans (IBM Plex Sans, Inter) | 18px | 400 | 28px | normal |
| Subheadline | Clean sans | 22px | 500 | 28px | 0.25px |
| Buttons | Clean sans | 16px | 600 | 22px | -0.04px |
| Section labels | Clean sans | 12px | 400 | — | widest (0.1em+) |

**Tailwind recipe for hero h1:**
```
text-[60px] font-bold leading-[70px] tracking-[-1px]
```

---

## Colors (Light SaaS)

| Token | Value | Usage |
|-------|-------|-------|
| Page bg | `#ffffff` | Everything |
| H1/H2 | `#000000` | Headings |
| Body text | `#565656` | Paragraphs, card descriptions |
| Secondary text | `#373D42` | Nav items, labels |
| Near-black label | `#171717` | Feature names, badges |
| Accent | `#3b5bdb` | One place only — hero word, links |
| Alt section bg | `#f8f9ff` | Alternating section bg |
| Card bg | `#f4f5fb` | Screenshot containers |
| Border default | `rgba(0,0,0,0.06)` | Dividers, card borders |
| Border hover | `rgba(0,0,0,0.20)` | Card hover |

---

## Buttons

### Primary (filled pill)
```css
background: #000;
color: #fff;
border: 1px solid #000;
border-radius: 9999px;
padding: 12px 20px;
font-size: 16px;
font-weight: 600;
letter-spacing: -0.04px;
```
**Tailwind:** `bg-black text-white border border-black rounded-full px-5 py-3 text-sm font-semibold hover:bg-zinc-800`

### Secondary (outlined pill)
```css
background: #fff;
color: #000;
border: 1px solid #000;
border-radius: 30px;
padding: 16px 30px;
font-size: 16px;
font-weight: 600;
```
**Tailwind:** `bg-white text-black border border-black rounded-[30px] px-8 py-3 text-sm font-semibold hover:bg-zinc-50`

> Rule: **always pill buttons** — never `rounded-lg`, never `rounded-xl`. Pill = `rounded-full` or `rounded-[30px]`.

---

## Navigation

```css
position: sticky; top: 0; z-index: 50;
background: rgba(255,255,255,0.9);
backdrop-filter: blur(12px);
border-bottom: 1px solid rgba(0,0,0,0.06);
height: 64px;
```

Logo: small circular icon (28px) + brand name `font-semibold text-sm`.
Nav links: plain, `color: #000`, `font-weight: 400`. No underlines.
Right side: "Login" text link + filled pill CTA.

**Tailwind nav:**
```
sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-black/[0.06] h-16
```

---

## Hero Section

```
text-align: center
padding-top: 80px
padding-bottom: 32px
max-width: 756px on h1
```

**Rotating accent text (correct implementation):**
```tsx
// Container clips overflow so only one word shows at a time
// height: 80px; overflow: hidden;

// Each word: position absolute, animates translateY(100%→0) on enter
// Fade: opacity 0→1 in, 1→0 out
// Timing: ~2.5s per word, cubic-bezier(0.25, 0.46, 0.45, 0.94)

// Simple React implementation:
const [index, setIndex] = useState(0);
const [visible, setVisible] = useState(true);
useEffect(() => {
  const t = setInterval(() => {
    setVisible(false);
    setTimeout(() => { setIndex(i => (i+1) % words.length); setVisible(true); }, 300);
  }, 2500);
  return () => clearInterval(t);
}, []);
// style: opacity + translateY transition, color: #3b5bdb
```

---

## Cards

```css
border: 1px solid rgba(0,0,0,0.08);
border-radius: 16px;
padding: 24px;
background: white;
/* no box-shadow — border only */
```
Hover: `border-color: rgba(0,0,0,0.20)` — no shadow on hover either.

**Tailwind:** `border border-black/[0.08] rounded-2xl p-6 hover:border-black/20 transition-colors`

---

## Section Layout

| Section | Background | Vertical padding |
|---------|-----------|-----------------|
| Nav | `white/90` blur | 16px (h-16) |
| Hero | white | `pt-20 pb-8` |
| Product screenshot | white | `pb-20` |
| Features grid | white | `py-24` |
| How it works | `#f8f9ff` | `py-24` |
| Bottom CTA | white | `py-28` |
| Footer | white | `py-8` |

**Alternating bg pattern:** white → white → white → `#f8f9ff` → white. Not every section, just one mid-page.

Dividers: `border-top: 1px solid rgba(0,0,0,0.06)` — never `hr`, never thick lines.

Max widths: `max-w-6xl` nav, `max-w-4xl` hero, `max-w-5xl` features. Always `px-6` padding.

---

## What Kills the "Generic AI Look"

| Bad (generic AI) | Good (production SaaS) |
|-----------------|----------------------|
| `rounded-xl` buttons | `rounded-full` pill buttons |
| `bg-gradient-to-r from-violet-500` everywhere | One accent color, one place |
| Multiple glow effects / `blur-[120px]` blobs | No glows. Clean white bg. |
| `text-zinc-400` body text | `#565656` — warm medium gray |
| `border-[#262626]` dark cards | `border-black/[0.08]` light cards |
| `text-5xl` h1 no letter-spacing | `-1px` letter-spacing on large text |
| Section backgrounds all different colors | White + one light tint (`#f8f9ff`) |
| Gradient text everywhere | Plain black heading, ONE blue accent |
| Stats with emojis or icons | Just number + small caps label below |

---

## Grid Patterns

```
Features: grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6
Steps: grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8
Stats: grid-cols-3 gap-8 text-center
Logos: flex flex-wrap justify-center gap-8 opacity-50
```

---

## Dark Mode Equivalent

When adapting these patterns to dark theme, substitute:

| Light | Dark |
|-------|------|
| `#ffffff` page bg | `#0a0a0a` |
| `#000000` heading | `#fafafa` |
| `#565656` body | `#71717a` |
| `rgba(0,0,0,0.06)` border | `rgba(255,255,255,0.06)` |
| `rgba(0,0,0,0.08)` card border | `rgba(255,255,255,0.07)` |
| `#f8f9ff` alt section | `#111111` |
| black filled button | white filled button |
| `border-black` | `border-white` |

Keep: pill buttons, -1px letter-spacing, same font sizes, same section padding.

