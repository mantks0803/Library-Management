
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


    const changePwdForm = document.getElementById('changePasswordForm');

    if (changePwdForm) {
        changePwdForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const oldPwd = document.getElementById('oldPassword').value;
            const newPwd = document.getElementById('newPassword').value;
            const confirmPwd = document.getElementById('confirmPassword').value;

            if (newPwd !== confirmPwd) {
                alert("Mật khẩu mới không khớp! Vui lòng nhập lại.");
                return;
            }

            const formData = new FormData();
            formData.append('old_password', oldPwd);
            formData.append('new_password', newPwd);
            formData.append('confirm_password', confirmPwd);

            fetch('/api/users/change-password', {
                method: 'PUT',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.ok) {
                    alert("Đổi mật khẩu thành công!");
                    changePwdForm.reset();

                    var modalElement = document.getElementById('changePasswordModal');
                    if (modalElement) {
                        var modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                        modal.hide();
                    }
                } else {
                    alert("Lỗi: " + data.error);
                }
            })
            .catch(err => {
                console.error('Lỗi khi đổi mật khẩu:', err);
                alert("Lỗi kết nối đến máy chủ!");
            });
        });
    }
