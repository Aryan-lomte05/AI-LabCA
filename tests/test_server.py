import server


def test_consult_api_shapes_and_coerces_input():
    out = server.consult({"role": "citizen", "region": "plains", "tmax": "45.6",
                          "tmax_normal": 39.8, "heat_days": 3.0, "rh": None, "symptoms": []})
    assert out["alert"] == "YELLOW" and out["input"]["heat_days"] == 3
    assert out["trace"] and out["trace"][0]["matched"]
    assert "alert" in out["how"] and out["advice"]


def test_consult_api_reports_bad_input_instead_of_crashing():
    out = server.consult({"region": "plains", "tmax": "hot", "tmax_normal": 40})
    assert out["halted_by"] and "error" in out["facts"]


def test_kb_endpoint_lists_all_rules():
    assert len(server.kb()["rules"]) == len(server.RULES)
