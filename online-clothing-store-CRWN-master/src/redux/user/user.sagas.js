import { takeLatest, put, call, all } from "redux-saga/effects";
import {
  auth,
  createUserProfileDocument,
  getCurrentUser,
  googleProvider,
} from "../../firebase/firebase.utils";
import {
  emailSignInFailure,
  emailSignInSuccess,
  googleSignInFailure,
  googleSignInSuccess,
  signUpFailure,
  signOutFailure,
  signOutSuccess,
  signUpSuccess,
} from "./user.actions";
import UserActionTypes from "./user.types";

export function* signInWithGoogle() {
  try {
    const { user } = yield auth.signInWithPopup(googleProvider);
    const UserRef = yield call(createUserProfileDocument, user);
    const userSnapshot = yield UserRef.get();
    yield put(
      googleSignInSuccess({ id: userSnapshot.id, ...userSnapshot.data() })
    );
  } catch (error) {
    yield put(googleSignInFailure(error));
  }
}
export function* onGoogleSignInStart() {
  yield takeLatest(UserActionTypes.GOOGLE_SIGN_IN_START, signInWithGoogle);
}

export function* signInWithEmail({ payload: { email, password } }) {
  try {
    const { user } = yield auth.signInWithEmailAndPassword(email, password);
    const UserRef = yield call(createUserProfileDocument, user);
    const userSnapshot = yield UserRef.get();
    yield put(
      emailSignInSuccess({ id: userSnapshot.id, ...userSnapshot.data() })
    );
  } catch (error) {
    yield put(emailSignInFailure(error));
  }
}
export function* onEmailSignInStart() {
  yield takeLatest(UserActionTypes.EMAIL_SIGN_IN_START, signInWithEmail);
}

export function* isUserAuthenticated() {
  try {
    const userAuth = yield getCurrentUser();
    if (!userAuth) {
      return;
    }
    const UserRef = yield call(createUserProfileDocument, userAuth);
    const userSnapshot = yield UserRef.get();
    yield put(
      emailSignInSuccess({ id: userSnapshot.id, ...userSnapshot.data() })
    );
  } catch (error) {
    yield put(emailSignInFailure(error));
  }
}
export function* onCheckUserSession() {
  yield takeLatest(UserActionTypes.CHECK_USER_SESSION, isUserAuthenticated);
}

export function* signOut() {
  try {
    yield auth.signOut();
    yield put(signOutSuccess());
  } catch (error) {
    yield put(signOutFailure(error));
  }
}

export function* onSignOutStart() {
  yield takeLatest(UserActionTypes.SIGN_OUT_START, signOut);
}

export function* signUp({ payload: { displayName, email, password } }) {
  try {
    const { user } = yield auth.createUserWithEmailAndPassword(email, password);
    const UserRef = yield createUserProfileDocument(user, { displayName });
    const userSnapshot = yield UserRef.get();
    yield put(signUpSuccess({ id: userSnapshot.id, ...userSnapshot.data() }));
  } catch (error) {
    yield put(signUpFailure);
  }
}

export function* onSignUpStart() {
  yield takeLatest(UserActionTypes.SIGN_UP_START, signUp);
}

export function* userSaga() {
  yield all([
    call(onCheckUserSession),
    call(onEmailSignInStart),
    call(onGoogleSignInStart),
    call(onSignOutStart),
    call(onSignUpStart),
  ]);
}
