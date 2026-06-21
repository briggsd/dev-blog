// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// Deployed to GitHub Pages project site by default:
//   https://briggsd.github.io/dev-blog/
// Swap `site`/`base` (or drop `base`) when a custom domain is wired up.
export default defineConfig({
	site: 'https://briggsd.github.io',
	base: '/dev-blog',
	integrations: [
		starlight({
			title: 'Field Notes',
			// TODO(confirm): working title + tagline — rename freely.
			tagline: 'Notes on agentic engineering, AI labor markets, and how software gets built now.',
			description:
				'A running synthesis of how AI is reshaping software, work, and the way products get built.',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/briggsd/dev-blog' },
			],
			customCss: ['@fontsource-variable/inter', './src/styles/theme.css'],
			lastUpdated: true,
			sidebar: [
				{
					label: 'Topics',
					items: [{ autogenerate: { directory: 'topics' } }],
				},
			],
		}),
	],
});
