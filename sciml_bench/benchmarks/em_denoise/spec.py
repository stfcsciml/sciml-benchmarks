import sciml_bench.mark
from sciml_bench.core.benchmark import BenchmarkSpec


@sciml_bench.mark.benchmark_spec
class EMDenoiseSpec(BenchmarkSpec):
    name = 'em_denoise'
    train_dir = 'train'
    test_dir = 'test'

    epochs = 10
    loss_function = 'mse'
    batch_size = 256
    optimizer_params = dict(learning_rate=0.01)
