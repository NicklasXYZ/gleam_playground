import React from 'react';
import { Provider } from 'react-redux';
import { Fabric } from 'office-ui-fabric-react/lib/Fabric';
import { ConnectedRouter } from 'connected-react-router';
import { Switch, Route, BrowserRouter } from "react-router-dom";

import { configureStore } from './store';
import { history } from './store/configure';
import Playground from './Playground';
import './App.css';
import config from './services/config'

// Configure store and import config from localStorage
const store = configureStore();
config.sync();

function App() {
  return (
    <Provider store={store}>
        <ConnectedRouter history={history}>
                <Fabric className="App">
                    <Switch>
                        <Route
                            // TODO: Is this 'basename' path needed here?
                            basename="/apps/gleam-playground"
                            path="/(snippet)?/:snippetID?"
                            component={Playground}
                        />
                    </Switch>
                </Fabric>
        </ConnectedRouter>
    </Provider>
  );
}

export default App;
