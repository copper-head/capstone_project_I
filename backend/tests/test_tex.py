# Test cases for /tex endpoints
#
# 1. Tests for /tex/images requires auth Route
# - Test that a request without Authorization header returns 401
# - Test that a request with valid token and images returns 200 with correct data structure


from datetime import datetime


### ========= Tests for /tex/images Route ========== ###

def test_tex_images_requires_auth(client):
    r = client.get("/tex/images")
    assert r.status_code == 401


def test_list_user_images(client, fake_pg, fake_verify_token):
    # Prepare rows: id, file_path, uploaded_at, batch_id
    from datetime import datetime

    # Insert some fake images into the fake DB
    fake_pg._rows = [
        (10, "uploads/images/user_1_a.png", datetime(2025, 12, 14, 12, 0, 0), None),
        (11, "uploads/images/user_1_b.png", datetime(2025, 12, 14, 13, 0, 0), 2),
    ]

    # Call the endpoint and verify 200
    r = client.get("/tex/images", headers={"Authorization": "Bearer valid"})
    assert r.status_code == 200

    # Make sure the response data matches the fake rows
    data = r.json()
    assert data["count"] == 2
    assert len(data["images"]) == 2
    assert {img["id"] for img in data["images"]} == {10, 11}
    assert all("file_path" in img for img in data["images"])
    assert all("uploaded_at" in img for img in data["images"])

def test_list_user_images_with_batch_id(client, fake_pg, fake_verify_token):

    from datetime import datetime

    # Insert some fake images into the fake DB
    fake_pg._rows = [
        (20, "uploads/images/user_1_c.png", datetime(2025, 12, 15, 10, 0, 0), 5),
        (21, "uploads/images/user_1_d.png", datetime(2025, 12, 15, 11, 0, 0), 3)
    ]

    # Call the endpoint with batch_id filter
    r = client.get("/tex/images?batch_id=5", headers={"Authorization": "Bearer valid"})
    assert r.status_code == 200

    # Make sure the response data matches the fake rows
    data = r.json()
    assert data["count"] == 1
    assert len(data["images"]) == 1
    assert data["images"][0]["id"] == 20
    assert data["images"][0]["batch_id"] == 5

### ========= Tests for /tex/images-to-latex Route ========== ###

def test_images_to_latex_requires_auth(client):
    r = client.post("/tex/images-to-latex", json={"image_ids": [1,2]})
    assert r.status_code == 401

def test_images_to_latex_invalid_token(client, fake_verify_token):
    r = client.post(
        "/tex/images-to-latex",
        headers={"Authorization": "Bearer invalid"},
        json={"image_ids": [1,2]},
    )
    assert r.status_code == 401

def test_images_to_latex_non_list_image_ids(client, fake_verify_token):
    r = client.post(
        "/tex/images-to-latex",
        headers={"Authorization": "Bearer valid"},
        json={"image_ids": "not_a_list"},
    )
    assert r.status_code == 422

def test_images_to_latex_converts_images_to_latex(client, fake_pg, fake_verify_token, monkeypatch):
    # Provide DB rows for the requested image IDs (id, file_path)
    # Note: route orders by id, so we intentionally provide them out-of-order.
    fake_pg._rows = [
        (2, "uploads/images/user_1_img2.png"),
        (1, "uploads/images/user_1_img1.png"),
    ]

    import backend.routers.tex as tex_router

    def fake_generate(paths):
        assert paths == [
            "uploads/images/user_1_img1.png",
            "uploads/images/user_1_img2.png",
        ]
        return "\\documentclass{article}\\begin{document}OK\\end{document}"

    monkeypatch.setattr(tex_router, "generate_latex_from_images", fake_generate)

    r = client.post(
        "/tex/images-to-latex",
        headers={"Authorization": "Bearer valid"},
        json={"image_ids": [1, 2]},
    )
    assert r.status_code == 200
    assert r.headers.get("content-type") == "application/x-tex"
    assert "attachment; filename=images_includes.tex" in r.headers.get("content-disposition", "")
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
