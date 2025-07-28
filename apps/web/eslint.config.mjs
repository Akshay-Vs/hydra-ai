import eslintNext from '@hydra/eslint-config/next';
import pluginNext from '@next/eslint-plugin-next';

// This brings in plugin:@next/next/recommended as flat config
const nextRecommendedConfig = pluginNext.configs.recommended;

const eslintConfig = [
	...eslintNext,

	{
		// Applies Next.js recommended rules globally
		plugins: {
			'@next/next': pluginNext,
		},
		rules: {
			...nextRecommendedConfig.rules,
		},
	},
];

export default eslintConfig;
