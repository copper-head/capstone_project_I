def test_tex_images_requires_auth(client):
    r = client.get("/tex/images")
    assert r.status_code == 401


def test_images_to_latex_requires_auth(client):
    r = client.post("/tex/images-to-latex", json={"image_ids": [1,2]})
    assert r.status_code == 401


def test_list_user_images_happy_path(client, fake_pg, fake_verify_token):
    # Prepare rows: id, file_path, uploaded_at, batch_id
    from datetime import datetime
    fake_pg._rows = [
        (10, "uploads/images/user_1_a.png", datetime(2025, 12, 14, 12, 0, 0), None),
        (11, "uploads/images/user_1_b.png", datetime(2025, 12, 14, 13, 0, 0), 2),
    ]

    r = client.get("/tex/images?limit=1&offset=0", headers={"Authorization": "Bearer valid"})
    assert r.status_code == 200
    data = r.json()
    # Our fake cursor returns all rows at once, but API should
    # reflect provided pagination params
    assert data["limit"] == 1
    assert data["offset"] == 0
    assert data["count"] == len(data["images"]) >= 1
    assert data["images"][0]["id"] in (10, 11)


def test_list_user_images_invalid_limit_offset(client, fake_verify_token):
    # invalid limit (>200) and negative offset should cause 422
    r1 = client.get("/tex/images?limit=1000&offset=0", headers={"Authorization": "Bearer valid"})
    assert r1.status_code == 422
    r2 = client.get("/tex/images?limit=50&offset=-1", headers={"Authorization": "Bearer valid"})
    assert r2.status_code == 422


def test_list_user_images_batch_filter(client, fake_pg, fake_verify_token):
    from datetime import datetime
    # Only rows with batch_id=2
    fake_pg._rows = [
        (21, "uploads/images/user_1_b1.png", datetime(2025, 12, 14, 14, 0, 0), 2),
        (22, "uploads/images/user_1_b2.png", datetime(2025, 12, 14, 14, 5, 0), 2),
    ]
    r = client.get("/tex/images?batch_id=2&limit=10&offset=0", headers={"Authorization": "Bearer valid"})
    assert r.status_code == 200
    data = r.json()
    assert data["batch_id"] == 2
    assert data["count"] == 2
    assert all(img["batch_id"] == 2 for img in data["images"])


def test_images_to_latex_happy_path(client, fake_pg, fake_verify_token, monkeypatch):
    # Prepare rows: id, file_path
    fake_pg._rows = [
        (5, "uploads/images/user_1_note1.png"),
        (6, "uploads/images/user_1_note2.png"),
    ]

    # Mock agent to avoid external calls and return deterministic latex
    import backend.routers.tex as tex_router

    def fake_generate(paths):
        assert paths == ["uploads/images/user_1_note1.png", "uploads/images/user_1_note2.png"]
        return "\\documentclass{article}\\begin{document}Test\\end{document}"

    monkeypatch.setattr(tex_router, "generate_latex_from_images", fake_generate)

    r = client.post(
        "/tex/images-to-latex",
        headers={"Authorization": "Bearer valid"},
        json={"image_ids": [5, 6]},
    )
    assert r.status_code == 200
    # Content-Type and attachment header
    assert r.headers.get("content-type") == "application/x-tex"
    assert "attachment; filename=images_includes.tex" in r.headers.get("content-disposition", "")
    # Body contains our fake latex
    assert b"\\documentclass{article}" in r.content


def test_images_to_latex_validation_empty_list(client, fake_verify_token):
    r = client.post(
        "/tex/images-to-latex",
        headers={"Authorization": "Bearer valid"},
        json={"image_ids": []},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "No image IDs provided"


def test_images_to_latex_404_when_no_rows(client, fake_pg, fake_verify_token):
    # No rows returned from DB
    fake_pg._rows = []
    r = client.post(
        "/tex/images-to-latex",
        headers={"Authorization": "Bearer valid"},
        json={"image_ids": [999]},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "No matching images found for user"
