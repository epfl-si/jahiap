"""
    Testing the crawl.py script
"""
import os
from importlib import reload

import pytest

import crawler


JAHIA_HOST = "https://fake-jahia.epfl.ch"
JAHIA_ROOT_USER = "root"
JAHIA_ROOT_PASSWORD = "FAKE"


@pytest.fixture()
def environment(request):
    """
    Load fake environment variables for every test
    """
    os.environ["JAHIA_ROOT_PASSWORD"] = JAHIA_ROOT_PASSWORD
    os.environ["JAHIA_ROOT_USER"] = JAHIA_ROOT_USER
    os.environ["JAHIA_HOST"] = JAHIA_HOST
    reload(crawler)
    return os.environ


def delete_environment():
    """
        Delete all env. vars
    """
    del os.environ["JAHIA_ROOT_PASSWORD"]
    del os.environ["JAHIA_ROOT_USER"]
    del os.environ["JAHIA_HOST"]


class TestSetup:

    def test_required_env_password(self, environment):
        """
            Delete all env. vars and check that module raise an exception on load
        """
        delete_environment()
        with pytest.raises(SystemExit):
            reload(crawler)
            crawler.SiteCrawler.get_credentials()

    def test_default_env(self, environment):
        """
            Check default values for JAHIA _USER and _HOST
        """
        delete_environment()
        os.environ["JAHIA_ROOT_PASSWORD"] = "TEST"
        reload(crawler)
        assert crawler.HOST == 'localhost'
        assert crawler.SiteCrawler.get_credentials() == {
            'login_username': 'root',
            'login_password': "TEST",
        }

    def test_loaded_env(self, environment):
        # values have been set in os.environ by fixture
        assert crawler.HOST == JAHIA_HOST
        assert crawler.SiteCrawler.get_credentials() == {
            'login_username': JAHIA_ROOT_USER,
            'login_password': JAHIA_ROOT_PASSWORD,
        }
