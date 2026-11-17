"""DormMate Lab 8: API + database integration tests.
Run from the ORIGINAL DormMate root: python -m pytest -v
Uses the existing root conftest.py and isolated SQLite test DB.
"""
import itertools
import pytest

_serial = itertools.count(50000)


def student(client):
    code = f"L8-{next(_serial)}"
    response = client.post('/students', json={
        'full_name': 'Lab8 Студент', 'student_number': code,
        'faculty': 'IT', 'phone': '+77001234567',
    })
    assert response.status_code == 201, response.text
    return response.json()['id']


def room(client, capacity=2):
    response = client.post('/rooms', json={
        'building': 'LAB8', 'room_number': str(next(_serial)),
        'capacity': capacity, 'monthly_fee': 12000,
    })
    assert response.status_code == 201, response.text
    return response.json()['id']


def test_01_home(client):
    assert client.get('/').status_code == 200


def test_02_students_initially_empty(client):
    assert client.get('/students').json() == []


def test_03_create_and_get_student(client):
    sid = student(client)
    response = client.get(f'/students/{sid}')
    assert response.status_code == 200
    assert response.json()['full_name'] == 'Lab8 Студент'


def test_04_search_students(client):
    student(client)
    response = client.get('/students', params={'search': 'Lab8'})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_05_edit_student(client):
    sid = student(client)
    response = client.patch(f'/students/{sid}', json={'faculty': 'Engineering'})
    assert response.status_code == 200
    assert client.get(f'/students/{sid}').json()['faculty'] == 'Engineering'


def test_06_delete_student(client):
    sid = student(client)
    assert client.delete(f'/students/{sid}').status_code == 204
    assert client.get(f'/students/{sid}').status_code == 404


def test_07_missing_student_404(client):
    assert client.get('/students/99999999').status_code == 404


def test_08_invalid_empty_student_payload(client):
    assert client.post('/students', json={}).status_code == 422


def test_09_invalid_json(client):
    response = client.post('/students', content='{bad json', headers={'content-type': 'application/json'})
    assert response.status_code == 422


def test_10_zero_capacity_rejected(client):
    response = client.post('/rooms', json={
        'building': 'LAB8', 'room_number': '001', 'capacity': 0, 'monthly_fee': 1000,
    })
    assert response.status_code == 422


def test_11_create_get_room(client):
    rid = room(client)
    result = client.get(f'/rooms/{rid}')
    assert result.status_code == 200
    assert result.json()['available_places'] == 2


def test_12_change_room_fee(client):
    rid = room(client)
    result = client.patch(f'/rooms/{rid}', json={'monthly_fee': 13000})
    assert result.status_code == 200
    assert client.get(f'/rooms/{rid}').json()['monthly_fee'] == 13000


def test_13_delete_room(client):
    rid = room(client)
    assert client.delete(f'/rooms/{rid}').status_code == 204
    assert client.get(f'/rooms/{rid}').status_code == 404


def test_14_application_connects_student_and_room(client):
    sid, rid = student(client), room(client)
    response = client.post('/applications', json={'student_id': sid, 'room_id': rid})
    assert response.status_code == 201, response.text
    aid = response.json()['id']
    assert client.get(f'/applications/{aid}').status_code == 200


def test_15_missing_foreign_keys_rejected(client):
    result = client.post('/applications', json={'student_id': 9999999, 'room_id': 9999999})
    assert result.status_code == 404


def test_16_room_occupancy_limit(client):
    sid1, sid2, rid = student(client), student(client), room(client, capacity=1)
    first = client.post('/applications', json={'student_id': sid1, 'room_id': rid})
    assert first.status_code == 201, first.text
    aid = first.json()['id']
    assert client.patch(f'/applications/{aid}', json={'status': 'Қабылданды'}).status_code == 200
    second = client.post('/applications', json={
        'student_id': sid2, 'room_id': rid, 'status': 'Қабылданды'
    })
    assert second.status_code == 409
    assert client.get(f'/rooms/{rid}').json()['available_places'] == 0


def test_17_repeated_student_number_rejected(client):
    code = f"L8-{next(_serial)}"
    payload = {'full_name': 'Lab8 Студент', 'student_number': code,
               'faculty': 'IT', 'phone': '+77001234567'}
    assert client.post('/students', json=payload).status_code == 201
    assert client.post('/students', json=payload).status_code == 409


def test_18_method_not_allowed(client):
    # Project API documents PATCH, not PUT, for updates.
    assert client.put('/students/123', json={'faculty': 'IT'}).status_code == 405
