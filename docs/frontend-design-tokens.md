# Frontend Design Tokens

## 1. Token Rules

1. Use semantic tokens, not hardcoded hex values in components.
2. Keep palette minimal and utility-focused.
3. Ensure WCAG AA contrast for text and actionable controls.
4. Tokens are source of truth for both EN and RU UI.

## 2. Color Tokens

## 2.1 Base
- `color.bg.default`: `#ffffff`
- `color.bg.subtle`: `#f7f8fa`
- `color.border.default`: `#d9dde4`
- `color.text.primary`: `#1b1f24`
- `color.text.secondary`: `#4a5563`

## 2.2 Status
- `color.status.success`: `#0f8f4f`
- `color.status.warning`: `#b07300`
- `color.status.error`: `#c62828`
- `color.status.info`: `#1769aa`

## 2.3 Interaction
- `color.action.primary.bg`: `#1769aa`
- `color.action.primary.text`: `#ffffff`
- `color.action.primary.bg.hover`: `#145989`
- `color.focus.ring`: `#4d90fe`

## 3. Typography Tokens

- `font.family.base`: `Inter, Arial, sans-serif`
- `font.size.xs`: `12px`
- `font.size.sm`: `14px`
- `font.size.md`: `16px`
- `font.size.lg`: `20px`
- `font.size.xl`: `28px`
- `font.weight.regular`: `400`
- `font.weight.medium`: `500`
- `font.weight.bold`: `700`
- `line.height.tight`: `1.25`
- `line.height.normal`: `1.5`

## 4. Spacing Tokens

- `space.1`: `4px`
- `space.2`: `8px`
- `space.3`: `12px`
- `space.4`: `16px`
- `space.5`: `20px`
- `space.6`: `24px`
- `space.8`: `32px`

## 5. Radius and Elevation

- `radius.sm`: `6px`
- `radius.md`: `10px`
- `radius.lg`: `14px`
- `shadow.card`: `0 1px 3px rgba(0,0,0,0.08)`
- `shadow.popover`: `0 6px 20px rgba(0,0,0,0.15)`

## 6. Component Token Mapping

- Buttons:
  - primary uses `color.action.primary.*`
- Cards:
  - background `color.bg.default`
  - border `color.border.default`
  - shadow `shadow.card`
- Status badge:
  - map freshness to status color set

## 7. Motion Tokens

- `motion.fast`: `120ms`
- `motion.normal`: `180ms`
- `motion.ease.standard`: `cubic-bezier(0.2, 0, 0, 1)`

Rule: avoid decorative animation on critical data loads.

## 8. Anti-Requirements

- No gradient-heavy themes.
- No dark mode in MVP unless explicitly requested.
- No more than one primary accent color.
