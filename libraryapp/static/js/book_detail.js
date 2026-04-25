function addToCart(bookId, bookTitle) {
    // Kiểm tra giỏ hàng có vượt quá 5 sách không (thông qua localStorage)
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    
    if (cart.length >= 5) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            <i class="fa-solid fa-exclamation-circle me-2"></i>
            Bạn chỉ được mượn tối đa 5 quyển sách! Vui lòng trả sách trước khi thêm sách mới.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.card'));
        return;
    }

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