import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from services.provider_reliability import record_endpoint_call, validate_corporate_actions, detect_schema_drift
from models import ProviderHealthScorecard, CorporateActionValidation


@pytest.mark.asyncio
async def test_detect_schema_drift():
    # Test valid/invalid responses
    drift, msg = detect_schema_drift("polygon", "/v2/aggs", {"results": [], "ticker": "AAPL", "status": "OK"})
    assert not drift
    assert msg is None

    drift, msg = detect_schema_drift("polygon", "/v2/aggs", {"status": "OK"})
    assert drift
    assert "Missing fields" in msg

    drift, msg = detect_schema_drift("polygon", "/v2/aggs", {"results": "not-a-list", "ticker": "AAPL", "status": "OK"})
    assert drift
    assert "not a list" in msg


@pytest.mark.asyncio
async def test_record_endpoint_call_and_scorecard():
    # Mock database session
    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_res)

    mock_db = MagicMock()
    mock_db.return_value.__aenter__.return_value = mock_session
    mock_db.return_value.__aexit__.return_value = None

    with patch("services.provider_reliability.AsyncSessionLocal", mock_db):
        await record_endpoint_call(
            provider="polygon",
            endpoint="/v2/aggs",
            latency_ms=120.0,
            status_code=200,
            response_body='{"results":[]}',
            ticker="AAPL",
        )

        # Verify added to database
        assert mock_session.add.call_count >= 1
        added_objs = [call_args[0][0] for call_args in mock_session.add.call_args_list]

        # Verify scorecard added
        scorecards = [obj for obj in added_objs if isinstance(obj, ProviderHealthScorecard)]
        assert len(scorecards) == 1
        assert scorecards[0].provider == "polygon"
        assert scorecards[0].endpoint == "/v2/aggs"
        assert scorecards[0].health_score == 100.0

        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_validate_corporate_actions():
    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    mock_db = MagicMock()
    mock_db.return_value.__aenter__.return_value = mock_session
    mock_db.return_value.__aexit__.return_value = None

    with patch("services.provider_reliability.AsyncSessionLocal", mock_db):
        # Test valid
        is_valid = await validate_corporate_actions("AAPL", date(2026, 6, 6), 0.25, 0.25, "dividend")
        assert is_valid

        # Verify validation row added
        assert mock_session.add.call_count == 1
        val_obj = mock_session.add.call_args[0][0]
        assert isinstance(val_obj, CorporateActionValidation)
        assert val_obj.is_valid is True

        # Test invalid (discrepancy)
        mock_session.add.reset_mock()
        is_valid = await validate_corporate_actions("AAPL", date(2026, 6, 6), 0.25, 0.50, "dividend")
        assert not is_valid

        added_objs = [call_args[0][0] for call_args in mock_session.add.call_args_list]
        assert any(isinstance(obj, CorporateActionValidation) and obj.is_valid is False for obj in added_objs)
