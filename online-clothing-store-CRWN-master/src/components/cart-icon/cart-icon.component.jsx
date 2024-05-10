import React from "react";

import { ReactComponent as Shoppingicon } from "../../assets/11.1 shopping-bag.svg";
import { toggleCartHidden } from "../../redux/cart/cart.actions";
import { connect } from "react-redux";
import { selectCartItemsCount } from "../../redux/cart/cart.selectors";

import "./cart-icon.styles.scss";
import { createStructuredSelector } from "reselect";

const CartIcon = ({ itemCount, toggleCartHidden }) => (
  <div className="cart-icon" onClick={toggleCartHidden}>
    <Shoppingicon className="shopping-icon" />
    <span className="item-count">{itemCount}</span>
  </div>
);

const mapStateToProps = createStructuredSelector({
  itemCount: selectCartItemsCount
});

const mapDispatchToProps = (dispatch) => ({
  toggleCartHidden: () => dispatch(toggleCartHidden()),
});

export default connect(mapStateToProps, mapDispatchToProps)(CartIcon);
