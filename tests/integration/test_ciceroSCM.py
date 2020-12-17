import os

import numpy.testing as npt
import pytest
from base import _AdapterTester
from scmdata import ScmRun

from openscm_runner import run
from openscm_runner.adapters import CICEROSCM
from openscm_runner.adapters.ciceroscm_adapter import (
    make_scenario_files,
    write_parameter_files,
)
from openscm_runner.utils import calculate_quantiles

RTOL = 1e-5


class TestCICEROSCMAdapter(_AdapterTester):
    def test_run(self, test_scenarios, ciceroscm_is_available):
        debug_run = False

        adapter = CICEROSCM()
        res = run(
            scenarios=test_scenarios.filter(scenario=["ssp126", "ssp245", "ssp370"]),
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
                ]
            },
            output_variables=(
                "Surface Temperature",
                "Surface Temperature (GMST)",
                "Heat Content|Ocean",
                "Effective Radiative Forcing",
                "Effective Radiative Forcing|Anthropogenic",
                "Effective Radiative Forcing|Aerosols",
                "Effective Radiative Forcing|Greenhouse Gases",
                "Heat Uptake",
                "Atmospheric Concentrations|CO2",
                "Emissions|CO2",
            ),
            out_config=None,
        )
        assert isinstance(res, ScmRun)
        assert res["run_id"].min() == 1
        assert res["run_id"].max() == 30040
        assert res.get_unique_meta("climate_model", no_duplicates=True) == "Cicero-SCM"

        assert set(res.get_unique_meta("variable")) == set(
            [
                "Surface Temperature",
                "Surface Temperature (GMST)",
                "Heat Content|Ocean",
                "Effective Radiative Forcing",
                "Effective Radiative Forcing|Anthropogenic",
                "Effective Radiative Forcing|Aerosols",
                "Effective Radiative Forcing|Greenhouse Gases",
                "Heat Uptake",
                "Atmospheric Concentrations|CO2",
                "Emissions|CO2",
            ]
        )

        # check ocean heat content unit conversion comes through correctly
        self._check_res(
            904.474,
            res.filter(
                unit="ZJ",
                variable="Heat Content|Ocean",
                region="World",
                year=2100,
                scenario="ssp126",
            ).values.max(),
            not debug_run,
        )

        self._check_res(
            1.50177,
            res.filter(
                variable="Surface Temperature",
                region="World",
                year=2100,
                scenario="ssp126",
            ).values.max(),
            not debug_run,
        )

        self._check_res(
            3.35742,
            res.filter(
                variable="Surface Temperature (GMST)",
                region="World",
                year=2100,
                scenario="ssp370",
            ).values.max(),
            not debug_run,
        )
        self._check_res(
            -2.5292859114958564,
            res.filter(
                unit="ZJ/yr",
                variable="Heat Uptake",
                region="World",
                year=2100,
                scenario="ssp126",
            ).values.max(),
            not debug_run,
        )
        self._check_res(
            780.2869999999999,
            res.filter(
                variable="Atmospheric Concentrations|CO2",
                region="World",
                year=2100,
                scenario="ssp370",
            ).values.max(),
            not debug_run,
        )
        self._check_res(
            22.5616,
            res.filter(
                variable="Emissions|CO2", region="World", year=2100, scenario="ssp370",
            ).values.max(),
            not debug_run,
        )
        # check we can also calcluate quantiles
        quantiles = calculate_quantiles(res, [0.05, 0.17, 0.5, 0.83, 0.95])

        self._check_res(
            1.1427785,
            quantiles.filter(
                variable="Surface Temperature (GMST)",
                region="World",
                year=2100,
                scenario="ssp126",
                quantile=0.05,
            ).values,
            not debug_run,
        )

        self._check_res(
            1.4757515,
            quantiles.filter(
                variable="Surface Temperature (GMST)",
                region="World",
                year=2100,
                scenario="ssp126",
                quantile=0.95,
            ).values,
            not debug_run,
        )

        self._check_res(
            2.7883605,
            quantiles.filter(
                variable="Surface Temperature (GMST)",
                region="World",
                year=2100,
                scenario="ssp370",
                quantile=0.05,
            ).values,
            not debug_run,
        )

        self._check_res(
            3.3274695,
            quantiles.filter(
                variable="Surface Temperature (GMST)",
                region="World",
                year=2100,
                scenario="ssp370",
                quantile=0.95,
            ).values,
            not debug_run,
        )
        if debug_run:
            assert False, "Turn off debug"

    def test_variable_naming(self, test_scenarios, ciceroscm_is_available):
        missing_from_ciceroscm = (
            "Effective Radiative Forcing|Aerosols|Direct Effect|BC|MAGICC AFOLU",
            "Effective Radiative Forcing|Aerosols|Direct Effect|BC|MAGICC Fossil and Industrial",
            "Effective Radiative Forcing|Aerosols|Direct Effect|OC|MAGICC AFOLU",
            "Effective Radiative Forcing|Aerosols|Direct Effect|OC|MAGICC Fossil and Industrial",
            "Effective Radiative Forcing|Aerosols|Direct Effect|SOx|MAGICC AFOLU",
            "Effective Radiative Forcing|Aerosols|Direct Effect|SOx|MAGICC Fossil and Industrial",
            "Net Atmosphere to Ocean Flux|CO2",
            "Net Atmosphere to Land Flux|CO2",
        )
        common_variables = [
            c for c in self._common_variables if c not in missing_from_ciceroscm
        ]
        res = run(
            climate_models_cfgs={"CICEROSCM": ({"lambda": 0.540},)},
            scenarios=test_scenarios.filter(scenario="ssp126"),
            output_variables=common_variables,
        )

        missing_vars = set(common_variables) - set(res["variable"])
        if missing_vars:
            raise AssertionError(missing_vars)

    def test_w_out_config(self, test_scenarios, ciceroscm_is_available):
        with pytest.raises(NotImplementedError):
            run(
                scenarios=test_scenarios.filter(scenario=["ssp126"]),
                climate_models_cfgs={
                    "CiceroSCM": [
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
                    ]
                },
                output_variables=("Surface Temperature",),
                out_config={"CiceroSCM": ("With ECS",)},
            )

    def test_make_scenario_files(self, test_scenarios):
        npt.assert_string_equal(
            make_scenario_files.unit_name_converter("Mt C/yr"), "Tg C/yr"
        )
        npt.assert_string_equal(make_scenario_files.unit_name_converter("kt N2O"), "Gg N2O")
        npt.assert_string_equal(
            make_scenario_files.unit_name_converter("Gt tests"), "Pg tests"
        )
        npt.assert_string_equal(make_scenario_files.unit_name_converter("Test"), "Test")

        self._check_res(
            3.0 / 11 * 1000.0,
            make_scenario_files.unit_conv_factor("Mg_C", "Gg CO2/yr", "CO2_lu"),
            False,
        )
        self._check_res(
            0.636 / 1.0e12,
            make_scenario_files.unit_conv_factor("Pg_N", "kg N2O/yr", "N2O"),
            False,
        )
        self._check_res(
            0.304 / 1.0e12,
            make_scenario_files.unit_conv_factor("Pt_N", "kt NOx/yr", "NOx"),
            False,
        )
        self._check_res(
            0.501,
            make_scenario_files.unit_conv_factor("Tg_S", "Tg SO2/yr", "SO2"),
            False,
        )


    @pytest.mark.parametrize(
        "input,exp",
        (
            ("folder", ("folder",)),
            (os.path.join("folder", "subfolder"), ("folder", "subfolder")),
        ),
    )
    def test_write_parameter_files(self, input, exp):
        assert write_parameter_files.splitall(input) == exp


def test_get_version(ciceroscm_is_available):
    assert CICEROSCM.get_version() == "v2019vCH4"
