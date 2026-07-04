from docpilot import main


def test_package_exports_main() -> None:
    assert callable(main)
