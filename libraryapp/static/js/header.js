function updateCartBadge() {
    const badge = document.querySelector('#cart-badge');
    if (badge) {
        fetch('/cart/count')
            .then(res => res.json())
            .then(data => {
                badge.textContent = data.count;
                badge.style.display = data.count > 0 ? 'inline-block' : 'none';
            })
            .catch(() => {});
    }
}
document.addEventListener('DOMContentLoaded', updateCartBadge);