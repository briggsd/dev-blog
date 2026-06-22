// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightBlog from 'starlight-blog';

// Deployed to GitHub Pages project site by default:
//   https://briggsd.github.io/working-intel/
// Swap `site`/`base` (or drop `base`) when a custom domain is wired up.
export default defineConfig({
	site: 'https://briggsd.github.io',
	base: '/working-intel',
	integrations: [
		starlight({
			title: 'working_intel',
			tagline: 'A working knowledge base on agentic engineering and how AI is reshaping software.',
			description:
				'Notes that synthesize each source, evergreen topics that compound them, and build logs that put the ideas into practice. A running read on agentic engineering and how software gets built now.',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/briggsd/working-intel' },
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
					// The "stream": dated, single-source posts at /working-intel/notes/.
					// Topics (the evergreen "garden") stay in the sidebar below.
					title: 'Notes',
					prefix: 'notes',
					// We render our own header nav (see src/components/Header.astro),
					// so the plugin should not inject its own link or override components.
					navigation: 'none',
					authors: {
						wi: { name: 'working_intel' },
					},
				}),
			],
			sidebar: [
				{
					label: 'Topics',
					items: [{ autogenerate: { directory: 'topics' } }],
				},
				{
					label: 'Build',
					items: [{ autogenerate: { directory: 'build' } }],
				},
			],
		}),
	],
});
