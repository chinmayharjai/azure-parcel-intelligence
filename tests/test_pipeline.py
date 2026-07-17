from pathlib import Path

from scripts.run_demo import main
from serving.cosmos.lookup import lookup


def test_end_to_end_pipeline(tmp_path: Path):
    result = main(tmp_path / "data", parcels=25, seed=4, keep_data=False)
    assert result["control_total_status"] == "PASSED"
    assert result["cosmos_documents"] == 25
    assert result["quality"]["incident_count"] == 0
    state = lookup("PAR00000001", tmp_path / "data")
    assert state and state["partition_key"] == "PAR00000001"
