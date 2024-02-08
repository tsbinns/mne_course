"""Helper functions for using the notebooks."""

import numpy as np
from matplotlib import pyplot as plt


def plot_psd(psd: np.ndarray, freqs: np.ndarray) -> None:
    """Plot power spectral density.

    Parameters
    ----------
    psd : np.ndarray, shape of (channels, freqs)
        Power spectral density data.

    freqs : np.ndarray, shape of (freqs,)
        Frequencies in `psd`.

    Notes
    -----
    PSD values are not scaled according to channel type, unlike in MNE's PSD plotting.
    """
    # Input checking
    if not isinstance(psd, np.ndarray):
        raise TypeError("`psd` must be a numpy array.")
    if not isinstance(freqs, np.ndarray):
        raise TypeError("`freqs` must be a numpy array.")

    if psd.ndim != 2:
        raise ValueError("`psd` must be a 2D array.")
    if freqs.ndim != 1:
        raise ValueError("`freqs` must be a 1D array.")

    if psd.shape[1] != freqs.shape[0]:
        raise ValueError("`psd` and `freqs` must have the same number of frequencies.")

    # Convert to same scale as MNE plotting
    psd = psd.copy()
    psd = np.log10(np.maximum(psd, np.finfo(float).tiny)) * 10

    # Plotting
    _, ax = plt.subplots(1, 1)

    for psd_chan in psd:
        plt.plot(freqs, psd_chan, alpha=0.5)

    ax.set_xlim((freqs.min(), freqs.max()))

    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power (dB; unscaled)")

    plt.show(block=False)
