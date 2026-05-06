document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('updateProfileForm');

    // Chỉ chạy nếu trang hiện tại có cái form cập nhật
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const userId = document.getElementById('userId').value;
            const newName = document.getElementById('updateName').value;
            const newPhone = document.getElementById('updatePhone').value;

            const phoneRegex = /^(03|05|07|08|09)\d{8}$/;
            if (!phoneRegex.test(newPhone)) {
                alert("Số điện thoại không hợp lệ!");
                return;
            }

            const formData = new FormData();
            formData.append('name', newName);
            formData.append('phone', newPhone);

            fetch(`/api/users/${userId}`, {
                method: 'PUT',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if(data.ok) {
                    document.getElementById('display-name').textContent = newName;
                    document.getElementById('info-name').textContent = newName;
                    document.getElementById('info-phone').textContent = newPhone;

                    var updateModal = document.getElementById('updateProfileModal');
                    var modal = bootstrap.Modal.getInstance(updateModal);
                    modal.hide();

                    alert('Cập nhật thông tin thành công!');
                } else {
                    alert('Có lỗi xảy ra: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Lỗi kết nối đến máy chủ!');
            });
        });
    }
});