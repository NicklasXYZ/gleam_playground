import {saveAs} from 'file-saver';
import {push} from 'connected-react-router';
import {
    Action,
    MonacoParamsChanges, newBuildParamsChangeAction,
    newBuildResultAction,
    newErrorAction,
    newImportFileAction,
    newLoadingAction, newMonacoParamsChangeAction,
    newToggleThemeAction
} from './actions';
import {State} from "./state";
// import client, {EvalEventKind, instantiateStreaming} from '../services/api';
import client from '../services/api';
import config, {RuntimeType} from '../services/config';
import {DEMO_CODE} from '../editor/props';

export type StateProvider = () => State
export type DispatchFn = (a: Action|any) => any
export type Dispatcher = (dispatch: DispatchFn, getState: StateProvider) => void

/////////////////////////////
//      Dispatchers        //
/////////////////////////////

export function newImportFileDispatcher(f: File): Dispatcher {
    return (dispatch: DispatchFn, _: StateProvider) => {
        const reader = new FileReader();
        reader.onload = e => {
            const data = e.target?.result as string;
            dispatch(newImportFileAction(f.name, data));
        };

        reader.onerror = e => {
            // TODO: replace with a nice modal
            alert(`Failed to import a file: ${e}`)
        };

        reader.readAsText(f, 'UTF-8');
    };
}

export function newCodeImportDispatcher(name: string, contents: string): Dispatcher {
    return (dispatch: DispatchFn, _: StateProvider) => {
        dispatch(newImportFileAction(`${encodeURIComponent(name)}.gleam`, contents));
    };
}

export function newMonacoParamsChangeDispatcher(changes: MonacoParamsChanges): Dispatcher {
    return (dispatch: DispatchFn, _: StateProvider) => {
        const current = config.monacoSettings;
        config.monacoSettings = Object.assign(current, changes);
        dispatch(newMonacoParamsChangeAction(changes));
    };
}

export function newBuildParamsChangeDispatcher(runtime: RuntimeType, autoFormat: boolean): Dispatcher {
    return (dispatch: DispatchFn, _: StateProvider) => {
        config.runtimeType = runtime;
        config.autoFormat = autoFormat;
        dispatch(newBuildParamsChangeAction(runtime, autoFormat));
    };
}

export function newSnippetLoadDispatcher(snippetID: string): Dispatcher {
    return async(dispatch: DispatchFn, _: StateProvider) => {
        if (!snippetID) {
            dispatch(newImportFileAction('gleam_project.gleam', DEMO_CODE));
            return;
        }

        dispatch(newLoadingAction());
        try {
            console.log('loading snippet %s', snippetID);
            const resp = await client.getSnippet(snippetID);
            const { fileName, code } = resp;
            dispatch(newImportFileAction(fileName, code));
        } catch(err) {
            dispatch(newErrorAction(err.message));
        }
    }
}

export const shareSnippetDispatcher: Dispatcher =
    async (dispatch: DispatchFn, getState: StateProvider) => {
        dispatch(newLoadingAction());
        try {
            const {code} = getState().editor;
            const res = await client.shareSnippet(code);
            dispatch(push(`/snippet/${res.snippetID}`));
        } catch (err) {
            dispatch(newErrorAction(err.message));
        }
    };

export const saveFileDispatcher: Dispatcher =
    (_: DispatchFn, getState: StateProvider) => {
        try {
            const {fileName, code } = getState().editor;
            const blob = new Blob([code], {type: 'text/plain;charset=utf-8'});
            saveAs(blob, fileName);
        } catch (err) {
            // TODO: replace with a nice modal
            alert(`Failed to save a file: ${err}`)
        }
    };

export const runFileDispatcher: Dispatcher =
    async (dispatch: DispatchFn, getState: StateProvider) => {
        dispatch(newLoadingAction());
        try {
            const { settings, editor } = getState();
            switch (settings.runtime) {
                case RuntimeType.GleamPlayground:
                    const res = await client.evaluateCode(editor.code, settings.autoFormat);
                    dispatch(newBuildResultAction(res));
                    break;
                default:
                    dispatch(newErrorAction(`AppError: Unknown Gleam runtime type "${settings.runtime}"`));
            }
        } catch (err) {
            dispatch(newErrorAction(err.message));
        }
    };

export const formatFileDispatcher: Dispatcher =
    async (dispatch: DispatchFn, getState: StateProvider) => {
        dispatch(newLoadingAction());
        try {
            const {code} = getState().editor;
            const res = await client.formatCode(code);

            if (res.formatted) {
                dispatch(newBuildResultAction(res));
            }
        } catch (err) {
            dispatch(newErrorAction(err.message));
        }
    };

export const dispatchToggleTheme: Dispatcher =
    (dispatch: DispatchFn, getState: StateProvider) => {
        const { darkMode } = getState().settings;
        config.darkThemeEnabled = !darkMode;
        dispatch(newToggleThemeAction())
    };