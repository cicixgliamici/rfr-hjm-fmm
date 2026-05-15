from __future__ import annotations

import pytest

from rfr_hjm_fmm.schedule import generate_regular_schedule


def test_generate_regular_schedule_quarterly() -> None:
    starts, ends, accruals = generate_regular_schedule(1.0, 4)

    assert starts == [0.0, 0.25, 0.5, 0.75]
    assert ends == [0.25, 0.5, 0.75, 1.0]
    assert accruals == [0.25, 0.25, 0.25, 0.25]


def test_generate_regular_schedule_rejects_non_positive_maturity() -> None:
    with pytest.raises(ValueError, match="maturity_years must be positive"):
        generate_regular_schedule(0.0, 4)


def test_generate_regular_schedule_rejects_non_positive_frequency() -> None:
    with pytest.raises(ValueError, match="payments_per_year must be positive"):
        generate_regular_schedule(1.0, 0)
