import React from 'react'
import StripeCheckout from 'react-stripe-checkout';

const StripeCheckoutButton = ({price}) => {
    const priceForStripe = price * 100;
    const publishablekey = 'pk_test_51IeJSaSJu1tANk5qWamhR73of5jBZh835Y8nbgOxSuOdhdTiTHMsGaFMltYXw7t29hJFeFPWn4MkthjXWlHuPSuI00ebpMr56o';

    const onToken = token => {
        console.log(token);
        alert('Payment Successfully Completed!')
    }

    return(
        <StripeCheckout 
            label="PayNow"
            name='CRWN Pvt. Ltd.'
            billingAddress
            shippingAddress
            image='https://sendeyo.com/up/d/f3eb2117da'
            description={`Your Total Is $${price}`}
            amount={priceForStripe}
            panelLabel='Complete Payment'
            token={onToken}
            stripeKey={publishablekey}
        />
    );
};

export default StripeCheckoutButton;