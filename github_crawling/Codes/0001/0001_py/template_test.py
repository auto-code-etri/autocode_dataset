# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
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
"""Tests for make_template."""
import functools
import traceback

from tensorflow.python.client import session
from tensorflow.python.eager import context
from tensorflow.python.framework import ops
from tensorflow.python.framework import random_seed
from tensorflow.python.framework import test_util
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import init_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import template
from tensorflow.python.ops import variable_scope
from tensorflow.python.ops import variables
import tensorflow.python.ops.nn_grad  # pylint: disable=unused-import
from tensorflow.python.platform import test
from tensorflow.python.training import gradient_descent


def variable_scoped_function(trainable=True):
  return variable_scope.get_variable(
      "dummy", shape=[1], trainable=trainable,
      initializer=init_ops.zeros_initializer())


def internally_variable_scoped_function(scope_name):
  with variable_scope.variable_scope(scope_name):
    return variable_scope.get_variable(
        "dummy", shape=[1], initializer=init_ops.zeros_initializer())


def function_with_create(trainable):
  """Creates a variable as a side effect using tf.Variable."""
  variables.Variable(0, trainable=trainable)
  return variable_scope.get_variable(
      "dummy", shape=[1], initializer=init_ops.zeros_initializer())


def function_with_side_create(trainable, name="side"):
  """Creates a variable as a side effect using tf.get_variable."""
  variable_scope.get_variable(name, shape=[1], trainable=trainable)
  return variable_scope.get_variable(
      "dummy", shape=[1], initializer=init_ops.zeros_initializer())


def variable_scoped_function_with_local_variable():
  variable_scope.get_local_variable(
      "local", shape=[1], initializer=init_ops.zeros_initializer())
  return variable_scope.get_variable(
      "dummy", shape=[1], initializer=init_ops.zeros_initializer())


class TemplateTest(test.TestCase):

  @test_util.run_deprecated_v1
  def test_end_to_end(self):
    """This test shows a very simple line model with test_loss.

    The template is used to share parameters between a training and test model.
    """
    # y = 2x + 1
    training_input, training_output = ([1., 2., 3., 4.], [2.8, 5.1, 7.2, 8.7])
    test_input, test_output = ([5., 6., 7., 8.], [11, 13, 15, 17])

    random_seed.set_random_seed(1234)

    def test_line(x):
      m = variable_scope.get_variable(
          "w", shape=[], initializer=init_ops.truncated_normal_initializer())
      b = variable_scope.get_variable(
          "b", shape=[], initializer=init_ops.truncated_normal_initializer())
      return x * m + b

    line_template = template.make_template("line", test_line)

    train_prediction = line_template(training_input)
    test_prediction = line_template(test_input)

    train_loss = math_ops.reduce_mean(
        math_ops.square(train_prediction - training_output))
    test_loss = math_ops.reduce_mean(
        math_ops.square(test_prediction - test_output))

    optimizer = gradient_descent.GradientDescentOptimizer(0.1)
    train_op = optimizer.minimize(train_loss)

    with session.Session() as sess:
      self.evaluate(variables.global_variables_initializer())
      initial_test_loss = self.evaluate(test_loss)
      self.evaluate(train_op)
      final_test_loss = self.evaluate(test_loss)

    # Parameters are tied, so the loss should have gone down when we trained it.
    self.assertLess(final_test_loss, initial_test_loss)

  def test_end_to_end_eager(self):
    """This test shows a very simple line model with test_loss in eager mode.

    The template is used to share parameters between a training and test model.
    """
    with context.eager_mode():
      # y = 2x + 1
      training_input, training_output = ([1., 2., 3., 4.], [2.8, 5.1, 7.2, 8.7])
      test_input, test_output = ([5., 6., 7., 8.], [11, 13, 15, 17])

      random_seed.set_random_seed(1234)

      def test_line(x):
        m = variable_scope.get_variable(
            "w", shape=[], initializer=init_ops.truncated_normal_initializer())
        b = variable_scope.get_variable(
            "b", shape=[], initializer=init_ops.truncated_normal_initializer())
        return x * m + b

      line_template = template.make_template("line", test_line)

      def train_loss():
        train_prediction = line_template(training_input)
        return math_ops.reduce_mean(
            math_ops.square(train_prediction - training_output))

      def test_loss():
        test_prediction = line_template(test_input)
        return math_ops.reduce_mean(
            math_ops.square(test_prediction - test_output))

      optimizer = gradient_descent.GradientDescentOptimizer(0.1)
      initial_test_loss = test_loss()
      optimizer.minimize(train_loss)
      final_test_loss = test_loss()

      # Parameters are tied, so the loss should have gone down after training.
      self.assertLess(final_test_loss.numpy(), initial_test_loss.numpy())

  def test_eager_delayed_store_pickup(self):
    """This test shows a very simple line model with test_loss in eager mode.

    The template is used to share parameters between a training and test model.

    This test also shows that it can pick up explicitly set variable stores
    even if they are only set before the first template usage.
    """
    with context.eager_mode():
      training_input, training_output = ([1., 2., 3., 4.], [2.8, 5.1, 7.2, 8.7])
      test_input, test_output = ([5., 6., 7., 8.], [11, 13, 15, 17])

      random_seed.set_random_seed(1234)

      def test_line(x):
        m = variable_scope.get_variable(
            "w", shape=[], initializer=init_ops.truncated_normal_initializer())
        b = variable_scope.get_variable(
            "b", shape=[], initializer=init_ops.truncated_normal_initializer())
        return x * m + b

      line_template = template.make_template("line", test_line)

      def train_loss():
        train_prediction = line_template(training_input)
        return math_ops.reduce_mean(
            math_ops.square(train_prediction - training_output))

      def test_loss():
        test_prediction = line_template(test_input)
        return math_ops.reduce_mean(
            math_ops.square(test_prediction - test_output))

      store = variable_scope._VariableStore()
      store._store_eager_variables = True

      with variable_scope.with_variable_store(store):
        optimizer = gradient_descent.GradientDescentOptimizer(0.1)
        initial_test_loss = test_loss()
        optimizer.minimize(train_loss)
        final_test_loss = test_loss()

        # Parameters are tied, so the loss should have gone down after training.
        self.assertLess(final_test_loss.numpy(), initial_test_loss.numpy())

      # Verify that the explicitly set store is not empty
      # and the make_template picked it up
      self.assertEqual(set(store._vars.keys()), {"line/w", "line/b"})

      # But the store should only get picked up once, so a second
      # store will go unused:
      second_store = variable_scope._VariableStore()
      second_store._store_eager_variables = True

      with variable_scope.with_variable_store(second_store):
        optimizer = gradient_descent.GradientDescentOptimizer(0.1)
        test_loss()
        optimizer.minimize(train_loss)
        test_loss()
      self.assertEmpty(second_store._vars)

  @test_util.run_in_graph_and_eager_modes
  def test_skip_stack_frames(self):
    first = traceback.format_stack()
    second = traceback.format_stack()
    result = template._skip_common_stack_elements(first, second)
    self.assertEqual(1, len(result))
    self.assertNotEqual(len(first), len(result))

  @test_util.run_in_graph_and_eager_modes
  def test_template_with_empty_name(self):
    tpl = template.make_template("", variable_scoped_function)
    with variable_scope.variable_scope("outer"):
      x = variable_scope.get_variable("x", [])
      v = tpl()
    self.assertEqual("outer/", tpl.variable_scope_name)
    self.assertEqual("outer//dummy:0", v.name)
    if context.executing_eagerly():
      # In eager mode `x` is not visible to the template since the template does
      # not rely on global collections.
      self.assertEqual(1, len(tpl.variables))
      self.assertIs(v, tpl.variables[0])
    else:
      self.assertEqual([x, v], tpl.variables)

  @test_util.run_in_graph_and_eager_modes
  def test_template_with_name(self):
    tmpl1 = template.make_template("s1", variable_scoped_function)
    tmpl2 = template.make_template("s1", variable_scoped_function)

    v1 = tmpl1()
    v2 = tmpl1()
    v3 = tmpl2()
    self.assertIs(v1, v2)
    self.assertIsNot(v1, v3)
    self.assertEqual("s1/dummy:0", v1.name)
    self.assertEqual("s1_1/dummy:0", v3.name)

  @test_util.run_deprecated_v1
  def test_same_unique_name_raise_error(self):
    tmpl1 = template.make_template(
        "_", variable_scoped_function, unique_name_="s1")
    tmpl1()
    tmpl2 = template.make_template(
        "_", variable_scoped_function, unique_name_="s1")
    with self.assertRaisesRegex(
        ValueError, "Variable s1/dummy already exists, disallowed.*"):
      tmpl2()

  def test_unique_name_raise_error_in_eager(self):
    with context.eager_mode():
      with self.assertRaisesRegex(
          ValueError,
          "unique_name_ cannot be used when eager execution is enabled."):
        template.make_template(
            "_", variable_scoped_function, unique_name_="s1")

  @test_util.run_deprecated_v1
  def test_unique_name_and_reuse(self):
    tmpl1 = template.make_template(
        "_", variable_scoped_function, unique_name_="s1")
    v1 = tmpl1()
    v2 = tmpl1()

    variable_scope.get_variable_scope().reuse_variables()
    tmpl2 = template.make_template(
        "_", variable_scoped_function, unique_name_="s1")
    v3 = tmpl2()

    self.assertIs(v1, v2)
    self.assertIs(v1, v3)
    self.assertEqual("s1/dummy:0", v1.name)

  @test_util.run_in_graph_and_eager_modes
  def test_template_in_scope(self):
    tmpl1 = template.make_template("s1", variable_scoped_function)
    tmpl2 = template.make_template("s1", variable_scoped_function)

    with variable_scope.variable_scope("scope"):
      v1 = tmpl1()
      v3 = tmpl2()

    # The template contract requires the following to ignore scope2.
    with variable_scope.variable_scope("scope2"):
      v2 = tmpl1()
    self.assertIs(v1, v2)
    self.assertIsNot(v1, v3)
    self.assertEqual("scope/s1/dummy:0", v1.name)
    self.assertEqual("scope/s1_1/dummy:0", v3.name)

  @test_util.run_in_graph_and_eager_modes
  def test_template_with_internal_reuse(self):
    tmpl1 = template.make_template("s1", internally_variable_scoped_function)
    tmpl2 = template.make_template("s1", internally_variable_scoped_function)

    v1 = tmpl1("test")
    v2 = tmpl1("test")
    v3 = tmpl2("test")
    self.assertIs(v1, v2)
    self.assertIsNot(v1, v3)
    self.assertEqual("s1/test/dummy:0", v1.name)
    self.assertEqual("s1_1/test/dummy:0", v3.name)

    with self.assertRaises(ValueError):
      tmpl1("not_test")

  @test_util.run_in_graph_and_eager_modes
  def test_template_without_name(self):
    with self.assertRaisesRegex(ValueError, "name cannot be None."):
      template.make_template(None, variable_scoped_function)

  @test_util.run_in_graph_and_eager_modes
  def test_make_template(self):
    # Test both that we can call it with positional and keywords.
    tmpl1 = template.make_template(
        "s1", internally_variable_scoped_function, scope_name="test")
    tmpl2 = template.make_template(
        "s1", internally_variable_scoped_function, scope_name="test")

    v1 = tmpl1()
    v2 = tmpl1()
    v3 = tmpl2()
    self.assertIs(v1, v2)
    self.assertIsNot(v1, v3)
    self.assertEqual("s1/test/dummy:0", v1.name)
    self.assertEqual("s1_1/test/dummy:0", v3.name)

  @test_util.run_deprecated_v1
  def test_enforces_no_extra_trainable_variables(self):
    tmpl = template.make_template("s", function_with_create, trainable=True)

    tmpl()
    with self.assertRaises(ValueError):
      tmpl()

  @test_util.run_in_graph_and_eager_modes
  def test_enforces_no_extra_trainable_variables_eager(self):
    tmpl = template.make_template("s",
                                  function_with_side_create,
                                  trainable=True)

    tmpl(name="1")
    with self.assertRaises(ValueError):
      tmpl(name="2")

  def test_permits_extra_non_trainable_variables(self):
    tmpl = template.make_template("s", function_with_create, trainable=False)
    self.assertIs(tmpl(), tmpl())

  def test_permits_extra_non_trainable_variables_eager(self):
    with context.eager_mode():
      tmpl = template.make_template("s",
                                    function_with_side_create,
                                    trainable=False)
      self.assertIs(tmpl(name="1"), tmpl(name="2"))

  @test_util.run_in_graph_and_eager_modes
  def test_internal_variable_reuse(self):

    def nested():
      with variable_scope.variable_scope("nested") as vs:
        v1 = variable_scope.get_variable(
            "x", initializer=init_ops.zeros_initializer(), shape=[])
      with variable_scope.variable_scope(vs, reuse=True):
        v2 = variable_scope.get_variable("x")
      self.assertIs(v1, v2)
      return v1

    tmpl1 = template.make_template("s1", nested)
    tmpl2 = template.make_template("s1", nested)

    v1 = tmpl1()
    v2 = tmpl1()
    v3 = tmpl2()
    self.assertIs(v1, v2)
    self.assertIsNot(v1, v3)
    self.assertEqual("s1/nested/x:0", v1.name)
    self.assertEqual("s1_1/nested/x:0", v3.name)

  @test_util.run_in_graph_and_eager_modes
  def test_nested_templates(self):

    def nested_template():
      nested1 = template.make_template("nested", variable_scoped_function)
      nested2 = template.make_template("nested", variable_scoped_function)
      v1 = nested1()
      v2 = nested2()

      # nested1 and nested2 should not share variables
      self.assertIsNot(v1, v2)

      # Variables created by nested1 should be isolated from variables
      # created by nested2.
      self.assertEqual(1, len(nested1.variables))
      self.assertEqual(1, len(nested2.variables))
      self.assertIs(nested1.variables[0], v1)
      self.assertIs(nested2.variables[0], v2)
      self.assertEqual(1, len(nested1.trainable_variables))
      self.assertEqual(1, len(nested2.trainable_variables))
      self.assertIs(nested1.trainable_variables[0], v1)
      self.assertIs(nested2.trainable_variables[0], v2)
      self.assertEqual(len(nested1.non_trainable_variables), 0)
      self.assertEqual(len(nested2.non_trainable_variables), 0)
      return v1, v2

    tmpl1 = template.make_template("s1", nested_template)
    tmpl2 = template.make_template("s1", nested_template)

    v1, v2 = tmpl1()
    v3, v4 = tmpl1()
    v5, v6 = tmpl2()

    # The second invocation of tmpl1 should reuse the variables
    # created in the first invocation.
    self.assertIs(v1, v3)
    self.assertIs(v2, v4)
    for v, w in zip(tmpl1.variables, [v1, v2]):
      self.assertIs(v, w)
    for v, w in zip(tmpl1.trainable_variables, [v1, v2]):
      self.assertIs(v, w)
    self.assertEqual(len(tmpl1.non_trainable_variables), 0)

    # tmpl1 and tmpl2 should not share variables.
    self.assertIsNot(v1, v5)
    self.assertIsNot(v2, v6)
    for v, w in zip(tmpl2.variables, [v5, v6]):
      self.assertIs(v, w)
    for v, w in zip(tmpl2.trainable_variables, [v5, v6]):
      self.assertIs(v, w)
    self.assertEqual(len(tmpl2.non_trainable_variables), 0)
    self.assertEqual("s1/nested/dummy:0", v1.name)
    self.assertEqual("s1/nested_1/dummy:0", v2.name)
    self.assertEqual("s1_1/nested/dummy:0", v5.name)
    self.assertEqual("s1_1/nested_1/dummy:0", v6.name)

    self.assertEqual(["nested", "nested_1"], list(tmpl1._trackable_children()))

  def test_graph_function_no_name(self):
    with context.eager_mode():

      def f(_, y):
        return y + 1

      partial = functools.partial(f, 1.0)
      tmpl = template.make_template_internal(
          "a", partial, create_graph_function_=True)
      self.assertAllEqual(tmpl(ops.convert_to_tensor(1.0)), 2.0)

  @test_util.run_in_graph_and_eager_modes
  def test_immediate_scope_creation(self):
    # Create templates in scope a then call in scope b. make_template should
    # capture the scope the first time it is called, and make_immediate_template
    # should capture the scope at construction time.
    with variable_scope.variable_scope("ctor_scope"):
      # Create scope here:
      tmpl_immed = template.make_template("a", variable_scoped_function,
                                          True)
      # default: create scope at __call__
      tmpl_defer = template.make_template(
          "b", variable_scoped_function, False)
    with variable_scope.variable_scope("call_scope"):
      inner_imm_var = tmpl_immed()
      inner_defer_var = tmpl_defer()
    outer_imm_var = tmpl_immed()
    outer_defer_var = tmpl_defer()

    self.assertIsNot(inner_imm_var, inner_defer_var)
    self.assertIs(outer_imm_var, inner_imm_var)
    self.assertIs(outer_defer_var, inner_defer_var)

    self.assertEqual("ctor_scope/a/dummy:0", inner_imm_var.name)
    self.assertEqual("call_scope/b/dummy:0", inner_defer_var.name)

  @test_util.run_in_graph_and_eager_modes
  def test_scope_access(self):
    # Ensure that we can access the scope inside the template, because the name
    # of that scope may be different from the name we pass to make_template, due
    # to having been made unique by variable_scope.
    with variable_scope.variable_scope("foo"):
      # Create two templates with the same name, ensure scopes are made unique.
      ta = template.make_template("bar", variable_scoped_function, True)
      tb = template.make_template("bar", variable_scoped_function, True)

    # Ensure we can get the scopes before either template is actually called.
    self.assertEqual(ta.variable_scope.name, "foo/bar")
    self.assertEqual(tb.variable_scope.name, "foo/bar_1")

    with variable_scope.variable_scope("foo_2"):
      # Create a template which defers scope creation.
      tc = template.make_template("blah", variable_scoped_function, False)

    # Before we call the template, the scope property will be set to None.
    self.assertEqual(tc.variable_scope, None)
    tc()

    # Template is called at the top level, so there is no preceding "foo_2".
    self.assertEqual(tc.variable_scope.name, "blah")

  @test_util.run_in_graph_and_eager_modes
  def test_custom_getter(self):
    # Custom getter that maintains call count and forwards to true getter
    custom_getter_count = [0]

    def custom_getter(getter, name, *args, **kwargs):
      custom_getter_count[0] += 1
      return getter(name, *args, **kwargs)

    # Test that custom getter is called both when variables are created and
    # subsequently accessed
    tmpl1 = template.make_template(
        "s1", variable_scoped_function, custom_getter_=custom_getter)
    self.assertEqual(custom_getter_count[0], 0)
    tmpl1()
    self.assertEqual(custom_getter_count[0], 1)
    tmpl1()
    self.assertEqual(custom_getter_count[0], 2)

    # Test that custom getter is called when the variable scope is created
    # during construction
    custom_getter_count[0] = 0
    tmpl2 = template.make_template(
        "s2",
        variable_scoped_function,
        custom_getter_=custom_getter,
        create_scope_now_=True)
    self.assertEqual(custom_getter_count[0], 0)
    tmpl2()
    self.assertEqual(custom_getter_count[0], 1)
    tmpl2()
    self.assertEqual(custom_getter_count[0], 2)

  @test_util.run_in_graph_and_eager_modes
  def test_fails_gracefully(self):
    for create_scope_now in [True, False]:
      def module_function_with_one_arg(inputs):
        w = variable_scope.get_variable(
            "w", shape=[1], initializer=init_ops.zeros_initializer())
        return inputs * w

      templatized_function = template.make_template(
          "f1", module_function_with_one_arg,
          create_scope_now_=create_scope_now)
      data = array_ops.zeros([1])
      try:
        # Try to connect with a kwarg which is unsupported.
        templatized_function(data, is_training=True)
      except TypeError:
        pass

      # The failed __call__ hasn't modified the inner state.
      self.assertFalse(templatized_function._variables_created)
      templatized_function(data)
      self.assertTrue(templatized_function._variables_created)

  @test_util.run_in_graph_and_eager_modes
  def test_name_scopes_for_variable_scopes(self):
    # Test that name scopes are not unnecessarily uniquified (but are
    # still uniquified when necessary).
    def linear_module(x, output_size):
      w = variable_scope.get_variable(
          "w", shape=[x.get_shape()[1], output_size],
          initializer=init_ops.zeros_initializer())
      b = variable_scope.get_variable(
          "b", shape=[output_size],
          initializer=init_ops.zeros_initializer())
      return (math_ops.matmul(x, w) + b), w

    def make_linear_module(output_size, name):
      return template.make_template(
          name,
          linear_module,
          output_size=output_size,
          create_scope_now_=True)

    inputs = array_ops.ones((3, 4))

    linear1 = make_linear_module(output_size=2, name="foo")
    outputs_a, w1 = linear1(inputs)
    outputs_b, _ = linear1(inputs)
    self.assertEqual("foo", linear1.variable_scope.name)
    self.assertEqual("foo/w:0", w1.name)
    if not context.executing_eagerly():
      self.assertEqual(
          "foo/add:0", outputs_a.name,
          "First application of template should get "
          "same name scope as variables.")
      self.assertEqual(
          "foo_1/add:0", outputs_b.name,
          "Second application of template should get "
          "a freshly uniquified name scope.")

    linear2 = make_linear_module(output_size=2, name="foo")
    outputs_c, w2 = linear2(inputs)
    outputs_d, _ = linear2(inputs)
    self.assertEqual(
        "foo_1", linear2.variable_scope.name,
        "New template gets a freshly uniquified variable scope "
        "because 'foo' is already taken.")
    self.assertEqual("foo_1/w:0", w2.name)
    if not context.executing_eagerly():
      self.assertEqual(
          "foo_1_1/add:0", outputs_c.name,
          "First application of template would get "
          "same name scope as variables, but 'foo_1' is already "
          "a name scope.")
      self.assertEqual(
          "foo_1_2/add:0", outputs_d.name,
          "Second application of template should also get "
          "a freshly uniquified name scope.")

  @test_util.run_in_graph_and_eager_modes
  def test_global_variables(self):
    # Make sure global_variables are created.
    with variable_scope.variable_scope("foo"):
      # Create two templates with the same name, ensure scopes are made unique.
      ta = template.make_template("bar", variable_scoped_function, True)
      if context.executing_eagerly():
        tb = template.make_template("s", function_with_side_create,
                                    trainable=False)
      else:
        tb = template.make_template("s", function_with_create, trainable=False)

    # Initially there are not variables created.
    self.assertEqual([], list(ta.global_variables))
    self.assertEqual([], list(tb.global_variables))
    # After calling there are variables created.
    ta()
    tb()
    # Ensure we can get the scopes before either template is actually called.
    self.assertEqual(1, len(ta.global_variables))
    self.assertEqual(2, len(tb.global_variables))

  @test_util.run_in_graph_and_eager_modes
  def test_trainable_variables(self):
    # Make sure trainable_variables are created.
    with variable_scope.variable_scope("foo2"):
      # Create two templates with the same name, ensure scopes are made unique.
      ta = template.make_template("bar", variable_scoped_function, True)
      tb = template.make_template("bar", variable_scoped_function, True)

    # Initially there are not variables created.
    self.assertEqual([], list(ta.trainable_variables))
    self.assertEqual([], list(tb.trainable_variables))
    # After calling there are variables created.
    ta()
    tb()
    # Ensure we can get the scopes before either template is actually called.
    self.assertEqual(1, len(ta.trainable_variables))
    self.assertEqual(1, len(tb.trainable_variables))
    # None non-trainable variable was created.
    self.assertEqual([], list(ta.non_trainable_variables))
    self.assertEqual([], list(tb.non_trainable_variables))
    # Ensure variables returns all the variables.
    self.assertEqual(1, len(ta.variables))
    self.assertEqual(1, len(tb.variables))

  @test_util.run_in_graph_and_eager_modes
  def test_non_trainable_variables(self):
    # Make sure non_trainable_variables are created.
    with variable_scope.variable_scope("foo2"):
      ta = template.make_template("a", variable_scoped_function,
                                  trainable=True)
      tb = template.make_template("b", variable_scoped_function,
                                  trainable=False)
    # Initially there are not variables created.
    self.assertEqual([], list(ta.variables))
    self.assertEqual([], list(tb.variables))
    # After calling there are variables created.
    ta()
    tb()
    # Check the trainable and non_trainable variables.
    self.assertEqual(1, len(ta.trainable_variables))
    self.assertEqual([], list(ta.non_trainable_variables))

    self.assertEqual([], list(tb.trainable_variables))
    self.assertEqual(1, len(tb.non_trainable_variables))
    # Ensure variables returns all the variables.
    self.assertEqual(1, len(ta.variables))
    self.assertEqual(1, len(tb.variables))

  # TODO(apassos) handle local variables in Eager
  @test_util.run_deprecated_v1
  def test_local_variables(self):
    # Make sure trainable_variables are created.
    with variable_scope.variable_scope("foo3"):
      # Create two templates with the same name, ensure scopes are made unique.
      ta = template.make_template("bar", variable_scoped_function, True)
      tb = template.make_template("bar",
                                  variable_scoped_function_with_local_variable)

    # Initially there are not variables created.
    self.assertEqual([], list(ta.local_variables))
    self.assertEqual([], list(tb.local_variables))
    # After calling there are variables created.
    ta()
    tb()
    # Ensure we can get the scopes before either template is actually called.
    self.assertEqual(0, len(ta.local_variables))
    self.assertEqual(1, len(tb.local_variables))

  @test_util.run_in_graph_and_eager_modes
  def test_make_template_with_defun(self):

    def variable_scoped_function_no_return_value(scope_name):
      # defun cannot compile functions that return non-Tensor objects
      with variable_scope.variable_scope(
          scope_name,
          reuse=variable_scope.AUTO_REUSE):
        _ = variable_scope.get_variable(
            "dummy", shape=[1], initializer=init_ops.zeros_initializer())

    tmpl = template.make_template_internal(
        "s1",
        variable_scoped_function_no_return_value,
        create_graph_function_=True,
        scope_name="test")

    # The first invocation of tmpl1 creates variables, the second should
    # be executed as a graph function.
    tmpl()
    v1 = tmpl.variables
    tmpl()
    v2 = tmpl.variables

    self.assertEqual(len(v1), len(v2))
    for v, w in zip(v1, v2):
      self.assertIs(v, w)
    self.assertEqual("s1/test/dummy:0", v1[0].name)


if __name__ == "__main__":
  test.main()
