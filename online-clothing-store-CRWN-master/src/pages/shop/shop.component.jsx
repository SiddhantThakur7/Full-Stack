import React, { useEffect } from "react";
import { Route } from "react-router-dom";

// import SHOP_DATA from "./shop.data";

// import CollectionsOverview from "../../components/collections-overview/collections-overview.component";
// import { createStructuredSelector } from 'reselect';

import { fetchCollectionsStart } from "../../redux/shop/shop.actions.js";

import { connect } from "react-redux";
// import { updateCollections } from "../../redux/shop/shop.actions";
// import WithSpinner from "../../components/with-spinner/with-spinner.components";
import collectionsOverviewContainer from "../../components/collections-overview/collection-overview.container";
import { CollectionPageContainer } from "../collection/collection.container";

// const CollectionsOverviewWithSpinner = WithSpinner(CollectionsOverview);
// const CollectionPageWithSpinner = WithSpinner(CollectionPage);

const ShopPage = ({ fetchCollectionsStart, match }) => {
  useEffect(() => {
    fetchCollectionsStart();
  }, [fetchCollectionsStart]);

  return (
    <div className="shop-page">
      <Route
        exact
        path={`${match.path}`}
        component={collectionsOverviewContainer}
      />
      <Route
        path={`${match.path}/:collectionId`}
        component={CollectionPageContainer}
      />
    </div>
  );
};

// const mapDispatchToProps = (dispatch) => ({
//   updateCollections: (collectionsMap) =>
//     dispatch(updateCollections(collectionsMap)),
// });

const mapDispatchToProps = (dispatch) => ({
  fetchCollectionsStart: () => dispatch(fetchCollectionsStart()),
});

export default connect(null, mapDispatchToProps)(ShopPage);
