function removeFromCart(bookId) {
    if (confirm('Xóa sách khỏi giỏ mượn?')) {
        fetch(`/cart/remove/${bookId}`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            });
    }
}

function clearCart() {
    if (confirm('Xóa tất cả sách khỏi giỏ mượn?')) {
        fetch('/cart/clear', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
    }
}