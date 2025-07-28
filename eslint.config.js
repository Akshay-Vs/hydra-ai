import prettierPlugin from 'eslint-plugin-prettier';

export default [
	{
		files: ['**/*.{js,jsx,ts,tsx}'],
		ignores: ['dist/**', 'node_modules/**', 'build/**'],
		languageOptions: {
			ecmaVersion: 'latest',
			sourceType: 'module',
		},
		plugins: {
			prettier: prettierPlugin,
		},
		rules: {
			// Prettier formatting
			'prettier/prettier': [
				'error',
				{
					singleQuote: true,
					trailingComma: 'es5',
					tabWidth: 2,
					semi: true,
					printWidth: 100,
					bracketSpacing: true,
					arrowParens: 'avoid',
				},
			],

			// Basic rules
			'no-console': 'warn',
			'no-unused-vars': 'warn',
			'prefer-const': 'error',
			'no-var': 'error',
		},
	},
];
