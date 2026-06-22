# working_intel

A working knowledge base on agentic engineering and how AI is reshaping software.
Dated **notes** synthesize each source, evergreen **topics** compound them, and
**build logs** put the ideas into practice. Built with [Astro](https://astro.build) +
[Starlight](https://starlight.astro.build).

This repo is the **publishable home** for the intelligence work — captures,
topics, and the synthesis pipeline live here, decoupled from any private source
notes. Pages are authored for a public audience; nothing is exported directly
from a personal vault.

## Structure

```
src/
├── content/docs/
│   ├── index.mdx          # landing page (splash hero)
│   └── topics/            # published topic syntheses
├── styles/theme.css       # Stripe-flavored Starlight theme
└── content.config.ts
astro.config.mjs           # site config, sidebar, theme
.github/workflows/deploy.yml  # GitHub Pages CI
```

Starlight serves every `.md` / `.mdx` file under `src/content/docs/` as a route.
New topics drop into `src/content/docs/topics/` and appear in the sidebar
automatically.

## Commands

| Command           | Action                                       |
| :---------------- | :------------------------------------------- |
| `npm install`     | Install dependencies                         |
| `npm run dev`     | Local dev server at `localhost:4321/working-intel`|
| `npm run build`   | Build production site to `./dist/`           |
| `npm run preview` | Preview the production build locally         |

## Deployment

Pushes to `main` build and deploy to GitHub Pages via
`.github/workflows/deploy.yml`. Enable it under **Settings → Pages → Build and
deployment → Source: GitHub Actions**. The site serves from
`https://briggsd.github.io/working-intel/`.

To use a custom domain, set it in the Pages settings and update `site` / `base`
in `astro.config.mjs`.
