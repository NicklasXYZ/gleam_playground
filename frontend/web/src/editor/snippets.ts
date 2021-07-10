import * as monaco from 'monaco-editor';

/* eslint-disable no-template-curly-in-string */

const Rule = monaco.languages.CompletionItemInsertTextRule;
/**
 * List of snippets for editor
 */
const snippets = [
    {
        label: 'pub fn',
        insertText: [
            'pub fn ${1:functionName}($2: ${3:param}) -> $4 {',
            '  $0',
            '}'
        ].join('\n'),
        documentation: 'Insert a function'
    },
    {
        label: 'fn',
        insertText: [
            'fn ${1:functionName}($2: ${3:param}) -> $4 {',
            '  $0',
            '}'
        ].join('\n'),
        documentation: 'Insert a private function'
    },
    {
        label: 'pub external fn',
        insertText: [
            'pub external fn ${1:functionName}($2: ${3:param}) -> $4 = ',
            '  "$5"  "$0"',
        ].join('\n'),
        documentation: 'Insert an external function'
    },
    {
        label: 'external fn',
        insertText: [
            'external fn ${1:functionName}($2: ${3:param}) -> $4 = ',
            '  "$5"  "$0"',
        ].join('\n'),
        documentation: 'Insert an external and private function'
    },
    {
        label: 'case',
        insertText: [
            'case $1 {',
            '  $2 -> $3',
            '  $0',
            '}'
        ].join('\n'),
        documentation: 'Insert a case clause'
    },
    {
        label: 'let',
        insertText: [
            'let ${1:param}: $2 = $0',
        ].join('\n'),
        documentation: 'Insert a let statement'
    },
    {
        label: 'pub const',
        insertText: [
            'pub const ${1:param}: $2 = $0',
        ].join('\n'),
        documentation: 'Insert a constant'
    },
    {
        label: 'const',
        insertText: [
            'const ${1:param}: $2 = $0',
        ].join('\n'),
        documentation: 'Insert a private constant'
    },
    {
        label: 'pub type custom',
        insertText: [
            'pub type $1 {',
            '  $0',
            '}',
        ].join('\n'),
        documentation: 'Insert a custom type'
    },
    {
        label: 'type custom',
        insertText: [
            'type $1 {',
            '  $0',
            '}',
        ].join('\n'),
        documentation: 'Insert a custom and private type'
    },
    {
        label: 'pub type alias',
        insertText: [
            'pub type $1 = $0',
        ].join('\n'),
        documentation: 'Insert a type alias'
    },
    {
        label: 'type custom',
        insertText: [
            'pub type $1 = $0',
        ].join('\n'),
        documentation: 'Insert a private type alias'
    },
    {
        label: 'pub external type',
        insertText: [
            'pub external type $0',
        ].join('\n'),
        documentation: 'Insert an external type'
    },   
    {
        label: 'external type',
        insertText: [
            'pub external type $0',
        ].join('\n'),
        documentation: 'Insert an external and private type'
    },
].map(s => ({
    kind: monaco.languages.CompletionItemKind.Snippet,
    insertTextRules: Rule.InsertAsSnippet,
    ...s,
}));

export default snippets as monaco.languages.CompletionItem[];
