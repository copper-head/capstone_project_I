

### ========= Tests for /auth/register Route ========== ###

def test_register_requires_username_and_password(client):
	r = client.post("/auth/register", json={"username": "u_only"})
	assert r.status_code == 400
	assert r.json()["detail"] == "Username and password are required"


def test_register_success_returns_user_id(client, monkeypatch):
	import backend.routers.auth as auth_router

	def fake_create_user(conn, username, password, email=None):
		assert username == "alice"
		assert password == "pw"
		assert email == "a@example.com"
		return 123

	monkeypatch.setattr(auth_router, "create_user", fake_create_user)

	r = client.post(
		"/auth/register",
		json={"username": "alice", "password": "pw", "email": "a@example.com"},
	)
	assert r.status_code == 200
	data = r.json()
	assert data["message"] == "User registered successfully"
	assert data["user_id"] == 123


def test_register_duplicate_username_or_email_returns_400(client, monkeypatch):
	import backend.routers.auth as auth_router

	def fake_create_user(_conn, _username, _password, _email=None):
		raise Exception("duplicate key value violates unique constraint")

	monkeypatch.setattr(auth_router, "create_user", fake_create_user)

	r = client.post("/auth/register", json={"username": "alice", "password": "pw"})
	assert r.status_code == 400
	assert r.json()["detail"] == "Username or email already exists"


def test_login_requires_username_and_password(client):
	r = client.post("/auth/login", json={"username": "alice"})
	assert r.status_code == 400
	assert r.json()["detail"] == "Username and password are required"


def test_login_invalid_credentials_returns_401(client, monkeypatch):
	import backend.routers.auth as auth_router

	def fake_authenticate_user(_conn, _username, _password):
		return None

	monkeypatch.setattr(auth_router, "authenticate_user", fake_authenticate_user)

	r = client.post("/auth/login", json={"username": "alice", "password": "bad"})
	assert r.status_code == 401
	assert r.json()["detail"] == "Invalid credentials"


def test_login_success_returns_user_and_token(client, monkeypatch):
	import backend.routers.auth as auth_router

	def fake_authenticate_user(_conn, username, password):
		assert username == "alice"
		assert password == "pw"
		return {"id": 1, "username": "alice", "email": "a@example.com"}

	def fake_get_token(_conn, user_id, ttl_minutes=60):
		assert user_id == 1
		assert ttl_minutes == 60
		return "tok_123"

	monkeypatch.setattr(auth_router, "authenticate_user", fake_authenticate_user)
	monkeypatch.setattr(auth_router, "get_token", fake_get_token)

	r = client.post("/auth/login", json={"username": "alice", "password": "pw"})
	assert r.status_code == 200
	data = r.json()
	assert data["message"] == "Login successful"
	assert data["user"]["username"] == "alice"
	assert data["token"] == "tok_123"