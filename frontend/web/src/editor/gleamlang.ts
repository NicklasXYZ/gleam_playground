import * as monaco from 'monaco-editor';
import { editor } from 'monaco-editor';

export const conf: monaco.languages.LanguageConfiguration = {
	comments: {
		lineComment: '//'
	},
	brackets: [
		['{', '}'],
		['[', ']'],
		['(', ')']
	],
	surroundingPairs: [
		{ open: '{', close: '}' },
		{ open: '[', close: ']' },
		{ open: '(', close: ')' },
		{ open: "'", close: "'" },
		{ open: '"', close: '"' }
	],
	autoClosingPairs: [
		{ open: "'", close: "'"},
		{ open: '"', close: '"'},
		// { open: '`', close: '`', notIn: ['string', 'comment'] },
		{ open: '`', close: '`'},
		{ open: '(', close: ')' },
		{ open: '{', close: '}' },
		{ open: '[', close: ']' },
	],
};

interface MonarchLanguageConfiguration extends monaco.languages.IMonarchLanguage {
    keywords: string[];
    operators: string[];
}

export const monarchLanguage: MonarchLanguageConfiguration = {
    // Set defaultToken to invalid to see what you do not tokenize yet
    // defaultToken: 'invalid',
  
    keywords: [
        'case', 'if', 'external', 'fn', 'import', 'let', 'assert', 'try',
        'pub', 'type', 'opaque', 'const', 'todo', 
        'True', 'False',
    ],
      
    operators: [
        '=',
        '>.', '<.', 
        '==.', '<=.', '>=.', '!=.',
        '>', '<', 
        '==', '<=', '>=', '!=',
        '&&', '||',
        '|>', '|',
        '+.', '-.', '*.', '/.',  '%.',
        '+', '-', '*', '/',  '%',
        '->',
        '..',
    ],
    
    // The main tokenizer for Gleam
    tokenizer: {
        root: [
            // identifiers and keywords
            [/[a-z_$][\w$]*/, { cases: { '@keywords': { token: 'keyword' }}}],
            [/[A-Z][\w$]*/, 'type.identifier' ],  // to show class names nicely
    
            // whitespace
            { include: '@whitespace' },
    
            // delimiters and operators
            // [/[{}()[]]/, '@brackets'],
    
            // numbers
            [/0[xX][0-9a-fA-F]+/, 'number.hex'],
            [/\b0[bB](?:_?[01]+)+/, 'number.binary'],
            [/\d*\.\d+([eE][-+]?\d+)?/, 'number.float'],
            [/\d+/, 'number'],
    
            // strings
            [/"([^"\\]|\\.)*$/, 'string.invalid' ],  // non-teminated string
            [/"/,  { token: 'string.quote', bracket: '@open', next: '@string' } ],  
      ],

        comment: [
            [/[^/*]+/, 'comment' ],
            [/\/\*/,    'comment', '@push' ],    // nested comment
            [/"\\*\/"/, 'comment', '@pop'  ],
            [/[/*]/,   'comment' ]
        ],
  
        string: [
            [/[^\\"]+/,  'string'],
            [/"/,        { token: 'string.quote', bracket: '@close', next: '@pop' } ]
        ],
  
        whitespace: [
            [/\/\/.*$/,    'comment'],
        ],
    },
};

export const themeData: editor.IStandaloneThemeData = {
    base: 'vs-dark',
    inherit: true,
    rules: [       
        { token: 'keyword', background: '#ffaff3', foreground: '#ffaff3'},
        { token: 'type.identifier', background: '#D9ADFF', foreground: '#D9ADFF'},
        { token: 'comment', background: '#666666', foreground: '#666666'},
    ],
    colors: {
        // Editor line number colour
        'editorLineNumber.foreground': '#666666',
        // Editor background color
        'editor.background': '#1F1F1F',
    }
}
  