import React from 'react';
import MonacoEditor from 'react-monaco-editor';
import { editor } from 'monaco-editor';
import * as monaco from 'monaco-editor';
import { Connect, formatFileDispatcher, newFileChangeAction, runFileDispatcher } from '../store';
import { Analyzer } from '../services/analyzer';
import { monarchLanguage, conf, themeData } from './gleamlang'
import { LANGUAGE_GLEAM, stateToOptions } from './props';

const ANALYZE_DEBOUNCE_TIME = 500;

interface CodeEditorState {
    code?: string
    loading?:boolean
}

// Register a new language
monaco.languages.register({ id: 'gleam' });
monaco.languages.setLanguageConfiguration('gleam', conf);
monaco.languages.setMonarchTokensProvider('gleam', monarchLanguage);
monaco.editor.defineTheme('vs-dark', themeData);

@Connect(s => ({
    code: s.editor.code,
    darkMode: s.settings.darkMode,
    loading: s.status?.loading,
    options: s.monaco,
}))
export default class CodeEditor extends React.Component<any, CodeEditorState> {
    analyzer?: Analyzer;
    _previousTimeout: any;
    editorInstance?: editor.IStandaloneCodeEditor;

    editorDidMount(editorInstance: editor.IStandaloneCodeEditor, _: monaco.editor.IEditorConstructionOptions) {
        this.editorInstance = editorInstance;
        if (Analyzer.supported()) {
            this.analyzer = new Analyzer();
        } else {
            console.info('Analyzer requires WebAssembly support');
        }

        const actions = [
            {
                id: 'run-code',
                label: 'Build And Run Code',
                contextMenuGroupId: 'navigation',
                keybindings: [
                    monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter
                ],
                run: (ed, ...args) => {
                    this.props.dispatch(runFileDispatcher);
                }
            },
            {
                id: 'format-code',
                label: 'Format Code',
                contextMenuGroupId: 'navigation',
                keybindings: [
                    monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KEY_F
                ],
                run: (ed, ...args) => {
                    this.props.dispatch(formatFileDispatcher);
                }
            }
        ];

        // Register custom actions
        actions.forEach(action => editorInstance.addAction(action))
        editorInstance.focus();
    }

    componentWillUnmount() {
        this.analyzer?.dispose();
    }

    onChange(newValue: string, e: editor.IModelContentChangedEvent) {
        this.props.dispatch(newFileChangeAction(newValue));

        if (this.analyzer) {
            this.doAnalyze(newValue);
        }
    }

    private doAnalyze(code: string) {
        if (this._previousTimeout) {
            clearTimeout(this._previousTimeout);
        }

        this._previousTimeout = setTimeout(() => {
            this._previousTimeout = null;
            this.analyzer?.analyzeCode(code).then(result => {
                editor.setModelMarkers(
                    this.editorInstance?.getModel() as editor.ITextModel,
                    this.editorInstance?.getId() as string,
                    result.markers
                );
            }).catch(err => console.error('failed to perform code analysis: %s', err));
        }, ANALYZE_DEBOUNCE_TIME);
    }

    render() {
        const options = stateToOptions(this.props.options);
        return <MonacoEditor
            language={LANGUAGE_GLEAM}
            // theme={this.props.darkMode ? 'vs-dark' : 'vs-light'}
            theme="vs-dark"
            value={this.props.code}
            options={options}
            onChange={(newVal, e) => this.onChange(newVal, e)}
            editorDidMount={(e, m: any) => this.editorDidMount(e, m)}
        />;
    }
}
