// Rules are modified from Portsoc's Eslint Config (https://github.com/portsoc/eslint-config-portsoc)
const rules = {
    'max-len': ['error', {
        ignoreComments: true,
        ignoreTrailingComments: true,
        ignoreUrls: true,
        ignoreStrings: true,
        ignoreTemplateLiterals: true,
        ignoreRegExpLiterals: true,
    }],
    'space-before-function-paren': ['error', {
        anonymous: 'always',
        named: 'never',
        asyncArrow: 'always',
    }],
    'lines-between-class-members': ['error', 'always', {
        exceptAfterSingleLine: true,
    }],
    'no-var': ['error'],
    'require-await': ['error'],
    'no-unused-vars': ['error', { vars: 'all', args: 'after-used' }],
    'no-restricted-syntax': ['error',
        {
            selector: 'SequenceExpression',
            message: 'sequence expressions (using comma operator) are not allowed',
        },
        {
            selector: 'IfStatement[alternate=null] > EmptyStatement.consequent',
            message: 'unexpected empty statement',
        },
        {
            selector: 'IfStatement > EmptyStatement.alternate',
            message: 'unexpected empty statement',
        },
        {
            selector: 'ForInStatement',
            message: 'for…in statements are not allowed',
        },
    ],
    'indent': ['error', 4, {
        SwitchCase: 1,
    }],
    'no-multiple-empty-lines': ['error', {
        max: 2,
        maxEOF: 1,
    }],
    'quotes': ['error', 'single', {
        avoidEscape: true,
        allowTemplateLiterals: true,
    }],
    'quote-props': ['error', 'consistent'],
    'semi': ['error', 'always'],
    'prefer-const': 'error',
    'comma-dangle': ['error', {
        arrays: 'always-multiline',
        objects: 'always-multiline',
        imports: 'never',
        exports: 'never',
        functions: 'never',
    }],
    'no-prototype-builtins': 'off',
};

const tsRules = {...rules,
    'no-unused-vars': 'off',
    '@typescript-eslint/no-unused-vars': ['error'],
    'import/no-named-as-default-member': 'off',
};

module.exports = {
    root: true,
    extends: [ 'eslint:recommended' ],
    env: {
        browser: true,
        node: true,
        es2021: true,
        mocha: true,
    },
    rules,
    parser: '@babel/eslint-parser', // Fixes eslint error when using static class propertes
    parserOptions: {
        sourceType: 'module',
        requireConfigFile: false,
        babelOptions: {
            plugins: [
                '@babel/plugin-proposal-class-properties',
                '@babel/plugin-proposal-private-methods',
            ],
        },
    },
    overrides: [
        {
            files: ['*.ts', '*.tsx'],
            excludedFiles: ['*.js', '*.jsx'],
            parser: '@typescript-eslint/parser',
            parserOptions: {
                sourceType: 'module',
            },
            plugins: [
                '@typescript-eslint',
                'import',
            ],
            extends: [
                'eslint:recommended',
                'plugin:@typescript-eslint/recommended',
                'plugin:import/errors',
                'plugin:import/warnings',
                'plugin:import/typescript',
            ],
            rules: tsRules,
            settings: {
                'import/parsers': {
                    '@typescript-eslint/parser': ['.ts', '.tsx'],
                },
                'import/resolver': {
                    typescript: {},
                },
            },
        },
    ],
};
