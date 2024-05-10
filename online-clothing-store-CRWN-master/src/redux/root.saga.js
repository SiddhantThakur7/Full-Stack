import { all, call } from "redux-saga/effects";
import { cartSagas } from "./cart/cart.sagas";
import { fetchCollectionsStart, shopSagas } from "./shop/shop.sagas";
import { userSaga } from "./user/user.sagas";

function* rootSaga() {
  yield all([call(fetchCollectionsStart), call(userSaga), call(shopSagas), call(cartSagas)]);
}


export default rootSaga;