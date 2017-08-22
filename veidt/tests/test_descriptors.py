# coding: utf-8

from __future__ import division, print_function, unicode_literals, \
    absolute_import

import unittest
import os
import json

import numpy as np
import pandas as pd
from pymatgen import Structure

from veidt.descriptors import FuncGenerator, DistinctSiteProperty,  \
    MultiDescriber


class GeneratorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = np.random.rand(100, 3) * 10 - 5
        cls.df = pd.DataFrame(cls.data, columns=["x", "y", "z"])
        func_dict = {"sin": "np.sin",
                     "sum": "lambda d: d.sum(axis=1)",
                     "nest": "lambda d: np.log(np.exp(d['x']))"}
        cls.generator = FuncGenerator(func_dict=func_dict)

    def test_describe(self):
        results = self.generator.describe(self.df)
        np.testing.assert_array_equal(np.sin(self.data),
                                      results[["sin x", "sin y", "sin z"]])
        np.testing.assert_array_equal(np.sum(self.data, axis=1),
                                      results["sum"])
        np.testing.assert_array_almost_equal(self.data[:, 0],
                                             results["nest"])

    def test_serialize(self):
        json_str = json.dumps(self.generator.as_dict())
        recover = FuncGenerator.from_dict(json.loads(json_str))
        self.assert_(True)


#class DistinctSitePropertyTest(unittest.TestCase):

#    def setUp(self):
#        self.li2o = Structure.from_file(os.path.join(os.path.dirname(__file__),
#                                                     "Li2O.cif"))
#        self.na2o = Structure.from_file(os.path.join(os.path.dirname(__file__),
#                                                     "Na2O.cif"))
#        self.describer = DistinctSiteProperty(['8c', '4a'],
#                                              ["Z", "atomic_radius"])


#    def test_describe(self):
#        descriptor = self.describer.describe(self.li2o)
#        self.assertAlmostEqual(descriptor["8c-Z"], 3)
#        self.assertAlmostEqual(descriptor["8c-atomic_radius"], 1.45)
#        descriptor = self.describer.describe(self.na2o)
#        self.assertEqual(descriptor["4a-Z"], 8)
#        self.assertEqual(descriptor["4a-atomic_radius"], 0.6)

#    def test_describe_all(self):
#        df = pd.DataFrame(self.describer.describe_all([self.li2o, self.na2o]))
#        self.assertEqual(df.iloc[0]["8c-Z"], 3)
#        self.assertEqual(df.iloc[0]["8c-atomic_radius"], 1.45)


class DistinctSitePropertyTest(unittest.TestCase):

    def setUp(self):
        self.y3al5o12 = Structure.from_file(os.path.join(os.path.dirname(__file__),
                                                         "Y3Al5O12.cif"))
        self.basg = Structure.from_file(os.path.join(os.path.dirname(__file__),
                                                     "Ba3Al2Ge2SiO12.cif"))
        self.y3al5o12.add_oxidation_state_by_element({"Y": +3, "Al": +3, "O": -2})
        self.basg.add_oxidation_state_by_element({"Ba": +2, "Al": +3, "Si": +4, "Ge": +4,"O":-2})
        self.describer = DistinctSiteProperty(CNs=[6,8,4],
                                              properties=["atomic_radius","X","ionic_radius"])

    def test_describe(self):
        descriptor = self.describer.describe(self.y3al5o12,exclude_ele=['O'])
        self.assertAlmostEqual(descriptor["6-atomic_radius"], 1.25)
        self.assertAlmostEqual(descriptor["8-atomic_radius"], 1.8)
        self.assertAlmostEqual(descriptor["4-atomic_radius"], 1.25)
        self.assertAlmostEqual(descriptor["8-X"], 1.22)
        self.assertAlmostEqual(descriptor["8-ionic_radius"], 1.04)
        descriptor = self.describer.describe(self.basg,exclude_ele=['O'])
        self.assertAlmostEqual(descriptor["4-ionic_radius"],0.62666666666666671)
        self.assertAlmostEqual(descriptor["4-X"], 1.9724169529461031)

    def test_describe_all(self):
        df = pd.DataFrame(self.describer.describe_all([self.y3al5o12, self.basg]))
        self.assertEqual(df.iloc[0]["6-atomic_radius"], 1.25)
        self.assertEqual(df.iloc[1]["4-ionic_radius"], 0.62666666666666671)


#class MultiDescriberTest(unittest.TestCase):

#    def test_describe(self):
#        li2o = Structure.from_file(os.path.join(os.path.dirname(__file__),
#                                                "Li2O.cif"))
#        na2o = Structure.from_file(os.path.join(os.path.dirname(__file__),
#                                                "Na2O.cif"))
#        d1 = DistinctSiteProperty(['8c', '4a'], ["Z", "atomic_radius"])
#        d2 = FuncGenerator(func_dict={"exp": "np.exp"}, append=False)
#        d = MultiDescriber([d1, d2])

#        results = d.describe(li2o)
#        self.assertAlmostEqual(results.loc["8c-Z"]["exp"], np.exp(3))
#        self.assertAlmostEqual(results.loc["8c-atomic_radius"]["exp"],
#                               np.exp(1.45))

#        df = d.describe_all([li2o, na2o])
#        print(df)


class MultiDescriberTest(unittest.TestCase):

    def test_describe(self):
        y3al5o12 = Structure.from_file(os.path.join(os.path.dirname(__file__),
                                                         "Y3Al5O12.cif"))
        basg = Structure.from_file(os.path.join(os.path.dirname(__file__),
                                                     "Ba3Al2Ge2SiO12.cif"))
        d1 = DistinctSiteProperty(CNs=[6, 8, 4],
                             properties=["atomic_radius", "X", "ionic_radius"])
        d2 = FuncGenerator(func_dict={"exp": "np.exp"}, append=False)
        d = MultiDescriber([d1, d2])

        results = d.describe(y3al5o12)
        self.assertAlmostEqual(results.loc["6-atomic_radius"]["exp"], np.exp(1.25))
        self.assertAlmostEqual(results.loc["8-atomic_radius"]["exp"],
                               np.exp(1.8))

        df = d.describe_all([y3al5o12, basg])
        print(df)



if __name__ == "__main__":
    unittest.main()