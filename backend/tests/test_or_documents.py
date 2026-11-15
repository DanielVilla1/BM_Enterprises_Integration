# ===== AI GENERATED: test_or_documents =====
# Purpose: Signed OR upload, private storage and signed URLs (IT-02, POD rules)
# Inputs: fake trips, real generated images, an in-memory bucket
# Returns: pass/fail
# Flow:
# 1. Only crew upload; content is validated and metadata stripped
# 2. Objects live in the private bucket under server-made paths; no public URL
# 3. Signed URLs are short-lived and issued only after the access check

import pytest

from backend.src import providers
from backend.src.Entity.access import RoleCode
from backend.src.Repository.document_repositories import OrDocumentRepository
from backend.tests.conftest import auth_headers
from backend.tests.dispatch_support import World
from backend.tests.image_support import exif_tags, image_size, make_jpeg, make_png, png_text


@pytest.fixture
def world(client, session_factory, employees) -> World:
    return World(client, session_factory, employees)


def _upload(
    world: World, trip_id: str, actor, content: bytes, kind: str = "SIGNED_OR", filename: str = "scan.jpg"
):
    return world.client.post(
        f"/api/v1/trips/{trip_id}/or-documents",
        headers=auth_headers(actor),
        files={"file": (filename, content, "image/jpeg")},
        data={"kind": kind},
    )


def test_driver_uploads_the_signed_or_and_the_trip_awaits_company_receipt(world: World, fake_storage) -> None:
    delivered = world.delivered_trip()
    response = _upload(world, delivered.trip_id, delivered.driver, make_jpeg(), filename="my-secret-name.jpg")
    assert response.status_code == 201
    body = response.json()
    assert body["kind"] == "SIGNED_OR" and body["superseded"] is False
    assert body["content_type"] == "image/jpeg" and body["size_bytes"] > 0
    assert "storage_path" not in body and "signed-or" not in response.text
    path = next(iter(fake_storage.objects))
    assert path.startswith(f"signed-or/{delivered.trip_id}/") and path.endswith(".jpg")
    assert "my-secret-name" not in path
    trip = world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()
    assert trip["status"] == "OR_UPLOADED" and trip["or_uploaded_at"] is not None
    assert world.truck_status(delivered.truck.truck_id) == "ASSIGNED"
    assert [document["kind"] for document in trip["documents"]] == ["SIGNED_OR"]


def test_helper_may_upload_only_when_authorized(world: World, monkeypatch) -> None:
    delivered = world.delivered_trip()
    helper = delivered.helpers[0]
    assert _upload(world, delivered.trip_id, helper, make_jpeg()).status_code == 403
    enabled = providers.get_settings().model_copy(update={"helper_or_upload_enabled": True})
    monkeypatch.setattr(providers, "get_settings", lambda: enabled)
    assert _upload(world, delivered.trip_id, helper, make_jpeg()).status_code == 201


def test_only_crew_of_that_trip_can_upload(world: World) -> None:
    delivered = world.delivered_trip()
    assert _upload(world, delivered.trip_id, world.make_driver(), make_jpeg()).status_code == 404
    for actor in (world.dispatcher, world.owner, world.employees.create((RoleCode.ACCOUNTING,))):
        assert _upload(world, delivered.trip_id, actor, make_jpeg()).status_code == 403


def test_gps_and_camera_metadata_are_stripped_and_orientation_is_applied(world: World, fake_storage) -> None:
    delivered = world.delivered_trip()
    original = make_jpeg(width=40, height=20, with_metadata=True, orientation=6)
    assert 0x010F in exif_tags(original) and 0x8825 in exif_tags(original)
    assert _upload(world, delivered.trip_id, delivered.driver, original).status_code == 201
    stored, content_type = next(iter(fake_storage.objects.values()))
    assert content_type == "image/jpeg"
    assert exif_tags(stored) == {}
    assert image_size(stored) == (20, 40)


def test_png_text_chunks_are_stripped(world: World, fake_storage) -> None:
    delivered = world.delivered_trip()
    original = make_png(with_text=True)
    assert png_text(original).get("Author") == "SecretAuthorName"
    assert (
        _upload(world, delivered.trip_id, delivered.driver, original, filename="scan.png").status_code == 201
    )
    path, (stored, content_type) = next(iter(fake_storage.objects.items()))
    assert path.endswith(".png") and content_type == "image/png"
    assert "Author" not in png_text(stored)


@pytest.mark.parametrize(
    "content",
    [
        b"plain text pretending to be an image",
        b"%PDF-1.7 fake",
        b"GIF89a....",
        b"\xff\xd8\xff garbage",
        b"\x89PNG\r\n\x1a\n broken",
        b"",
    ],
)
def test_non_images_and_broken_images_are_rejected(world: World, fake_storage, content: bytes) -> None:
    delivered = world.delivered_trip()
    response = _upload(world, delivered.trip_id, delivered.driver, content)
    assert response.status_code == 422 and response.json()["code"] == "INVALID_IMAGE"
    assert fake_storage.objects == {}
    assert (
        world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()["status"]
        == "DELIVERED_OR_PENDING"
    )


def test_a_png_disguised_with_a_jpeg_name_is_judged_by_its_content(world: World) -> None:
    delivered = world.delivered_trip()
    response = _upload(world, delivered.trip_id, delivered.driver, make_png(), filename="looks-like.jpg")
    assert response.status_code == 201 and response.json()["content_type"] == "image/png"


def test_files_over_five_megabytes_are_rejected(world: World, fake_storage) -> None:
    delivered = world.delivered_trip()
    too_big = b"\xff\xd8\xff" + b"\x00" * (5 * 1024 * 1024)
    response = _upload(world, delivered.trip_id, delivered.driver, too_big)
    assert response.status_code == 413 and response.json()["code"] == "PAYLOAD_TOO_LARGE"
    assert fake_storage.objects == {}


def test_bodies_far_over_the_cap_are_refused_before_authentication(world: World) -> None:
    response = world.client.post(
        "/api/v1/trips/00000000-0000-4000-8000-000000000001/or-documents",
        content=b"x" * (7 * 1024 * 1024),
        headers={"content-type": "application/octet-stream"},
    )
    assert response.status_code == 413
    assert response.headers["content-type"].startswith("application/problem+json")


def test_uploads_need_a_delivered_trip_and_a_signed_or_before_a_stamped_copy(world: World) -> None:
    order_id = world.make_order()
    truck, (driver, helpers) = world.make_truck(), world.crew()
    trip = world.assign_ok(order_id, truck, driver, helpers)
    early = _upload(world, trip["trip_id"], driver, make_jpeg())
    assert early.status_code == 409 and early.json()["code"] == "TRIP_NOT_DELIVERED"
    delivered = world.delivered_trip()
    stamped_first = _upload(world, delivered.trip_id, delivered.driver, make_jpeg(), kind="STAMPED_COPY")
    assert stamped_first.status_code == 409 and stamped_first.json()["code"] == "SIGNED_OR_REQUIRED"
    assert _upload(world, delivered.trip_id, delivered.driver, make_jpeg(), kind="BOGUS").status_code == 422


def test_reuploading_supersedes_the_previous_file_and_keeps_history(world: World, fake_storage) -> None:
    delivered = world.delivered_trip()
    _upload(world, delivered.trip_id, delivered.driver, make_jpeg(width=40))
    _upload(world, delivered.trip_id, delivered.driver, make_jpeg(width=50))
    assert len(fake_storage.objects) == 2
    driver_view = world.get(f"/api/v1/trips/{delivered.trip_id}/or-documents", delivered.driver).json()
    assert len(driver_view) == 1 and driver_view[0]["superseded"] is False
    owner_view = world.get(f"/api/v1/trips/{delivered.trip_id}/or-documents", world.owner).json()
    assert sorted(document["superseded"] for document in owner_view) == [False, True]
    trip = world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()
    assert trip["status"] == "OR_UPLOADED" and len(trip["documents"]) == 1


def test_storage_outage_changes_nothing(world: World, fake_storage) -> None:
    delivered = world.delivered_trip()
    fake_storage.fail_put = True
    response = _upload(world, delivered.trip_id, delivered.driver, make_jpeg())
    assert response.status_code == 503 and response.json()["code"] == "STORAGE_UNAVAILABLE"
    trip = world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()
    assert trip["status"] == "DELIVERED_OR_PENDING" and trip["documents"] == []


def test_database_failure_after_storing_removes_the_orphaned_object(
    world: World, fake_storage, monkeypatch
) -> None:
    delivered = world.delivered_trip()

    def failing_add(*_arguments, **_keywords):
        raise RuntimeError("database exploded")

    monkeypatch.setattr(OrDocumentRepository, "add", failing_add)
    response = _upload(world, delivered.trip_id, delivered.driver, make_jpeg())
    assert response.status_code == 500 and "exploded" not in response.text
    assert fake_storage.objects == {} and len(fake_storage.deleted) == 1
    monkeypatch.undo()
    trip = world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()
    assert trip["status"] == "DELIVERED_OR_PENDING"


def test_signed_urls_are_short_lived_and_audited(world: World) -> None:
    delivered = world.delivered_trip()
    document = _upload(world, delivered.trip_id, delivered.driver, make_jpeg()).json()
    url_path = f"/api/v1/trips/{delivered.trip_id}/or-documents/{document['document_id']}/url"
    response = world.get(url_path, delivered.driver)
    assert response.status_code == 200
    body = response.json()
    assert body["expires_in_seconds"] == 120 and "ttl=120" in body["url"]
    audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    issued = [row for row in audit if row["action"] == "or_document.url_issued"]
    assert issued and "signed-or" not in str(issued[0]["details"])


def test_signed_url_access_follows_the_matrix(world: World) -> None:
    delivered = world.delivered_trip()
    document = _upload(world, delivered.trip_id, delivered.driver, make_jpeg()).json()
    url_path = f"/api/v1/trips/{delivered.trip_id}/or-documents/{document['document_id']}/url"
    for actor in (world.dispatcher, world.owner, world.employees.create((RoleCode.ACCOUNTING,))):
        assert world.get(url_path, actor).status_code == 200
    assert world.get(url_path, world.make_driver()).status_code == 404
    assert world.get(url_path, delivered.helpers[0]).status_code == 403
    for role in (RoleCode.FLEET_MANAGER, RoleCode.HR_PAYROLL):
        assert world.get(url_path, world.employees.create((role,))).status_code == 403


def test_documents_of_another_trip_or_unknown_ids_are_not_found(world: World) -> None:
    first = world.delivered_trip()
    second = world.delivered_trip()
    document = _upload(world, first.trip_id, first.driver, make_jpeg()).json()
    cross = f"/api/v1/trips/{second.trip_id}/or-documents/{document['document_id']}/url"
    assert world.get(cross, world.owner).status_code == 404
    unknown = f"/api/v1/trips/{first.trip_id}/or-documents/00000000-0000-4000-8000-000000000009/url"
    assert world.get(unknown, world.owner).status_code == 404


def test_storage_outage_while_signing_is_a_503(world: World, fake_storage) -> None:
    delivered = world.delivered_trip()
    document = _upload(world, delivered.trip_id, delivered.driver, make_jpeg()).json()
    fake_storage.fail_sign = True
    url_path = f"/api/v1/trips/{delivered.trip_id}/or-documents/{document['document_id']}/url"
    assert world.get(url_path, delivered.driver).status_code == 503


def test_uploads_are_audited_without_file_details(world: World) -> None:
    delivered = world.delivered_trip()
    _upload(world, delivered.trip_id, delivered.driver, make_jpeg(), filename="private-name.jpg")
    audit = world.get("/api/v1/audit-logs", world.owner)
    uploaded = [row for row in audit.json()["items"] if row["action"] == "or_document.uploaded"]
    assert uploaded and uploaded[0]["details"] == {"kind": "SIGNED_OR"}
    assert "private-name" not in audit.text
