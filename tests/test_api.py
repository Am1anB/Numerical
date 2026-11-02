import pytest

from app import create_app
from methods import ALL_METHODS

SLUGS = [method.slug for method in ALL_METHODS]
ROOT_INPUTS = {"function": "x^2 - 2", "a": 0, "b": 2, "tolerance": 1e-6, "max_iterations": 60}


@pytest.fixture
def client(tmp_path):
    return create_app(tmp_path / "test.db").test_client()


def calculate(client, slug="bisection", inputs=ROOT_INPUTS):
    return client.post(f"/api/methods/{slug}/calculate", json=inputs)


def test_lists_five_methods(client):
    assert len(client.get("/api/methods").get_json()) == 5


@pytest.mark.parametrize("method", ALL_METHODS, ids=SLUGS)
def test_default_values_work(client, method):
    defaults = {field["name"]: field["default"] for field in method.fields}
    response = calculate(client, method.slug, defaults)
    assert response.status_code == 201
    assert response.get_json()["result"]["warning"] is None


@pytest.mark.parametrize("slug", SLUGS)
def test_method_pages(client, slug):
    assert client.get(f"/methods/{slug}").status_code == 200


def test_home_lists_every_topic(client):
    page = client.get("/").get_data(as_text=True)
    for method in ALL_METHODS:
        assert method.name in page


def test_unknown_page(client):
    assert client.get("/methods/nope").status_code == 404


def test_saved_and_read_back(client):
    created = calculate(client).get_json()
    saved = client.get(f"/api/calculations/{created['id']}").get_json()
    assert saved["inputs"] == ROOT_INPUTS
    assert saved["result"] == created["result"]


def test_history_newest_first_and_filter(client):
    first = calculate(client).get_json()["id"]
    second = calculate(client, "false-position").get_json()["id"]
    history = client.get("/api/calculations").get_json()
    assert [item["id"] for item in history] == [second, first]
    filtered = client.get("/api/calculations?method=bisection").get_json()
    assert [item["id"] for item in filtered] == [first]


def test_saved_after_restart(tmp_path):
    path = tmp_path / "keep.db"
    new_id = calculate(create_app(path).test_client()).get_json()["id"]
    assert create_app(path).test_client().get(f"/api/calculations/{new_id}").status_code == 200


def test_delete(client):
    new_id = calculate(client).get_json()["id"]
    assert client.delete(f"/api/calculations/{new_id}").status_code == 204
    assert client.get(f"/api/calculations/{new_id}").status_code == 404
    assert client.delete(f"/api/calculations/{new_id}").status_code == 404


def test_error_is_returned_and_not_saved(client):
    response = calculate(client, inputs={**ROOT_INPUTS, "a": 2, "b": 3})
    assert response.status_code == 400
    assert "same sign" in response.get_json()["error"]
    assert client.get("/api/calculations").get_json() == []


def test_unknown_method_and_bad_body(client):
    assert calculate(client, "nope").status_code == 404
    bad = client.post("/api/methods/bisection/calculate", data="not json", content_type="application/json")
    assert bad.status_code == 400
    assert client.post("/api/methods/bisection/calculate", json=[1]).status_code == 400


@pytest.mark.parametrize("limit", [0, 101])
def test_limit(client, limit):
    assert client.get(f"/api/calculations?limit={limit}").status_code == 400
