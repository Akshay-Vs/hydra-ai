// base.eslint.mjs
import tsParser from '@typescript-eslint/parser';
import eslintPluginReact from 'eslint-plugin-react';
import eslintPluginReactHooks from 'eslint-plugin-react-hooks';
import eslintPluginTypescript from '@typescript-eslint/eslint-plugin';
import eslintPluginImport from 'eslint-plugin-import';
import eslintPluginUnusedImports from 'eslint-plugin-unused-imports';
import eslintPluginCspell from '@cspell/eslint-plugin';
import eslintPluginPrettier from 'eslint-plugin-prettier';

export default [
	{
		files: ['**/*.{js,jsx,ts,tsx}'],
		ignores: ['dist/**'],
		languageOptions: {
			parser: tsParser,
			parserOptions: {
				ecmaFeatures: { jsx: true },
				ecmaVersion: 'latest',
				sourceType: 'module',
				project: './tsconfig.json',
			},
		},
		plugins: {
			react: eslintPluginReact,
			'react-hooks': eslintPluginReactHooks,
			'@typescript-eslint': eslintPluginTypescript,
			import: eslintPluginImport,
			'unused-imports': eslintPluginUnusedImports,
			'@cspell': eslintPluginCspell,
			prettier: eslintPluginPrettier,
		},
		settings: {
			react: { version: 'detect' },
			'import/resolver': {
				typescript: {
					alwaysTryTypes: true,
					project: './tsconfig.json',
				},
				node: {
					extensions: ['.js', '.jsx', '.ts', '.tsx'],
				},
			},
		},
		rules: {
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
			'unused-imports/no-unused-imports': 'error',
			'unused-imports/no-unused-vars': [
				'warn',
				{ vars: 'all', varsIgnorePattern: '^_', args: 'after-used', argsIgnorePattern: '^_' },
			],
			'import/order': [
				'error',
				{
					groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
					pathGroups: [
						{ pattern: 'react', group: 'external', position: 'before' },
						{ pattern: '@/**', group: 'internal' },
						{ pattern: '~/**', group: 'internal' },
					],
					pathGroupsExcludedImportTypes: ['react'],
					alphabetize: { order: 'asc', caseInsensitive: true },
				},
			],
			'import/no-unresolved': 'error',
			'import/no-duplicates': 'error',
			'import/newline-after-import': 'error',
			'@cspell/spellchecker': [
				'warn',
				{ cspell: { words: ['andromeda', 'meda', 'meda-ui', 'meda-ui-native', 'meda-ui-web', 'meda-ai'], ignoreWords: [] } },
			],
			'@typescript-eslint/no-unused-vars': 'off',
			'@typescript-eslint/explicit-function-return-type': 'off',
			'@typescript-eslint/explicit-module-boundary-types': 'off',
			'@typescript-eslint/no-explicit-any': 'warn',
			'@typescript-eslint/no-non-null-assertion': 'warn',
			'@typescript-eslint/prefer-nullish-coalescing': 'error',
			'@typescript-eslint/prefer-optional-chain': 'error',
			'@typescript-eslint/consistent-type-imports': [
				'error',
				{ prefer: 'type-imports', disallowTypeAnnotations: false },
			],
			'react/react-in-jsx-scope': 'off',
			'react/prop-types': 'off',
			'react/display-name': 'off',
			'react-hooks/rules-of-hooks': 'error',
			'react-hooks/exhaustive-deps': 'warn',
			'react/jsx-curly-brace-presence': ['error', { props: 'never', children: 'never' }],
			'react/jsx-boolean-value': ['error', 'never'],
			'react/jsx-fragments': ['error', 'syntax'],
			'react/self-closing-comp': ['error', { component: true, html: true }],
			'no-console': 'warn',
			'no-debugger': 'error',
			'no-alert': 'warn',
			'no-var': 'error',
			'prefer-const': 'error',
			'prefer-arrow-callback': 'error',
			'arrow-spacing': 'error',
			'object-shorthand': 'error',
			'prefer-template': 'error',
			'template-curly-spacing': 'error',
			'no-multiple-empty-lines': ['error', { max: 2, maxEOF: 1 }],
			'eol-last': 'error',
			'comma-dangle': [
				'error',
				{
					arrays: 'always-multiline',
					objects: 'always-multiline',
					imports: 'always-multiline',
					exports: 'always-multiline',
					functions: 'never',
				},
			],
			quotes: ['error', 'single', { avoidEscape: true, allowTemplateLiterals: true }],
			semi: ['error', 'always'],
			'max-len': [
				'error',
				{ code: 100, tabWidth: 2, ignoreUrls: true, ignoreStrings: true, ignoreTemplateLiterals: true },
			],
		},
	},
	{
		files: ['*.test.{js,jsx,ts,tsx}', '**/__tests__/**/*'],
		rules: {
			'no-console': 'off',
			'@typescript-eslint/no-explicit-any': 'off',
		},
	},
	{
		files: ['*.js', '*.jsx'],
		rules: {
			'@typescript-eslint/explicit-function-return-type': 'off',
			'@typescript-eslint/no-var-requires': 'off',
		},
	},
];
