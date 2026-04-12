function addToCart(bookId, bookTitle) {
    fetch(`/cart/add/${bookId}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${data.success ? 'success' : 'warning'} alert-dismissible fade show`;
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                <i class="fa-solid fa-${data.success ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                ${data.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.card'));

            if (data.success && typeof updateCartBadge === 'function') {
                updateCartBadge(); // Gọi hàm update badge trên header
            }
        });
}