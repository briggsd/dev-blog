// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightBlog from 'starlight-blog';

// Deployed to GitHub Pages project site by default:
//   https://briggsd.github.io/dev-blog/
// Swap `site`/`base` (or drop `base`) when a custom domain is wired up.
export default defineConfig({
	site: 'https://briggsd.github.io',
	base: '/dev-blog',
	integrations: [
		starlight({
			title: 'Working Intelligence',
			tagline: 'Field notes on agentic engineering, AI labor markets, and how software gets built now.',
			description:
				'A running synthesis of how AI is reshaping software, work, and the way products get built.',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/briggsd/dev-blog' },
			],
			customCss: [
				'@fontsource-variable/inter',
				'@fontsource-variable/jetbrains-mono',
				'./src/styles/theme.css',
			],
			lastUpdated: true,
			// Terminal theme overrides:
			//  - ThemeSelect: empty (dark-only, no toggle).
			//  - Header: adds a persistent top nav (topics/notes/github) on every page.
			components: {
				ThemeSelect: './src/components/ThemeSelect.astro',
				Header: './src/components/Header.astro',
			},
			plugins: [
				starlightBlog({
					// The "stream": dated, single-source posts at /dev-blog/notes/.
					// Topics (the evergreen "garden") stay in the sidebar below.
					title: 'Notes',
					prefix: 'notes',
					// We render our own header nav (see src/components/Header.astro),
					// so the plugin should not inject its own link or override components.
					navigation: 'none',
					authors: {
						wi: { name: 'Working Intelligence' },
					},
				}),
			],
			sidebar: [
				{
					label: 'Topics',
					items: [{ autogenerate: { directory: 'topics' } }],
				},
			],
		}),
	],
});
