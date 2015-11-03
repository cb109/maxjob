#!/usr/bin/env python
# :coding: utf-8

import os
import filecmp

import pytest

import maxjob


@pytest.fixture
def maxfound():
    """Fail early if 3dsmax.exe can not be found."""
    if not os.path.isfile(maxjob.cfg.paths.max):
        raise Exception("3dsmax not found, aborting test")
    return True


@pytest.yield_fixture
def renderscript_paths(tmpdir):
    """Yield the paths to a maxscript file and its output renderings.

    Copy the template renderscript to a temporary location so that
    its output (which is relative to the script) will also be placed
    there. Remove the temporary files after the test.

    """
    testsdir = os.path.dirname(__file__)
    templatescript = os.path.join(testsdir, "data", "render.ms")
    copiedscript = tmpdir.mkdir("maxjob").join("render.ms")
    copiedscript.write(open(templatescript).read())
    copiedscript_path = str(copiedscript)

    tempdir = os.path.dirname(copiedscript_path)
    rendering = os.path.join(tempdir, "render.png")
    expected_rendering = os.path.join(
        testsdir, "data", "expected_render.png")
    if os.path.isfile(rendering):
        os.remove(rendering)

    paths = (copiedscript_path, rendering, expected_rendering)
    yield paths

    copiedscript.remove()
    if os.path.isfile(rendering):
        os.remove(rendering)


@pytest.mark.slow
def test_renderscript(maxfound, renderscript_paths):
    """Launch max to render an image and check the resulting file."""
    renderscript, rendering, expected_rendering = renderscript_paths
    maxjob.api.main(renderscript)
    assert filecmp.cmp(rendering, expected_rendering)
