import { createStore, applyMiddleware } from "redux";
import {persistStore} from 'redux-persist';

import logger from 'redux-logger';
import thunk from 'redux-thunk';
import createSagaMiddleware from 'redux-saga';

import rootReducer from './root-reducer';
import rootSaga from "./root.saga";



const sagaMiddleware = createSagaMiddleware();

// putting the logger function inside an array, can add several othwer middleware functions too.
const middlewares = [sagaMiddleware];

if (process.env.NODE_ENV == 'development') {
        middlewares.push(logger);
}

// do not need to add seperate individual middlewares therefore providing abstraction to the number and names of the middle wares to be implemented
export const store = createStore(rootReducer, applyMiddleware(...middlewares));

sagaMiddleware.run(rootSaga);

export const persistor = persistStore(store);

export default {store, persistor};
