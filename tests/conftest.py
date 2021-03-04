import os.path

import pyam
import pytest
from scmdata import ScmRun

from openscm_runner.adapters import CICEROSCM, MAGICC7

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test-data")


@pytest.fixture(scope="session")
def test_data_dir():
    return TEST_DATA_DIR


@pytest.fixture(scope="session")
def test_scenarios(test_data_dir):
    scenarios = pyam.IamDataFrame(
        os.path.join(test_data_dir, "rcmip_scen_ssp_world_emissions.csv")
    )

    return scenarios


@pytest.fixture(scope="session")
def test_scenarios_2600(test_data_dir):
    scenarios = pyam.IamDataFrame(
        os.path.join(test_data_dir, "rcmip_scen_ssp_world_emissions_2600.csv")
    )

    return scenarios


@pytest.fixture(scope="session")
def test_scenario_ssp370_world(test_data_dir):
    scenario = ScmRun(
        os.path.join(
            test_data_dir, "rcmip-emissions-annual-means-v5-1-0-ssp370-world.csv"
        ),
        lowercase_cols=True,
    )

    return scenario


try:
    MAGICC_VERSION = MAGICC7.get_version()
    if MAGICC_VERSION != "v7.5.1":
        CORRECT_MAGICC_IS_AVAILABLE = False
    else:
        CORRECT_MAGICC_IS_AVAILABLE = True

except KeyError:
    MAGICC_VERSION = None
    CORRECT_MAGICC_IS_AVAILABLE = False


def pytest_runtest_setup(item):
    for mark in item.iter_markers():
        if mark.name == "magicc" and not CORRECT_MAGICC_IS_AVAILABLE:
            if MAGICC_VERSION is None:
                pytest.skip("MAGICC7 not available")
            else:
                pytest.skip(
                    "Wrong MAGICC version for tests ({})".format(MAGICC_VERSION)
                )


@pytest.fixture(scope="session")
def magicc7_is_available():
    try:
        magicc_version = MAGICC7.get_version()
        if magicc_version != "v7.4.2-23-g635c48cab":
            raise AssertionError(
                "Wrong MAGICC version for tests ({})".format(magicc_version)
            )

    except KeyError:
        pytest.skip("MAGICC7 not available")


@pytest.fixture(scope="session")
def ciceroscm_is_available():
    try:
        CICEROSCM.get_version()

    except OSError:
        pytest.skip("Cicero-SCM not available because of operating system")
    except KeyError:
        pytest.skip("Cicero-SCM not available")


def pytest_addoption(parser):
    parser.addoption(
        "--update-expected-values",
        action="store_true",
        default=False,
        help="Overwrite expected values",
    )


@pytest.fixture
def update_expected_values(request):
    return request.config.getoption("--update-expected-values")
