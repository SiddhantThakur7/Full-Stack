import { takeLatest, all, put, call } from "redux-saga/effects";

import UserActionTypes from "../user/user.types";
import { clearCart } from "./cart.actions";



export function* clearCartSignOut () {
    yield put(clearCart());
} 

export function* onSignoutSuccess() {
    yield takeLatest(UserActionTypes.SIGN_OUT_SUCCESS, clearCartSignOut);
};


export function* cartSagas() {
    yield all([call(onSignoutSuccess)]);
} 