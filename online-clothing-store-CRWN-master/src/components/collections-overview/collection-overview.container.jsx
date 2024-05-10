import React from "react";
import { connect } from "react-redux";
import { compose } from "redux";
import { createStructuredSelector } from "reselect";
import { selectIsCollectionFetching } from "../../redux/shop/shop.selector";
import WithSpinner from "../with-spinner/with-spinner.components";
import collectionsOverviewComponent from "./collections-overview.component";

const mapStateToProps = createStructuredSelector({
  isLoading: selectIsCollectionFetching,
});

// export const collectionsOverviewContainer = connect(mapStateToProps)(
//   WithSpinner(collectionsOverviewComponent)
// );

export const collectionsOverviewContainer = compose(
  connect(mapStateToProps),
  WithSpinner
)(collectionsOverviewComponent);


export default collectionsOverviewContainer;
