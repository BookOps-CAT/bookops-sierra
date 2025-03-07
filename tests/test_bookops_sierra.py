# -*- coding: utf-8 -*-

from bookops_sierra import __version__, __title__


def test_version():
    assert __version__ == "0.1.0"


def test_title():
    assert __title__ == "bookops-sierra"


def test_SierraToken_top_level_import():
    from bookops_sierra import SierraToken  # noqa: F401


def test_PlatformSession_top_level_import():
    from bookops_sierra import SierraSession  # noqa: F401


def test_BookopsPlatformError_top_level_import():
    from bookops_sierra import BookopsSierraError  # noqa: 401
