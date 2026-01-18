from workedon import constants


def test_constants_have_expected_values() -> None:
    assert constants.APP_NAME == "workedon"
    assert constants.CURRENT_DB_VERSION > 0
    assert constants.WORK_CHUNK_SIZE > 0
    assert "workedon settings file" in constants.SETTINGS_HEADER
