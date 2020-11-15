class Checkout {
    account = "";
    buyerId = "";
    buyerName = "";

    products = {};
    cart = {};

    constructor(account, buyerId, buyerName) {
        this.account = account;
        this.buyerId = buyerId;
        this.buyerName = buyerName;
    }

    addProduct(productId, quantity) {
        this.products[productId] = quantity;
    }

    addToCart(productId) {
        if (this.products.hasOwnProperty(productId) && this.products[productId] > 0) {
            if (this.cart.hasOwnProperty(productId)) {
                ++this.cart[productId];
            } else {
                this.cart[productId] = 1;
            }
            --this.products[productId];

            return true;
        }

        return false;
    }

    removeFromCart(productId) {
        if (this.products.hasOwnProperty(productId) && this.cart.hasOwnProperty(productId)) {
            if (this.cart[productId] > 1) {
                --this.cart[productId];
            } else {
                delete this.cart[productId];
            }
            ++this.products[productId];

            return true;
        }

        return false;
    }

    cartAsArrayOfDict() {
        let array = []
        for (var id in this.cart) {
            array.push({
                productId: id,
                quantity: this.cart[id]
            });
        }

        return array;
    }
}
