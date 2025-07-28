// library.eslint.mjs
import baseConfig from './base.eslint.mjs';
import eslintPluginJsdoc from 'eslint-plugin-jsdoc';

export default [
	...baseConfig.map(config => ({
		...config,
		ignores: [
			...(config.ignores ?? []),
			'dist/**',
			'lib/**',
			'build/**',
			'coverage/**',
			'*.d.ts',
			'*.min.js',
		],
		languageOptions: {
			...config.languageOptions,
			globals: {
				...config.languageOptions?.globals,
				process: 'readonly',
				Buffer: 'readonly',
				__dirname: 'readonly',
				__filename: 'readonly',
				module: 'readonly',
				require: 'readonly',
				exports: 'readonly',
				global: 'readonly',
			},
		},
		plugins: {
			...config.plugins,
			jsdoc: eslintPluginJsdoc,
		},
		rules: {
			...config.rules,
			'@typescript-eslint/explicit-function-return-type': 'error',
			'@typescript-eslint/explicit-module-boundary-types': 'error',
			'@typescript-eslint/no-explicit-any': 'error',
			'@typescript-eslint/no-non-null-assertion': 'error',
			'@typescript-eslint/prefer-readonly': 'error',
			'@typescript-eslint/prefer-readonly-parameter-types': 'off',
			'@typescript-eslint/no-unsafe-assignment': 'error',
			'@typescript-eslint/no-unsafe-call': 'error',
			'@typescript-eslint/no-unsafe-member-access': 'error',
			'@typescript-eslint/no-unsafe-return': 'error',

			// JSDoc rules
			'jsdoc/check-alignment': 'error',
			'jsdoc/check-indentation': 'error',
			'jsdoc/check-param-names': 'error',
			'jsdoc/check-syntax': 'error',
			'jsdoc/check-tag-names': 'error',
			'jsdoc/check-types': 'error',
			'jsdoc/implements-on-classes': 'error',
			'jsdoc/match-description': 'error',
			'jsdoc/newline-after-description': 'error',
			'jsdoc/no-undefined-types': 'error',
			'jsdoc/require-description': 'error',
			'jsdoc/require-description-complete-sentence': 'error',
			'jsdoc/require-example': 'off',
			'jsdoc/require-hyphen-before-param-description': 'error',
			'jsdoc/require-param': 'error',
			'jsdoc/require-param-description': 'error',
			'jsdoc/require-param-name': 'error',
			'jsdoc/require-param-type': 'off',
			'jsdoc/require-returns': 'error',
			'jsdoc/require-returns-check': 'error',
			'jsdoc/require-returns-description': 'error',
			'jsdoc/require-returns-type': 'off',
			'jsdoc/valid-types': 'error',

			// Import/export rules
			'import/no-default-export': 'error',
			'import/prefer-default-export': 'off',
			'import/no-extraneous-dependencies': [
				'error',
				{
					devDependencies: [
						'**/*.test.{js,jsx,ts,tsx}',
						'**/*.spec.{js,jsx,ts,tsx}',
						'**/__tests__/**/*',
						'**/__mocks__/**/*',
						'**/test/**/*',
						'**/tests/**/*',
						'**/*.config.{js,ts}',
						'**/build/**/*',
						'**/scripts/**/*',
						'**/rollup.config.{js,ts}',
						'**/webpack.config.{js,ts}',
						'**/vite.config.{js,ts}',
					],
					optionalDependencies: false,
					peerDependencies: true,
				},
			],

			// Spell checker
			'@cspell/spellchecker': [
				'warn',
				{
					cspell: {
						words: [
							'tsup', 'rollup', 'bundler', 'commonjs', 'esm', 'umd', 'cjs', 'mjs', 'dts',
							'typings', 'pkg', 'deps', 'peerDeps', 'devDeps', 'semver', 'changelog', 'readme',
						],
						ignoreWords: [],
					},
				},
			],

			// Stricter code quality rules
			'no-console': 'error',
			'no-debugger': 'error',
			complexity: ['error', 10],
			'max-depth': ['error', 4],
			'max-lines': ['error', 300],
			'max-lines-per-function': ['error', 50],
			'max-params': ['error', 5],
			'no-magic-numbers': [
				'error',
				{
					ignore: [-1, 0, 1, 2],
					ignoreArrayIndexes: true,
					ignoreDefaultValues: true,
				},
			],

			'no-restricted-globals': [
				'error',
				{
					name: 'process',
					message: 'Use feature detection instead of process checks.',
				},
			],
		},
	})),

	// Configuration files
	{
		files: [
			'*.config.{js,ts,mjs}',
			'rollup.config.{js,ts}',
			'webpack.config.{js,ts}',
			'vite.config.{js,ts}',
			'tsup.config.{js,ts}',
			'build.{js,ts}',
			'scripts/**/*.{js,ts}',
		],
		rules: {
			'@typescript-eslint/no-var-requires': 'off',
			'import/no-default-export': 'off',
			'no-console': 'off',
			'jsdoc/require-description': 'off',
			'jsdoc/require-param': 'off',
			'jsdoc/require-returns': 'off',
		},
	},

	// Example/demo files
	{
		files: [
			'examples/**/*.{js,jsx,ts,tsx}',
			'demo/**/*.{js,jsx,ts,tsx}',
			'docs/**/*.{js,jsx,ts,tsx}',
		],
		rules: {
			'no-console': 'off',
			'jsdoc/require-description': 'off',
			'jsdoc/require-param': 'off',
			'jsdoc/require-returns': 'off',
			'import/no-extraneous-dependencies': 'off',
		},
	},

	// Type definition files
	{
		files: ['*.d.ts', '**/*.d.ts'],
		rules: {
			'@typescript-eslint/no-explicit-any': 'off',
			'@typescript-eslint/no-unused-vars': 'off',
			'import/no-default-export': 'off',
		},
	},
];
