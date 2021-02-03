import requests

def test_admin_login(http_service, admin_user):
    res = admin_user.get(f"{http_service}/admin/")
    assert "This is the admin section!" in res.text

def test_admin_load_users_page(http_service, admin_user):
    res = admin_user.get(f"{http_service}/admin/users")
    assert "Admin | Manage Users" in res.text

def test_admin_import_users_from_csv(http_service, admin_user):
    # TODO: also verify users
    team_count_before = requests.get(f"{http_service}/stats.json").json()["Teams competing"]
    res = admin_user.post(f"{http_service}/admin/import_users", files={
        'import_data': open('resources/users_to_import.csv'),
    })
    assert res.status_code == 200
    team_count_after = requests.get(f"{http_service}/stats.json").json()["Teams competing"]
    assert team_count_after - team_count_before == 10

def test_admin_create_user(http_service, admin_user):
    # TODO: count users before and after
    res = admin_user.post(f"{http_service}/admin/add_user", data={
        "name": "New User 1",
        "email": "new_user@chandlerswift.com",
        "password": "password",
    }, headers={
        'referer': f"{http_service}/admin/users"
    })
    assert res.status_code == 200
    assert "User added with password " in res.text

def test_admin_create_user_with_generated_password(http_service, admin_user):
    # TODO: count users before and after
    # TODO: verify that duplicate user emails produces a sane error
    res = admin_user.post(f"{http_service}/admin/add_user", data={
        "name": "New User 2",
        "email": "new_user2@chandlerswift.com",
        "password": "",
    }, headers={
        'referer': f"{http_service}/admin/users"
    })
    assert res.status_code == 200
    assert "User added with password " in res.text

def test_admin_update_user(http_service, admin_user):
    res = admin_user.post(f"{http_service}/admin/update_user", data={
        "userid": "2",
        "name": "Existing User With New Username",
        "email": "new_username@chandlerswift.com",
        "teamid": "1",
    }, headers={
        'referer': f"{http_service}/admin/users"
    })
    assert res.status_code == 200
    assert "User new_username@chandlerswift.com updated" in res.text

def test_admin_load_teams_page(http_service, admin_user):
    res = admin_user.get(f"{http_service}/admin/teams")
    assert res.status_code == 200
    assert "Admin | Manage Teams" in res.text

def test_admin_create_team(http_service, admin_user):
    res = admin_user.post(f"{http_service}/admin/add_team", data={
        "name": "New Team",
    }, headers={
        'referer': f"{http_service}/admin/teams"
    })

    assert res.status_code == 200
    assert "<strong>Success!</strong> Team added" in res.text

def test_admin_delete_team(http_service, admin_user):
    # Since we ran test_admin_import_users_from_csv above, there should be at
    # least 10 teams. Let's delete the seventh.
    res = admin_user.post(f"{http_service}/admin/teams/7/delete", headers={
        'referer': f"{http_service}/admin/teams"
    })

    assert res.status_code == 200
    assert "Team deleted" in res.text

def test_admin_load_challenge_page(http_service, admin_user):
    res = admin_user.get(f"{http_service}/admin/challenge")
    assert "Admin | Challenge Settings" in res.text
