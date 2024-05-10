document.addEventListener('DOMContentLoaded', () => {
    // Your script code here
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const cartCountElement = document.querySelector('.cart-count');

    const cart = [];

    addToCartButtons.forEach(button => {
      button.addEventListener('click', () => {
        const productId = button.dataset.productId;
        const quantity = parseInt(button.nextElementSibling.value) || 1; // Get quantity from the input field

        cart.push({ productId, quantity });

        updateCartCount();
        displayCartItems();
      });
    });

    function updateCartCount() {
      cartCountElement.textContent = cart.length;
    }

    function displayCartItems() {
        const cartTable = document.getElementById('cartTable'); // Select the table by its ID
        console.log("Cart table element:", cartTable); // Add this line for debugging

        const tbody = document.createElement('tbody');

      cart.forEach(item => {
        const productElement = document.querySelector(`.product[data-id="${item.productId}"]`);
        const productName = productElement.querySelector('h2').textContent;
        const productPrice = parseFloat(productElement.querySelector('p').textContent.slice(1)); // Remove '$' and parse as float

        const cartItemRow = createCartItemRow({ name: productName, price: productPrice }, item.quantity);
        tbody.appendChild(cartItemRow);
      });

      // Append the tbody to the table
      if (cartTable) {
        cartTable.replaceChild(tbody, cartTable.querySelector('tbody'));
      } else {
        console.error("Cart table element not found");
      }
    }

    function createCartItemRow(product, quantity) {
      const row = document.createElement('tr');
      row.classList.add('cart-item');

      const productNameCell = document.createElement('td');
      productNameCell.textContent = product.name;
      row.appendChild(productNameCell);

      const quantityCell = document.createElement('td');
      quantityCell.textContent = quantity;
      row.appendChild(quantityCell);

      const priceCell = document.createElement('td');
      priceCell.textContent = `$${product.price}`;
      row.appendChild(priceCell);

      const totalCell = document.createElement('td');
      totalCell.textContent = `$${product.price * quantity}`;
      row.appendChild(totalCell);

      const removeCell = document.createElement('td');
      const removeButton = document.createElement('button');
      removeButton.textContent = 'Remove';
      removeButton.addEventListener('click', () => {
        // Remove the item from the cart and update the UI
        const index = cart.findIndex(item => item.name === product.name);
        if (index !== -1) {
          cart.splice(index, 1);
          displayCartItems();
          updateCartCount();
        }
      });
      removeCell.appendChild(removeButton);
      row.appendChild(removeCell);

      return row;
    }
});
