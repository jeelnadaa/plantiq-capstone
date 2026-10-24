import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginIn, RegisterIn
from app.schemas.common import normalize_phone
from app.schemas.marketplace import ListingIn, PhotoIn, normalize_price_to_per_kg, normalize_quantity_to_kg

pytestmark = pytest.mark.unit
MID = "a" * 32


@pytest.mark.parametrize("raw,expected", [
    ("9876543210", "9876543210"), ("+91 98765 43210", "9876543210"), ("919876543210", "9876543210"),
    ("098765-43210", "9876543210"), ("98765 43210", "9876543210"),
])
def test_phone_normalisation(raw, expected):
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize("raw", ["12345", "98765432101", "abcdefghij", "", "+1 555 123 4567 89"])
def test_phone_invalid(raw):
    with pytest.raises(ValueError):
        normalize_phone(raw)


@pytest.mark.parametrize("qty,unit,kg", [
    (5, "kg", 5), (2, "ton", 2000), (1.5, "tonne", 1500), (3, "quintal", 300), (10, "bag (50kg)", 500),
    (4, "bag (60kg)", 240), (8, "25 kg sack", 200), (2, "2 ton lot", 4000), (7, "crates", 7), (0, "kg", 0),
])
def test_quantity_normalisation(qty, unit, kg):
    assert normalize_quantity_to_kg(qty, unit) == kg


@pytest.mark.parametrize("price,unit,per_kg", [
    (420, "per kg", 420), (35000, "per ton", 35), (900, "per 2 kg", 450), (9500, "per 50kg bag", 190),
    (12000, "per 60kg bag", 200), (40000, "per quintal", 400), (70000, "per 2 ton", 35), (300, "per box", 300),
])
def test_price_normalisation(price, unit, per_kg):
    assert normalize_price_to_per_kg(price, unit) == per_kg


def listing(**over):
    base = dict(title="Arabica Parchment AA", variety="Arabica SLN 795", quantity=2, quantity_unit="ton", price=420,
                price_unit="per kg", farmer_name="Ravi Gowda", phone_number="9876543210", address="Mudigere, Chikkamagaluru",
                latitude=13.21, longitude=75.64)
    base.update(over)
    return ListingIn(**base)


def test_listing_valid_resolves_units():
    item = listing()
    assert item.quantity_kg == 2000 and item.price_per_kg == 420


def test_listing_accepts_legacy_kg_fields():
    item = listing(quantity=None, quantity_unit="", quantity_kg=50, price=None, price_unit="", price_per_kg=300)
    assert item.quantity == 50 and item.quantity_unit == "kg" and item.price == 300 and item.price_unit == "per kg"


@pytest.mark.parametrize("field,value,msg", [
    ("title", "ab", "Crop title"), ("variety", "", "Variety"), ("farmer_name", " ", "Farmer name"),
    ("address", "x", "Estate address"), ("phone_number", "12345", "10 digits"), ("quantity", 0, "quantity"),
    ("price", -1, "price"), ("price", 2_000_000, "exceed"), ("quantity", 200, "100,000"),
])
def test_listing_invalid(field, value, msg):
    over = {field: value}
    if field == "quantity" and value == 200:
        over["quantity_unit"] = "ton"
    with pytest.raises(ValidationError) as exc:
        listing(**over)
    assert msg.lower() in str(exc.value).lower()


def test_listing_strips_html_brackets_and_keeps_text():
    item = listing(title="<script>alert(1)</script> Arabica & Robusta")
    assert "<" not in item.title and ">" not in item.title and "&" in item.title


def test_listing_drops_half_coordinates_and_out_of_range():
    assert listing(latitude=13.2, longitude=None).latitude is None
    assert listing(latitude=200, longitude=75).latitude is None


def test_photo_reference_rules():
    assert PhotoIn(url=f"/media/{MID}.jpg").media_id == MID
    with pytest.raises(ValidationError):
        PhotoIn(url="data:image/png;base64,AAAA")
    with pytest.raises(ValidationError):
        PhotoIn(media_id="../../etc/passwd")
    assert len(listing(photos=[{"media_id": MID, "caption": "x"}] * 8).photos) == 8
    with pytest.raises(ValidationError):
        listing(photos=[{"media_id": MID}] * 9)


def reg(**over):
    base = dict(full_name="Ravi Gowda", username="Ravi_Estate", phone="9876543210", password="Coffee2026!",
                confirm_password="Coffee2026!", accept_terms=True)
    base.update(over)
    return RegisterIn(**base)


def test_register_normalises_username_and_requires_contact():
    assert reg().username == "ravi_estate"
    with pytest.raises(ValidationError, match="mobile number or an email"):
        reg(phone=None, email=None)
    assert reg(phone=None, email="Ravi@Example.com").email == "ravi@example.com"


@pytest.mark.parametrize("over,msg", [
    ({"confirm_password": "Other2026!"}, "do not match"),
    ({"accept_terms": False}, "accept the terms"),
    ({"username": "ab"}, "Username"),
    ({"username": "bad name!"}, "Username"),
    ({"email": "not-an-email", "phone": None}, "email"),
    ({"full_name": "R"}, "Full name"),
])
def test_register_invalid(over, msg):
    with pytest.raises(ValidationError, match=msg):
        reg(**over)


def test_login_accepts_original_username_field():
    assert LoginIn(username="ravi", password="x").identifier == "ravi"
