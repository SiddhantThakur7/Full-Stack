import React, { useState } from "react";

import FormInput from "../form-input/form-input.component";
import CustomButton from "../custom-button/custom-button.component";

import "./sign-up.styles.scss";
import { connect } from "react-redux";
import { sigUpStart } from "../../redux/user/user.actions";

const SignUp = ({ SignUpStart }) => {
  const [userCredentials, setCredentials] = useState({
    displayName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const { displayName, email, password, confirmPassword } = userCredentials;
  const handleSubmit = async (event) => {
    event.preventDefault();

    if (password !== confirmPassword) {
      alert("passwords dont match");
      return;
    }

    SignUpStart(displayName, email, password);
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setCredentials({ ...userCredentials, [name]: value });
  };

  return (
    <div className="sign-up">
      <h2 className="title">I do not have an account</h2>
      <span>Sign up with your email and password</span>
      <form className="sign-up-form" onSubmit={handleSubmit}>
        <FormInput
          type="text"
          name="displayName"
          value={displayName}
          onChange={handleChange}
          label="Display name"
        ></FormInput>

        <FormInput
          type="text"
          name="email"
          value={email}
          onChange={handleChange}
          label="Email"
        ></FormInput>

        <FormInput
          type="password"
          name="password"
          value={password}
          onChange={handleChange}
          label="Password"
        ></FormInput>

        <FormInput
          type="password"
          name="confirmPassword"
          value={confirmPassword}
          onChange={handleChange}
          label="Confirm Password"
        ></FormInput>

        <CustomButton type="submit">Sign-Up</CustomButton>
      </form>
    </div>
  );
};

const mapDispatchToProps = (dispatch) => ({
  SignUpStart: (displayName, email, password) =>
    dispatch(sigUpStart({ displayName, email, password })),
});

export default connect(null, mapDispatchToProps)(SignUp);
