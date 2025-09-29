import os

from fastapi.testclient import TestClient

# Payment service tests
def test_payment_create_and_qr():
    os.environ["DATABASE_URL"] = "sqlite:///./test_payment.db"
    os.environ["PUBLIC_BASE_URL"] = "http://localhost:8002"
    os.environ["PROMPTPAY_ID"] = "0916974995"
    os.environ["INTERNAL_TOKEN"] = "internal-secret"
    from services.payment.app.main import app as payment_app
    from services.payment.app.db import seed_packages

    seed_packages()
    client = TestClient(payment_app)
    # list packages
    r = client.get("/internal/packages", headers={"X-Internal-Token": "internal-secret"})
    assert r.status_code == 200
    pkgs = r.json()
    assert isinstance(pkgs, list) and len(pkgs) > 0
    pkg_id = pkgs[0]["id"]
    # create payment
    r2 = client.post("/internal/payment/create", json={"user_id": "user-1", "package_id": pkg_id}, headers={"X-Internal-Token": "internal-secret"})
    assert r2.status_code == 200
    data = r2.json()
    assert "transaction_id" in data and "qr_code_url" in data and "qr_payload" in data


def test_credit_add_and_deduct():
    os.environ["DATABASE_URL"] = "sqlite:///./test_credit.db"
    os.environ["INTERNAL_TOKEN"] = "internal-secret"
    from services.credit.app.main import app as credit_app

    client = TestClient(credit_app)
    # add
    r = client.post("/internal/credits/add", json={"user_id": "u1", "amount": 2, "reason": "test"}, headers={"X-Internal-Token": "internal-secret"})
    assert r.status_code == 200
    assert r.json()["success"] is True
    # deduct
    r2 = client.post("/internal/credits/deduct", json={"user_id": "u1", "amount": 1, "reason": "test"}, headers={"X-Internal-Token": "internal-secret"})
    assert r2.status_code == 200
    assert r2.json()["success"] is True
    # get
    r3 = client.get("/internal/credits/u1", headers={"X-Internal-Token": "internal-secret"})
    assert r3.status_code == 200
    assert r3.json()["balance"] == 1


def test_fortune_execute_with_prob_and_record():
    os.environ["DATABASE_URL"] = "sqlite:///./test_fortune.db"
    os.environ["TAROT_UPRIGHT_PROB"] = "0.0"  # force reversed
    os.environ["INTERNAL_TOKEN"] = "internal-secret"
    from services.fortune.app.main import app as fortune_app
    from services.fortune.app.db import seed_sources_and_content, SessionLocal, FortuneSource

    seed_sources_and_content()
    # set tarot source upright_prob None so default applies (0.0 => reversed)
    with SessionLocal() as db:
      src = db.query(FortuneSource).filter(FortuneSource.type == "Tarot").first()
      tarot_source_id = src.id

    client = TestClient(fortune_app)
    r = client.post("/internal/fortune/execute", json={"user_id": "u1", "source_id": tarot_source_id}, headers={"X-Internal-Token": "internal-secret"})
    assert r.status_code == 200
    data = r.json()
    assert " (Reversed)" in data["result_key"]  # due to prob 0.0

    # record
    r2 = client.post("/internal/fortune/record", json={"user_id": "u1", "source_id": tarot_source_id, "result_key": data["result_key"], "reading_date": "2024-01-01T00:00:00", "verse": data.get("verse"), "summary": data.get("summary")}, headers={"X-Internal-Token": "internal-secret"})
    assert r2.status_code == 200
    assert "fortune_history_id" in r2.json()


def test_gateway_auth_register_login():
    os.environ["DATABASE_URL"] = "sqlite:///./test_gateway.db"
    os.environ["JWT_SECRET"] = "test"
    from services.gateway.app.main import app as gateway_app

    client = TestClient(gateway_app)
    r = client.post("/auth/register", json={"email": "a@b.c", "password": "123456"})
    assert r.status_code == 200
    uid = r.json()["user_id"]
    token = r.json()["token"]
    assert token

    r2 = client.post("/auth/login", json={"email": "a@b.c", "password": "123456"})
    assert r2.status_code == 200
    assert r2.json()["user_id"] == uid