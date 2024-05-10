import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { createStructuredSelector } from 'reselect'

import WithSpinner from '../../components/with-spinner/with-spinner.components';
import { selectCollectionsLoaded } from "../../redux/shop/shop.selector";
import CollectionPage from "../collection/collection.component";


const mapStateToProps = createStructuredSelector({
    isLoading: state => !selectCollectionsLoaded(state)
});

export const CollectionPageContainer = compose(
    connect(mapStateToProps),
    WithSpinner
)(CollectionPage);

export default CollectionPageContainer;