let currentReturnSlipId = null;

function openReturnModal(slipId) {
    currentReturnSlipId = slipId;

    const slip = historyData.find(s => s.slip_id === slipId);
    if (!slip) return;

    // Nạp text vào Modal
    document.getElementById('modalSlipId').textContent = '#' + slip.slip_id;
    document.getElementById('modalBorrowDate').textContent = slip.borrow_date;
    document.getElementById('modalDueDate').textContent = slip.due_date;

    // Lấy ngày hôm nay làm "Ngày trả thực tế"
    const today = new Date();
    document.getElementById('modalCurrentDate').textContent = today.toLocaleDateString('vi-VN');

    // Đổ danh sách các cuốn sách ra
    const bookListEl = document.getElementById('modalBookList');
    bookListEl.innerHTML = ''; // Xóa sách cũ
    slip.books.forEach(book => {
        const li = document.createElement('li');
        li.className = 'list-group-item px-0 fw-medium text-primary';
        li.innerHTML = `<i class="fa-solid fa-caret-right text-muted me-2"></i>${book.title}`;
        bookListEl.appendChild(li);
    });

    const modal = new bootstrap.Modal(document.getElementById('returnBookModal'));
    modal.show();
}

document.getElementById('btnConfirmReturn')?.addEventListener('click', function() {
    if (!currentReturnSlipId) return;

    const btn = this;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Đang xử lý...';
    btn.disabled = true;

    fetch(`/return-slip/${currentReturnSlipId}`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            window.location.reload();
        } else {
            alert("Lỗi: " + data.message);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    })
    .catch(err => {
        console.error(err);
        alert("Lỗi kết nối đến máy chủ!");
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
});