import numpy as np
import pytest

import nengo


def _normalize(x):
    return x / np.linalg.norm(x)


@pytest.mark.optional  # Skip test per default, it is too slow
@pytest.mark.parametrize('d', [4, 32])
def test_dotproduct(Simulator, d, plt):
    np.random.seed(324)
    v1 = _normalize(np.random.randn(d))
    v2 = _normalize(np.random.randn(d))

    model = nengo.Network(seed=3359)
    with model:
        in_a = nengo.Node(output=v1)
        in_b = nengo.Node(
            output=lambda t: _normalize(np.sin(t) * v2 + (1 - np.sin(t)) * v1))
        prod = nengo.spaopt.Product(int(6400 / d), d)
        result = nengo.Ensemble(
            n_neurons=1, dimensions=1, neuron_type=nengo.Direct())

        nengo.Connection(in_a, prod.A)
        nengo.Connection(in_b, prod.B)
        nengo.Connection(
            prod.output, result, transform=prod.dot_product_transform())

        ddot = nengo.networks.EnsembleArray(
            2, d, 2, neuron_type=nengo.Direct())
        dresult = nengo.Ensemble(
            n_neurons=1, dimensions=1, neuron_type=nengo.Direct())

        nengo.Connection(in_a, ddot.input[::2])
        nengo.Connection(in_b, ddot.input[1::2])
        nengo.Connection(
            ddot.add_output('dot', lambda x: x[0] * x[1]), dresult,
            transform=[d * [1.0]])

        probe = nengo.Probe(result, synapse=0.01)
        dprobe = nengo.Probe(dresult, synapse=0.01)

    sim = Simulator(model)
    sim.run(2 * np.pi)

    plt.plot(sim.trange(), sim.data[probe])
    plt.plot(sim.trange(), sim.data[dprobe])

    assert np.max(np.abs(sim.data[probe] - sim.data[dprobe])) < 0.11

if __name__ == '__main__':
    nengo.log(debug=True)
    pytest.main([__file__, '-v'])