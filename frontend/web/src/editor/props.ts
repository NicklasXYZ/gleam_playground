import * as monaco from 'monaco-editor';
import {MonacoSettings} from '../services/config';
import { getFontFamily, getDefaultFontFamily } from '../services/fonts';

export const LANGUAGE_GLEAM = 'gleam';

export const DEMO_CODE = [
    'import gleam/io\n',
    'pub external type CharList\n',
    '// Main escript entrypoint (function is required)',
    'pub fn main(_args: List(CharList)) {',
    '  io.println("Hello, world!")',
    '}',
].join('\n');

// stateToOptions converts MonacoState to IEditorOptions
export const stateToOptions = (state: MonacoSettings): monaco.editor.IEditorOptions => {
    const {
        selectOnLineNumbers,
        mouseWheelZoom,
        smoothScrolling,
        cursorBlinking,
        fontLigatures,
        cursorStyle,
        contextMenu
    } = state;
    return {
        selectOnLineNumbers, mouseWheelZoom, smoothScrolling, cursorBlinking, cursorStyle, fontLigatures,
        fontFamily: state.fontFamily ? getFontFamily(state.fontFamily) : getDefaultFontFamily(),
        showUnused: true,
        automaticLayout: true,
        minimap: {enabled: state.minimap},
        contextmenu: contextMenu,
    };
};
