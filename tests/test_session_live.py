import pytest


class TestSierraSessionLive:
    """
    Test of the live Sierra API service
    """

    @pytest.mark.webtest
    def test_bib_get_success_default_fields(self, live_session):
        res = live_session.bib_get("21759599")
        assert res.status_code == 200
        assert sorted(list(res.json().keys())) == sorted(
            [
                "id",
                "updatedDate",
                "createdDate",
                "deleted",
                "suppressed",
                "isbn",
                "lang",
                "title",
                "author",
                "materialType",
                "publishYear",
                "bibLevel",
                "catalogDate",
                "country",
                "callNumber",
            ]
        )

    @pytest.mark.webtest
    def test_bib_get_404_error(self, live_session):
        res = live_session.bib_get("92345678")
        assert res.status_code == 404

    @pytest.mark.webtest
    def test_bib_get_default_response_content_marc_xml(self, live_session):
        res = live_session.bib_get_marc("21759599")
        assert res.status_code == 200
        assert res.headers["Content-Type"] == "application/marc-xml;charset=UTF-8"

    @pytest.mark.webtest
    def test_bib_get_marc_save_to_file(self, live_session):
        res = live_session.bib_get_marc("13213996")
        assert res.status_code == 200

        with open("tests/bib-marc-sample.xml", "wb") as out:
            out.write(res.content)

    @pytest.mark.webtest
    def test_bibs_query(self, live_session):
        json = {
            "target": {"record": {"type": "bib"}, "id": 30},
            "expr": {"op": "equals", "operands": ["8", ""]},
        }
        res = live_session.bibs_query(query=json)
        assert res.status_code == 200
        assert len(res.json()["entries"]) == 50

    @pytest.mark.webtest
    def test_item_get_success_default_fields(self, live_session):
        res = live_session.item_get("i389995009")
        assert res.status_code == 200
        assert res.json()["barcode"] == "33333440868293"
