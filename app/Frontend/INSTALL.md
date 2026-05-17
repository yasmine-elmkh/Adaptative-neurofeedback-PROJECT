# NeuroCap Frontend — Installation

## Nouvelles dépendances (v2.0)

```bash
cd app/Frontend
npm install
```

Les packages suivants ont été ajoutés :

| Package | Version | Usage |
|---------|---------|-------|
| `i18next` | ^23.7.6 | Moteur i18n |
| `react-i18next` | ^14.0.0 | Bindings React |
| `i18next-browser-languagedetector` | ^8.0.0 | Détection automatique langue |

## Lancer le frontend

```bash
npm run dev
```

## Fonctionnalités ajoutées

### Langue (FR / EN / AR)
- Sélecteur dans la navbar (header) et sur les pages Login/Register
- Détection automatique depuis `localStorage` → `navigator`
- Stockage dans `localStorage.neurocap_language`
- Arabe : RTL automatique (`dir="rtl"`, police Cairo)

### Thème (Clair / Sombre / Système)
- Icône dans la navbar : ☀️ Clair | 🌙 Sombre | 🖥️ Système
- Détection OS quand mode = "Système"
- Stockage dans `localStorage.neurocap_theme`
- Transition CSS douce (200ms)

### Design professionnel
- Palette de couleurs CSS variables (auto-switch clair/sombre)
- Composants : `card`, `btn-primary`, `btn-secondary`, `btn-ghost`, `badge-*`, `input`, `label`
- Animations : `animate-fade-in`, `animate-slide-up`
- Scrollbar stylée, focus rings accessibles
- Layout responsive avec drawer mobile
