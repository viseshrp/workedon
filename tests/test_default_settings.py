from workedon import default_settings


def test_default_settings_are_sane() -> None:
    assert isinstance(default_settings.DATE_FORMAT, str)
    assert isinstance(default_settings.TIME_FORMAT, str)
    assert default_settings.DATETIME_FORMAT == ""
    assert isinstance(default_settings.TIME_ZONE, str)
    assert default_settings.TIME_ZONE
    assert default_settings.DURATION_UNIT == "minutes"
