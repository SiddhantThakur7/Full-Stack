import React from 'react';

import './custom-button.styles.scss';

const CustomButton = ({ children, func, isGoogleSignIn, inverted, ...otherProps}) => (
    <button className={`${inverted ? 'inverted' : ''} ${isGoogleSignIn ? 'google-sign-in' : ''} custom-button`} onClick={func}>
        {children}
    </button>
)

export default CustomButton;