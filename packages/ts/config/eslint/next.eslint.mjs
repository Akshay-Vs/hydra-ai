// nextjs.eslint.mjs
import baseConfig from './base.eslint.mjs';
import eslintPluginNext from '@next/eslint-plugin-next';

export default [
	...baseConfig.map(config => ({
		...config,
		languageOptions: {
			...config.languageOptions,
			globals: {
				...config.languageOptions?.globals,
				React: 'readonly',
				JSX: 'readonly',
			},
		},
		plugins: {
			...config.plugins,
			'@next/next': eslintPluginNext,
		},
		settings: {
			...config.settings,
			'import/resolver': {
				...(config.settings?.['import/resolver'] ?? {}),
				alias: {
					map: [
						['@', './src'],
						['~', './'],
					],
					extensions: ['.js', '.jsx', '.ts', '.tsx'],
				},
			},
		},
		rules: {
			...config.rules,

			// Next.js specific rules
			'@next/next/no-html-link-for-pages': 'error',
			'@next/next/no-img-element': 'error',
			'@next/next/no-unwanted-polyfillio': 'error',
			'@next/next/no-page-custom-font': 'error',
			'@next/next/no-sync-scripts': 'error',
			'@next/next/no-document-import-in-page': 'error',
			'@next/next/no-head-import-in-document': 'error',
			'@next/next/no-script-component-in-head': 'error',
			'@next/next/no-styled-jsx-in-document': 'error',
			'@next/next/no-css-tags': 'error',
			'@next/next/no-title-in-document-head': 'error',
			'@next/next/google-font-display': 'warn',
			'@next/next/google-font-preconnect': 'warn',
			'@next/next/next-script-for-ga': 'warn',
			'@next/next/no-before-interactive-script-outside-document': 'warn',
			'@next/next/no-head-element': 'error',
			'@next/next/no-duplicate-head': 'error',
			'@next/next/inline-script-id': 'error',
			'@next/next/no-assign-module-variable': 'error',

			'import/order': [
				'error',
				{
					groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
					pathGroups: [
						{ pattern: 'react', group: 'external', position: 'before' },
						{ pattern: 'next', group: 'external', position: 'before' },
						{ pattern: 'next/**', group: 'external', position: 'before' },
						{ pattern: '@/**', group: 'internal' },
						{ pattern: '~/**', group: 'internal' },
					],
					pathGroupsExcludedImportTypes: ['react', 'next'],
					alphabetize: {
						order: 'asc',
						caseInsensitive: true,
					},
				},
			],

			'@cspell/spellchecker': [
				'warn',
				{
					cspell: {
						words: [
							'nextjs',
							'vercel',
							'middleware',
							'getServerSideProps',
							'getStaticProps',
							'getStaticPaths',
							'getInitialProps',
							'prefetch',
							'revalidate',
							'unstable',
							'preload',
							'webp',
							'avif',
						],
						ignoreWords: [],
					},
				},
			],

			'no-console': 'off',
		},
	})),

	// Next.js pages
	{
		files: ['pages/**/*.{js,jsx,ts,tsx}', 'src/pages/**/*.{js,jsx,ts,tsx}'],
		rules: {
			'import/no-default-export': 'off',
			'import/prefer-default-export': 'error',
		},
	},
	// API routes
	{
		files: ['pages/api/**/*.{js,ts}', 'src/pages/api/**/*.{js,ts}'],
		rules: {
			'import/no-default-export': 'off',
			'import/prefer-default-export': 'error',
			'no-console': 'off',
		},
	},
	// App directory (app router)
	{
		files: ['app/**/*.{js,jsx,ts,tsx}', 'src/app/**/*.{js,jsx,ts,tsx}'],
		rules: {
			'import/no-default-export': 'off',
		},
	},
	// Middleware
	{
		files: ['middleware.{js,ts}', 'src/middleware.{js,ts}'],
		rules: {
			'import/no-default-export': 'off',
			'import/prefer-default-export': 'error',
		},
	},
	// Next + Tailwind configs
	{
		files: ['next.config.{js,mjs}', 'tailwind.config.{js,ts}'],
		rules: {
			'@typescript-eslint/no-var-requires': 'off',
			'import/no-default-export': 'off',
		},
	},
];
