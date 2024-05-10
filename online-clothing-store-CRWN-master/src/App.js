import React, {useEffect} from "react";
import "./App.css";
import { connect } from "react-redux";

import { Switch, Route, Redirect } from "react-router-dom";

import HomePage from "./pages/homepage/homepage.component";
import ShopPage from "./pages/shop/shop.component";
import CheckoutPage from './pages/checkout/checkout.component';
import SignInAndSignUpPage from "./pages/sign-in-and-sign-up/sign-in-and-sign-up.component";

import Header from "./components/header/header.component.jsx";

import { selectCurrentUser } from "./redux/user/user.selector";
import { createStructuredSelector } from "reselect";
import { checkUserSession } from "./redux/user/user.actions";

// import { selectCollectionForPreview } from "./redux/shop/shop.selector";
const App = ({ checkUserSession, currentUser }) => {
  // componentDidMount() {
  //   const { checkUserSession } = this.props;
  //   checkUserSession();
  // }
 
  useEffect(() => {
    checkUserSession();
  }, [checkUserSession]); 

    return (
      <div>
        {/* <Header currentUser={this.state.currentUser} /> */}
        {/* Passing the current uer from the redux store instead of drilling them from the App.js */}
        <Header />
        <Switch>
          <Route exact path="/" component={HomePage} />
          <Route path="/shop" component={ShopPage} />
          <Route path="/checkout" component={CheckoutPage} />
          {/* <Route exact path="/signin" component={SignInAndSignUpPage} /> */}
          <Route
            exact
            path="/signin"
            render={() =>
              currentUser ? (
                <Redirect to="/" />
              ) : (
                <SignInAndSignUpPage />
              )
            }
          />
        </Switch>
      </div>
    );
  }

const mapStateToProps = createStructuredSelector({
  currentUser: selectCurrentUser,
  // collectionsArray: selectCollectionForPreview
});

const mapDispatchToProps = (dispatch) => ({
  checkUserSession: () => dispatch(checkUserSession())
});

export default connect(mapStateToProps, mapDispatchToProps)(App);
