import os
import os.path
import logging
import sys

import scmdata

try:
    from colorlog import ColoredFormatter
except ImportError as imp_exc:
    raise ImportError("pip install colorlog") from imp_exc

from openscm_runner import run

os.environ["MAGICC_WORKER_NUMBER"] = "8"

os.environ["CICEROSCM_WORKER_NUMBER"] = "8"
# os.environ["CICEROSCM_WORKER_ROOT_DIR"] = os.path.expanduser("~/Desktop/cicero-scm-workers")

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

formatter = ColoredFormatter("%(log_color)s%(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)

test_data_file = os.path.join(
    os.path.dirname(__file__),
    "..",
    "tests",
    "test-data",
    "rcmip_scen_ssp_world_emissions.csv",
)
test_scenarios = scmdata.ScmRun(test_data_file, lowercase_cols=True)

res = run(
    climate_models_cfgs={
        "CICEROSCM": [
            {
                "Index": 30040,
                "lambda": 0.540,
                "akapa": 0.341,
                "cpi": 0.556,
                "W": 1.897,
                "rlamdo": 16.618,
                "beto": 3.225,
                "mixed": 107.277,
                "dirso2_forc": -0.457,
                "indso2_forc": -0.514,
                "bc_forc": 0.200,
                "oc_forc": -0.103,
            },
            {
                "Index": 1,
                "lambda": 0.3925,
                "akapa": 0.2421,
                "cpi": 0.3745,
                "W": 0.8172,
                "rlamdo": 16.4599,
                "beto": 4.4369,
                "mixed": 35.4192,
                "dirso2_forc": -0.3428,
                "indso2_forc": -0.3856,
                "bc_forc": 0.1507,
                "oc_forc": -0.0776,
            },
        ],
        "MAGICC7": [
            {
                "core_climatesensitivity": 3,
                "rf_soxi_dir_wm2": -0.2,
                "out_temperature": 1,
                "out_forcing": 1,
                "out_dynamic_vars": [
                    "DAT_AEROSOL_ERF",
                    "DAT_HEATCONTENT_AGGREG_TOTAL",
                    "DAT_CO2_AIR2LAND_FLUX",
                ],
                "out_ascii_binary": "BINARY",
                "out_binary_format": 2,
            },
            {
                "core_climatesensitivity": 2,
                "rf_soxi_dir_wm2": -0.1,
                "out_temperature": 1,
                "out_forcing": 1,
                "out_ascii_binary": "BINARY",
                "out_binary_format": 2,
            },
            {
                "core_climatesensitivity": 5,
                "rf_soxi_dir_wm2": -0.35,
                "out_temperature": 1,
                "out_forcing": 1,
                "out_ascii_binary": "BINARY",
                "out_binary_format": 2,
            },
        ],
    },
    scenarios=test_scenarios.filter(scenario=["ssp126", "ssp245", "ssp370"]),
    output_variables=(
        "Surface Air Temperature Change",
        "Effective Radiative Forcing",
        "Effective Radiative Forcing|Aerosols",
        "Effective Radiative Forcing|CO2",
        "Heat Content|Ocean",
        # "Net Atmosphere to Land Flux|CO2",
    ),
)

print(res)
