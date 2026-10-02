"""Order checkout, part 2."""

from shop.checkout import calculate_order_total, validate_order


def line(
    sku: str = "SKU-1",
    qty: str = "1",
    unit_price_kopecks: str = "10000",
) -> dict[str, str]:
    """Build one order line the way the warehouse export delivers it."""
    return {
        "sku": sku,
        "qty": qty,
        "unit_price_kopecks": unit_price_kopecks,
    }


def test_smoke_single_line_without_delivery() -> None:
    assert validate_order([line()]) is None
    assert calculate_order_total([line()]) == 12_000


def test_empty_order_is_rejected() -> None:
    assert validate_order([]) is not None


def test_empty_sku_is_rejected() -> None:
    assert validate_order([line(sku="")]) is not None


def test_missing_line_key_is_rejected() -> None:
    bad_line = {"sku": "SKU-1", "qty": "1"}
    assert validate_order([bad_line]) is not None


def test_non_numeric_quantity_is_rejected() -> None:
    assert validate_order([line(qty="abc")]) is not None


def test_zero_quantity_is_rejected() -> None:
    assert validate_order([line(qty="0")]) is not None


def test_non_numeric_price_is_rejected() -> None:
    assert validate_order([line(unit_price_kopecks="abc")]) is not None


def test_negative_price_is_rejected() -> None:
    assert validate_order([line(unit_price_kopecks="-1")]) is not None


def test_duplicate_sku_is_rejected() -> None:
    assert validate_order(
        [line(), line(sku="SKU-1", qty="2")]
    ) is not None


def test_unknown_promo_code_is_rejected() -> None:
    assert validate_order(
        [line()],
        promo_code="UNKNOWN",
    ) is not None


def test_unsupported_city_is_rejected() -> None:
    assert validate_order(
        [line()],
        shipping_city="kazan",
    ) is not None


def test_valid_order_passes_validation() -> None:
    assert validate_order(
        [line(qty="2", unit_price_kopecks="5000")],
        promo_code="WELCOME10",
        shipping_city="msk",
    ) is None


def test_no_discount_below_first_tier() -> None:
    order = [line(qty="9", unit_price_kopecks="10000")]
    assert calculate_order_total(order) == 108_000


def test_tier_discount_at_first_threshold() -> None:
    order = [line(qty="10", unit_price_kopecks="1990")]
    assert calculate_order_total(order) == 22_686


def test_tier_discount_at_highest_threshold() -> None:
    order = [line(qty="50", unit_price_kopecks="1990")]
    assert calculate_order_total(order) == 101_490


def test_promo_code_beats_tier_discount() -> None:
    order = [line(qty="50", unit_price_kopecks="1990")]
    assert (
        calculate_order_total(
            order,
            promo_code="WELCOME10",
        )
        == 101_490
    )


def test_discount_is_capped_at_thirty_percent() -> None:
    order = [line(qty="100", unit_price_kopecks="10000")]
    assert (
        calculate_order_total(
            order,
            promo_code="VIP35",
            shipping_city="spb",
        )
        == 840_000
    )


def test_delivery_is_charged_for_small_order() -> None:
    order = [line(qty="1", unit_price_kopecks="10000")]
    assert calculate_order_total(
        order,
        shipping_city="msk",
    ) == 70_800


def test_free_delivery_uses_discounted_subtotal() -> None:
    order = [line(qty="50", unit_price_kopecks="10000")]
    assert calculate_order_total(
        order,
        promo_code="WELCOME10",
        shipping_city="msk",
    ) == 568_800


def test_vat_is_charged_on_the_discounted_sum() -> None:
    order = [line(qty="1", unit_price_kopecks="10000")]
    assert calculate_order_total(
        order,
        shipping_city="msk",
    ) == 70_800
