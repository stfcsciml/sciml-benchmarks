import inspect
from collections import defaultdict
from sciml_bench.core.bench_logger import LOGGER
import tensorflow as tf

# Registry of model functions for each benchmark spec
# This provides a mapping from str -> list, where the key is the name of the
# benchmark spec and the value is a list of registered functions for that spec.
# Currently we take the last function added as the one to use.
BENCHMARK_REGISTRY = {}

# Registry of model functions for each benchmark spec
# This provides a mapping from str -> list, where the key is the name of the
# benchmark spec and the value is a list of registered functions for that spec.
# Currently we take the last function added as the one to use.
MODEL_FUNCS_REGISTRY = defaultdict(list)

# Registry of data loaders for each benchmark spec
# This provides a mapping from str -> list, where the key is the name of the
# benchmark spec and the value is a list of registered data loader classes for that spec.
# Currently we take the last registered loader added as the one to use.
DATA_LOADER_REGISTRY = defaultdict(list)

# Registry of validation data loaders for each benchmark spec
# This provides a mapping from str -> list, where the key is the name of the
# benchmark spec and the value is a list of registered data loader classes for that spec.
# Currently we take the last registered loader added as the one to use.
VALIDATION_DATA_LOADER_REGISTRY = defaultdict(list)


class BenchmarkSpec:

    epochs = None
    loss_function = None
    batch_size = None
    optimizer = None

    train_dir = ''
    test_dir = ''

    model_params={}
    loss_params={}
    optimizer_params={}
    metrics=[]

    def __init__(self, data_dir, optimizer='adam', loss_function='binary_crossentropy', model_params={}, loss_params={}, optimizer_params={}, metrics=[], **kwargs):

        self.model_func = MODEL_FUNCS_REGISTRY[self.name][-1]

        data_loader_class = DATA_LOADER_REGISTRY[self.name][-1]
        validation_data_loader_class = VALIDATION_DATA_LOADER_REGISTRY[self.name][-1]

        LOGGER.debug('Model function is {} defined in {}'.format(self.model_func.__name__, inspect.getfile(self.model_func)))
        LOGGER.debug('Data loader class is {}'.format(data_loader_class.__name__))
        LOGGER.debug('Validation data loader class is {}'.format(validation_data_loader_class.__name__))

        self.data_loader = data_loader_class(data_dir=data_dir / self.train_dir, batch_size=self.batch_size, is_training_data=True, **kwargs)
        self.validation_data_loader = validation_data_loader_class(data_dir=data_dir / self.test_dir, batch_size=self.batch_size, is_training_data=False, **kwargs)

        self.loss_function = loss_function
        self.optimizer = optimizer
        self.metrics.extend(metrics)

        # Params for model objects
        self.model_params.update(model_params)
        self.loss_params.update(loss_params)
        self.optimizer_params.update(optimizer_params)


class Benchmark:

    def __init__(self, spec):
        self._spec = spec

    @property
    def spec(self):
        return self._spec

    @property
    def data_loader(self):
        return self._spec.data_loader

    @property
    def validation_data_loader(self):
        return self._spec.validation_data_loader


class TensorflowKerasBenchmark(Benchmark):

    def __init__(self, spec):
        super().__init__(spec)

    @property
    def model(self):
        return self._spec.model_func(self._spec.data_loader.input_shape, **self._spec.model_params)

    @property
    def loss(self):
        loss = tf.keras.losses.get(self._spec.loss_function)
        if hasattr(loss, 'get_config'):
            cfg = loss.get_config()
            cfg.update(self._spec.loss_params)
            loss = loss.from_config(cfg)
        return loss

    @property
    def optimizer(self):
        opt = tf.keras.optimizers.get(self._spec.optimizer)
        cfg = opt.get_config()
        cfg.update(self._spec.optimizer_params)
        opt = opt.from_config(cfg)
        return opt

    @property
    def metrics(self):
        return self._spec.metrics
