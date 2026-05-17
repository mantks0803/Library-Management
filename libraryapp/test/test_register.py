import hashlib

import pytest

from libraryapp.test.test_base import test_session, test_app, test_client, sample_user
from libraryapp.dao.users import add_user, validate_phone, validate_username, change_password, auth_user, get_current_user, update_user, validate_username, change_password, auth_user,\
    validate_password
from libraryapp.models import User
from libraryapp.utils import hash_password

def test_register_success(test_session):
    add_user(name="test1", email="test@gmail.com", phone="08484822222", username="tester", password="P@ssw0rd")
    u = User.query.filter(User.username.__eq__("tester")).first()

    assert u
    assert u.name == "test1"
    assert u.email == "test@gmail.com"
    assert u.phone == "08484822222"
    assert u.password == str(hashlib.md5('P@ssw0rd'.encode('utf-8')).hexdigest())
    assert u.active == True

def test_existing_username(test_session):
    add_user(name='Nguyen Van A',email="nva@gmail.com",phone="08484822222", username='test', password='aB@123456789')

    with pytest.raises(ValueError):
        add_user(name='Nguyen Van B',email="nvb@gmail.com",phone="09123456789", username='test', password='aB@123456787')

@pytest.mark.parametrize('password', [
    '1aB', '1'*8, 'a'*8, 'A'*8, '1a'*4, 'aA'*4
])
def test_invalid_password(password, test_session):
    with pytest.raises(ValueError):
        add_user(name='tester',email="test@gmail.com",phone="08484822222", username='test', password=password)

def test_update_user_success(sample_user):
    update_user(1,"newname", "0848482273")
    user_updated = User.query.filter(User.id==1).first()
    assert user_updated.name == "newname"
    assert user_updated.phone == "0848482273"

def test_update_invalid_phone(sample_user):
    with pytest.raises(ValueError) as ex:
        update_user(sample_user.id, "newname", "sodienthoai")

    assert "Số điện thoại không hợp lệ" in str(ex.value)

    user_updated = User.query.get(sample_user.id)

    assert user_updated.name == sample_user.name
    assert user_updated.phone == sample_user.phone


def test_get_current_user(sample_user):
    result = get_current_user(1)
    assert result.username == "tester"


def test_login_success(sample_user):
    res = auth_user('tester', "Abc1234@")

    assert res is not None
    assert res.username == sample_user.username


def test_login_wrong_password(sample_user):
    res = auth_user("tester", "12345678")

    assert res is None


def test_login_wrong_username(sample_user):
    result = auth_user("username", "Abc123@")
    assert result is None


def test_change_pass_success(sample_user):
    new_password = "P@ssw0rd"
    change_password(sample_user, new_password)

    assert sample_user.password == hash_password(new_password)


def test_username_exists(sample_user):
    assert validate_username("tester") is False


def test_username_available(test_session):
    assert validate_username("testuser") is True


def test_valid_phone(test_session):
    assert validate_phone(phone="0848482222") is True


def test_invalid_prefix(test_session):
    assert validate_phone(phone="18484822222") is False


def test_invalid_short(test_session):
    assert validate_phone(phone="084848") is False


def test_invalid_long(test_session):
    assert validate_phone(phone="084848394394733434") is False


def test_invalid_letter(test_session):
    assert validate_phone(phone="0848482abcd") is False


def test_empty_phone(test_session):
    assert validate_phone(phone="") is False


def test_validate_password_match():
    assert validate_password("Abc1234@", "Abc1234@") is True


def test_validate_password_not_match():
    assert validate_password("Abc1234@", "Abc1234#") is False


def test_register_existed(test_client, mocker):
    mocker.patch('libraryapp.dao.users.validate_username', return_value=False)
    mocker.patch("libraryapp.routes.register.render_template", return_value="auth/register.html")

    res = test_client.post('/register', data={
        'name': 'test',
        'email': 'test@gmail.com',
        'phone': '08484822222',
        'username': 'tester',
        'password': 'Abc1234@',
        'confirm' : 'Abc1234@'
    })
    assert res.status_code == 200

def test_register_invalid_phone(test_client, mocker):
    mocker.patch('libraryapp.dao.users.validate_username', return_value=True)
    mocker.patch('libraryapp.dao.users.validate_phone', return_value=False)
    mocker.patch("libraryapp.routes.register.render_template", return_value="auth/register.html")

    res = test_client.post('/register', data={
        'name': 'test',
        'email': 'test@gmail.com',
        'phone': '08484822222',
        'username': 'tester',
        'password': 'Abc1234@',
        'confirm': 'Abc1234@'
    })

    assert res.status_code == 200

def test_register_password_not_match(test_client, mocker):
    mocker.patch('libraryapp.dao.users.validate_username', return_value=True)
    mocker.patch('libraryapp.dao.users.validate_phone', return_value=True)
    mocker.patch('libraryapp.dao.users.validate_password', return_value=False)
    mocker.patch("libraryapp.routes.register.render_template", return_value="auth/register.html")

    res = test_client.post('/register', data={
        'name': 'test',
        'email': 'test@gmail.com',
        'phone': '08484822222',
        'username': 'tester',
        'password': 'Abc1234@',
        'confirm':'Abc1234#'
    })

    assert res.status_code == 200

def test_register_view(mocker, test_client):
    mocker.patch("libraryapp.routes.register.render_template", return_value="auth/register.html")

    response = test_client.get("/register")

    assert response.status_code == 200

def test_client_register_success(test_client, mocker):
    mocker.patch('libraryapp.dao.users.validate_username', return_value=True)
    mocker.patch('libraryapp.dao.users.validate_phone', return_value=True)
    mocker.patch('libraryapp.dao.users.validate_password', return_value=True)

    mock_add = mocker.patch('libraryapp.dao.users.add_user')

    res = test_client.post('/register', data={
        'name': 'Bao',
        'email': 'a@gmail.com',
        'phone': '08484822222',
        'username': 'tester',
        'password': 'Abc1234@',
        'confirm': 'Abc1234@'
    })

    assert res.status_code == 302
    assert "/login" in res.headers["Location"]
    assert mock_add.called

def test_register_value_error(test_client, mocker):
    mocker.patch('libraryapp.dao.users.validate_username', return_value=True)
    mocker.patch('libraryapp.dao.users.validate_phone', return_value=True)
    mocker.patch('libraryapp.dao.users.validate_password', return_value=True)

    mocker.patch('libraryapp.dao.users.add_user',side_effect=ValueError("Sai dữ liệu"))

    mocker.patch("libraryapp.routes.register.render_template", return_value="error")

    res = test_client.post('/register', data={
        'name': 'Bao',
        'email': 'a@gmail.com',
        'phone': '08484822222',
        'username': 'tester',
        'password': 'Abc12345',
        'confirm': 'Abc12345'
    })

    assert res.status_code == 200
    assert res.data == b"error"

def test_register_system_error(test_client, mocker):
    mocker.patch('libraryapp.dao.users.validate_username', return_value=True)
    mocker.patch('libraryapp.dao.users.validate_phone', return_value=True)
    mocker.patch('libraryapp.dao.users.validate_password', return_value=True)

    mocker.patch(
        'libraryapp.dao.users.add_user',
        side_effect=Exception("DB crash")
    )

    mocker.patch("libraryapp.routes.register.render_template", return_value="error")

    res = test_client.post('/register', data={
        'name': 'Bao',
        'email': 'a@gmail.com',
        'phone': '08484822222',
        'username': 'tester',
        'password': 'Abc12345',
        'confirm': 'Abc12345'
    })

    assert res.status_code == 200
    assert res.data == b"error"

