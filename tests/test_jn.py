# Copyright 2021 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import unittest

def run_jn(jn, timeout):

    open_jn = open(jn, "r", encoding='utf-8')
    notebook = nbformat.read(open_jn, nbformat.current_nbformat)
    open_jn.close()

    preprocessor = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
    preprocessor.allow_errors = True
    preprocessor.preprocess(notebook, {'metadata': {'path': os.path.dirname(jn)}})

    return notebook

def collect_jn_errors(nb):

    errors = []
    for cell in nb.cells:
        if 'outputs' in cell:
            for output in cell['outputs']:
                if output.output_type == 'error':
                    errors.append(output)

    return errors

def embedding_fail(error_list):
    return error_list and error_list[0].evalue == 'no embedding found'

def robust_run_jn(jn, timeout, retries):

    run_num = 1
    notebook = run_jn(jn, timeout)
    errors = collect_jn_errors(notebook)

    while embedding_fail(errors) and run_num < retries:
        run_num += 1
        notebook = run_jn(jn, timeout)
        errors = collect_jn_errors(notebook)

    return notebook, errors

def cell_text(nb, cell):
    return nb["cells"][cell]["outputs"][0]["text"]

def cell_output(nb, cell, part, data_type):
    return nb["cells"][cell]["outputs"][part][data_type]

jn_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jn_file = os.path.join(jn_dir, '01-anneal-schedule.ipynb')

class TestJupyterNotebook(unittest.TestCase):

    def test_jn(self):
        # Smoketest
        MAX_EMBEDDING_RETRIES = 3
        MAX_RUN_TIME = 400                 # Ran on my laptop in < 150 secs

        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])

        # Section Feature Availability, code cell 1
        self.assertIn("Connected to sampler", cell_text(nb, 3))

        # Section Feature Availability, code cell 2
        self.assertIn("Maximum anneal schedule points", cell_text(nb, 4))

        # Section Understanding the Anneal Schedule, code cell 1
        self.assertIn("Annealing time range", cell_text(nb, 7))

        # Section Understanding the Anneal Schedule, Subsection Pause, code cell 1
        self.assertIn("Schedule", cell_output(nb, 11, 0, "text"))

        # Section Understanding the Anneal Schedule, Subsection Quesnch, code cell 1
        self.assertIn("Schedule", cell_output(nb, 14, 0, "text"))

        # Section Understanding the Anneal Schedule, Subsection Pause & Quesnch, code cell 1
        self.assertIn("Schedule", cell_output(nb, 16, 0, "text"))

        # Section Using Anneal Schedule Features, code cell 3
        self.assertIn("QPU time used", cell_text(nb, 22))

        # Section Using Anneal Schedule Features, code cell 4
        self.assertIn("image/png", cell_output(nb, 24, 0, "data"))

        # Section Using Anneal Schedule Features, code cell 5
        self.assertIn("Ground state probability", cell_text(nb, 26))

        # Section Using Anneal Schedule Features, Subsection Using Pause, code cell 2
        self.assertIn("text/plain", cell_output(nb, 30, 0, "data"))

        # Section Using Anneal Schedule Features, Subsection Using Pause, code cell 3
        self.assertIn("Success probability", cell_output(nb, 32, 0, "text"))

        # Section Using Anneal Schedule Features, Subsection Quench, code cell 2
        self.assertIn("text/plain", cell_output(nb, 36, 0, "data"))

        # Section Using Anneal Schedule Features, Subsection Quench, code cell 3
        self.assertIn("Success probability", cell_output(nb, 38, 0, "text"))

        # Section Running the Paused Anneals on the QPU, code cell 1
        self.assertIn("Starting QPU calls", cell_text(nb, 41))

        # Section Running the Quenched Anneals on the QPU, code cell 1
        self.assertIn("Starting QPU calls", cell_text(nb, 43))
