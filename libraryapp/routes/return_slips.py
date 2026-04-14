from flask import Blueprint, jsonify
from flask_login import current_user

from libraryapp.utils import permission
from libraryapp.models import UserRole
from libraryapp.dao.return_slips import return_slip

return_slips_bp = Blueprint('return_slips', __name__)

@return_slips_bp.route('/return-slip/<int:slip_id>', methods=['POST'])
@permission(allow={
    "roles": [UserRole.READER],
    "access": True
})
def api_return_slip(slip_id):
    success, message = return_slip(slip_id, current_user.id)
    return jsonify({
        'success': success,
        'message': message
    })