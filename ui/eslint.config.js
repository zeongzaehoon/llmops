import js from '@eslint/js'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import globals from 'globals'

export default [
  { ignores: ['dist/**', 'dist-ssr/**', 'coverage/**'] },
  js.configs.recommended,
  react.configs.flat.recommended,
  react.configs.flat['jsx-runtime'],
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: { ...globals.browser, ...globals.es2021 },
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    plugins: { 'react-hooks': reactHooks },
    settings: { react: { version: 'detect' } },
    rules: {
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      'react/prop-types': 'off',
      // Preserve ESLint 8 behavior: v9 changed this rule's default
      // `checkLoops` to 'allExceptWhileTrue', which would stop flagging
      // the existing `while (true)` streaming loops and shrink the known
      // error set from 12 to 10. Pin to v8 behavior for rule equivalence.
      'no-constant-condition': ['error', { checkLoops: true }],
    },
  },
]
