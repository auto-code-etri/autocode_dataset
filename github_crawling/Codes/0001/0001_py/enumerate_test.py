# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Tests for `tf.data.Dataset.enumerate()`."""
from absl.testing import parameterized

from tensorflow.python.data.kernel_tests import checkpoint_test_base
from tensorflow.python.data.kernel_tests import test_base
from tensorflow.python.data.ops import dataset_ops
from tensorflow.python.data.ops import options as options_lib
from tensorflow.python.framework import combinations
from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import tensor_shape
from tensorflow.python.platform import test


class EnumerateTest(test_base.DatasetTestBase, parameterized.TestCase):

  @combinations.generate(test_base.default_test_combinations())
  def testEnumerate(self):
    components = (["a", "b"], [1, 2], [37.0, 38])
    start = constant_op.constant(20, dtype=dtypes.int64)

    dataset = dataset_ops.Dataset.from_tensor_slices(components).enumerate(
        start)

    self.assertEqual(dtypes.int64,
                     dataset_ops.get_legacy_output_types(dataset)[0])
    dataset_output_shapes = dataset_ops.get_legacy_output_shapes(dataset)
    self.assertEqual((), dataset_output_shapes[0])
    self.assertEqual([tensor_shape.TensorShape([])] * 3,
                     [shape for shape in dataset_output_shapes[1]])

    self.assertDatasetProduces(dataset, [(20, (b"a", 1, 37.0)),
                                         (21, (b"b", 2, 38.0))])


class EnumerateCheckpointTest(checkpoint_test_base.CheckpointTestBase,
                              parameterized.TestCase):

  def _build_enumerate_dataset(self, start, stop, options=None):
    dataset = dataset_ops.Dataset.range(start, stop).enumerate()
    if options:
      dataset = dataset.with_options(options)
    return dataset

  @combinations.generate(
      combinations.times(
          test_base.default_test_combinations(),
          checkpoint_test_base.default_test_combinations(),
          combinations.combine(symbolic_checkpoint=[False, True])))
  def test(self, verify_fn, symbolic_checkpoint):
    start = 2
    stop = 10
    options = options_lib.Options()
    options.experimental_symbolic_checkpoint = symbolic_checkpoint
    verify_fn(
        self, lambda: self._build_enumerate_dataset(
            start=start, stop=stop, options=options), stop - start)


if __name__ == "__main__":
  test.main()
