
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
        const oldPwdInput = document.getElementById('oldPassword');
        const newPwdInput = document.getElementById('newPassword');
        const confirmPwdInput = document.getElementById('confirmPassword');
        const newPwdError = document.getElementById('newPasswordError');
        const confirmPwdError = document.getElementById('confirmPasswordError');

        function validatePasswordRealtime() {
            const newPwd = newPwdInput.value;
            const confirmPwd = confirmPwdInput.value;

            newPwdError.textContent = '';
            confirmPwdError.textContent = '';

            if (newPwd.length > 0 && newPwd.length < 6) {
                newPwdError.textContent = 'Mật khẩu phải có ít nhất 6 ký tự!';
                return false;
            }

            if (newPwd && !/[0-9]/.test(newPwd)) {
                newPwdError.textContent = 'Mật khẩu phải chứa ít nhất một chữ số!';
                return false;
            }

            if (newPwd && !/[a-z]/.test(newPwd)) {
                newPwdError.textContent = 'Mật khẩu phải chứa ít nhất một chữ thường!';
                return false;
            }

            if (newPwd && !/[A-Z]/.test(newPwd)) {
                newPwdError.textContent = 'Mật khẩu phải chứa ít nhất một chữ hoa!';
                return false;
            }

            if (confirmPwd && newPwd !== confirmPwd) {
                confirmPwdError.textContent = 'Mật khẩu xác nhận không khớp!';
                return false;
            }

            return true;
        }

        newPwdInput.addEventListener('input', validatePasswordRealtime);
        confirmPwdInput.addEventListener('input', validatePasswordRealtime);

        changePwdForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const oldPwd = oldPwdInput.value;
            const newPwd = newPwdInput.value;
            const confirmPwd = confirmPwdInput.value;

            if (!validatePasswordRealtime()) {
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
