"""
Test Project and Issues classes
"""
import pytest

from ytissues.ytlib import Project


class TestProject:
    data_displaynames = [
        (
            {"project_id": "P_ID", "shortname": "", "name": ""},
            {"name": "P_ID", "plaintext": "P_ID None None"},
        ),
        (
            {"project_id": "P_ID", "shortname": "S_NAME", "name": "NAME"},
            {"name": "S_NAME", "plaintext": "P_ID S_NAME NAME"},
        ),
        (
            {"project_id": "P_ID", "shortname": "", "name": "NAME"},
            {"name": "NAME", "plaintext": "P_ID None NAME"},
        ),
        (
            {"project_id": "", "shortname": "S_NAME", "name": "NAME"},
            {"name": "S_NAME", "plaintext": "None S_NAME NAME"},
        ),
    ]

    def test_plain_text(self):
        p = Project("P_ID", "P_SHORT", "P_NAME")
        assert p.as_plaintext() == "P_ID P_SHORT P_NAME"

    @pytest.mark.parametrize("init, result", data_displaynames)
    def test_displayname_text(self, init, result):
        p = Project(**init)
        assert p.displayname == result["name"]

    @pytest.mark.parametrize("init, result", data_displaynames)
    def test_as_plaintext(self, init, result):
        p = Project(**init)
        assert p.as_plaintext() == result["plaintext"]
