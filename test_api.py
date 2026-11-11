"""DormMate API integration tests. Run: python -m pytest -v"""


def add_student(client, number="DM-1001"):
    return client.post("/students", json={
        "full_name": "Тест Студент", "student_number": number,
        "faculty": "IT", "phone": "+77001234567",
    })


def add_room(client, capacity=2):
    return client.post("/rooms", json={
        "building": "A", "room_number": "101", "capacity": capacity,
        "monthly_fee": 12000,
    })


def test_home_and_empty_lists(client):
    assert client.get("/").status_code == 200
    assert client.get("/students").json() == []
    assert client.get("/rooms").json() == []
    assert client.get("/applications").json() == []


def test_student_crud_and_search(client):
    response = add_student(client)
    assert response.status_code == 201, response.text
    sid = response.json()["id"]
    assert len(client.get("/students", params={"search": "Тест"}).json()) == 1
    assert client.get(f"/students/{sid}").status_code == 200
    assert client.patch(f"/students/{sid}", json={"faculty": "Design"}).json()["faculty"] == "Design"
    assert client.delete(f"/students/{sid}").status_code == 204
    assert client.get(f"/students/{sid}").status_code == 404


def test_duplicate_student_and_invalid_data(client):
    assert add_student(client).status_code == 201
    assert add_student(client).status_code == 409
    assert client.post("/rooms", json={"building": "A", "room_number": "3", "capacity": 0, "monthly_fee": 10}).status_code == 422


def test_rooms_filter_patch_delete(client):
    response = add_room(client)
    assert response.status_code == 201, response.text
    rid = response.json()["id"]
    rows = client.get("/rooms", params={"building": "A", "min_fee": 10000, "max_fee": 15000}).json()
    assert len(rows) == 1
    assert rows[0]["available_places"] == 2
    assert client.patch(f"/rooms/{rid}", json={"monthly_fee": 14000}).json()["monthly_fee"] == 14000
    assert client.delete(f"/rooms/{rid}").status_code == 204
    assert client.get(f"/rooms/{rid}").status_code == 404


def test_application_approval_occupancy_and_delete(client):
    sid = add_student(client).json()["id"]
    rid = add_room(client, capacity=1).json()["id"]
    response = client.post("/applications", json={"student_id": sid, "room_id": rid})
    assert response.status_code == 201, response.text
    aid = response.json()["id"]
    assert client.patch(f"/applications/{aid}", json={"status": "Қабылданды"}).status_code == 200
    assert client.get(f"/rooms/{rid}").json()["available_places"] == 0
    assert client.delete(f"/rooms/{rid}").status_code == 409
    assert client.delete(f"/students/{sid}").status_code == 409
    sid2 = add_student(client, "DM-1002").json()["id"]
    assert client.post("/applications", json={"student_id": sid2, "room_id": rid, "status": "Қабылданды"}).status_code == 409
    assert client.delete(f"/applications/{aid}").status_code == 204
    assert client.get(f"/rooms/{rid}").json()["available_places"] == 1


def test_missing_records_and_validation(client):
    assert client.get("/students/999").status_code == 404
    assert client.patch("/rooms/999", json={"capacity": 3}).status_code == 404
    assert client.delete("/applications/999").status_code == 404
    assert client.post("/applications", json={"student_id": 100, "room_id": 200}).status_code == 404
