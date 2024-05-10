import { takeLatest, call, put, all } from "redux-saga/effects";
import {
  firestore,
  convertCollectionsSnapshotToMap,
} from "../../firebase/firebase.utils";
import {
  fetchCollectionsFailure,
  fetchCollectionsSuccess,
} from "./shop.actions";

import ShopActionTypes from "./shop.types";

export function* fetchCollectionsAsync() {
  yield console.log("I am Hired!");
  try {
    const collectionRef = firestore.collection("collections");
    const snapshot = yield collectionRef.get();
    const collectionMap = yield call(convertCollectionsSnapshotToMap, snapshot);
    yield put(fetchCollectionsSuccess(collectionMap));
  } catch (error) {
    put(fetchCollectionsFailure(error.message));
  }

  // collectionRef
  //   .get()
  //   .then((snapshot) => {
  //     const collectionsMap = convertCollectionsSnapshotToMap(snapshot);
  //     console.log(collectionsMap);
  //     dispatch(fetchCollectionsSuccess(collectionsMap));
  //   })
  //   .catch((error) => dispatch(fetchCollectionsFailure(error.message)));
}

export function* fetchCollectionsStart() {
  yield takeLatest(
    ShopActionTypes.FETCH_COLLECTIONS_START,
    fetchCollectionsAsync
  );
}


export function* shopSagas() {
  yield all([call(fetchCollectionsStart)]);
}