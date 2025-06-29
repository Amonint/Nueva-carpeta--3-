let cart = [];

// Search functionality
document.getElementById('search-input').addEventListener('input', async (e) => {
    const query = e.target.value;
    const response = await fetch(`/search?q=${query}`);
    const products = await response.json();
    updateProductsDisplay(products);
});

function updateProductsDisplay(products) {
    const container = document.getElementById('products-container');
    container.innerHTML = products.map(product => `
        <div class="col-md-6 mb-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text">Precio: $${product.price.toFixed(2)}</p>
                    <p class="card-text">Stock: ${product.stock}</p>
                    <button class="btn btn-primary" onclick="addToCart(${product.id})">
                        Añadir al carrito
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Cart functionality
async function addToCart(productId) {
    const response = await fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    });
    cart = await response.json();
    updateCartDisplay();
}

async function updateCartItemQuantity(productId, quantity) {
    const response = await fetch('/update_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    });
    cart = await response.json();
    updateCartDisplay();
}

function updateCartDisplay() {
    const cartItems = document.getElementById('cart-items');
    const cartCount = document.getElementById('cart-count');
    const cartTotal = document.getElementById('cart-total');
    
    cartItems.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div>
                <h6>${item.name}</h6>
                <p>$${item.price.toFixed(2)}</p>
            </div>
            <div class="cart-item-quantity">
                <button class="btn btn-sm btn-outline-secondary btn-quantity" 
                        onclick="updateCartItemQuantity(${item.product_id}, ${item.quantity - 1})">-</button>
                <span>${item.quantity}</span>
                <button class="btn btn-sm btn-outline-secondary btn-quantity" 
                        onclick="updateCartItemQuantity(${item.product_id}, ${item.quantity + 1})">+</button>
            </div>
        </div>
    `).join('');
    
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    cartTotal.textContent = total.toFixed(2);
    cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
}

async function checkout() {
    if (cart.length === 0) {
        alert('El carrito está vacío');
        return;
    }
    
    const response = await fetch('/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    });
    
    const result = await response.json();
    if (result.message) {
        alert('¡Compra completada con éxito!');
        cart = [];
        updateCartDisplay();
    } else {
        alert('Error al procesar la compra');
    }
}

function toggleCart() {
    const cartContainer = document.getElementById('cart-container');
    cartContainer.style.display = cartContainer.style.display === 'none' ? 'block' : 'none';
} 