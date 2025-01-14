import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import { initializeIcons } from '@uifabric/icons';
import * as serviceWorker from './serviceWorker';
import { registerGleamLanguageProvider } from './editor/provider';
import apiClient from './services/api';


initializeIcons();
// TODO: Code suggestions do not work yet...
// registerGleamLanguageProvider(apiClient);

ReactDOM.render(<App />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
