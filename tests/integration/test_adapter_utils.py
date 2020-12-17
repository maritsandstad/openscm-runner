from concurrent.futures import ProcessPoolExecutor

import numpy as np
import numpy.testing as npt

from openscm_runner.adapters.utils import _parallel_process


def _square(x):
    return x ** 2


def test_parallel():
    runs = [{"x": x} for x in range(10)]
    result = _parallel_process._parallel_process(
        func=_square,
        configuration=runs,
        pool=None,
        config_are_kwargs=True,
        front_serial=2,
        front_parallel=2,
    )
    npt.assert_array_equal(np.sort(result), np.arange(10) ** 2)

    runs2 = [x for x in range(10)]
    result2 = _parallel_process._parallel_process(
        func=_square,
        configuration=runs2,
        pool=ProcessPoolExecutor(max_workers=2),
        config_are_kwargs=False,
        front_serial=2,
        front_parallel=2,
    )
    npt.assert_array_equal(np.sort(result2), np.arange(10) ** 2)
