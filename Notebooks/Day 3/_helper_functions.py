"""Helper functions for using the notebooks."""

import mne
import numpy as np
from matplotlib import pyplot as plt


def simulate_connectivity(
    n_seeds: int,
    n_targets: int,
    freq_band: tuple[int, int],
    n_epochs: int = 10,
    n_times: int = 200,
    sfreq: int = 100,
    snr: float = 0.7,
    connection_delay: int = 10,
    rng_seed: int | None = None,
) -> mne.Epochs:
    """Simulates signals interacting in a given frequency band.

    Parameters
    ----------
    n_seeds : int
        Number of seed channels to simulate.

    n_targets : int
        Number of target channels to simulate.

    freq_band : tuple of int, int
        Frequency band where the connectivity should be simulated, where the first entry corresponds
        to the lower frequency, and the second entry to the higher frequency.

    n_epochs : int (default 10)
        Number of epochs in the simulated data.

    n_times : int (default 200)
        Number of timepoints each epoch of the simulated data.

    sfreq : int (default 100)
        Sampling frequency of the simulated data, in Hz.

    snr : float (default 0.7)
        Signal-to-noise ratio of the simulated data.

    connection_delay : int (default 10)
        Number of timepoints for the delay of connectivity between the seeds and targets. If > 0,
        the target data is a delayed form of the seed data by this many timepoints.

    rng_seed : int | None (default None)
        Seed to use for the random number generator. If `None`, no seed is specified.

    Returns
    -------
    epochs : mne.Epochs
        The simulated data stored in an Epochs object. The channels are arranged according to seeds,
        then targets.
    """
    if rng_seed is not None:
        np.random.seed(rng_seed)

    n_channels = n_seeds + n_targets
    trans_bandwidth = 1  # Hz

    # simulate signal source at desired frequency band
    signal = np.random.randn(1, n_epochs * n_times + connection_delay)
    signal = mne.filter.filter_data(
        data=signal,
        sfreq=sfreq,
        l_freq=freq_band[0],
        h_freq=freq_band[1],
        l_trans_bandwidth=trans_bandwidth,
        h_trans_bandwidth=trans_bandwidth,
        fir_design="firwin2",
        verbose=False,
    )

    # simulate noise for each channel
    noise = np.random.randn(n_channels, n_epochs * n_times + connection_delay)

    # create data by projecting signal into noise
    data = (signal * snr) + (noise * (1 - snr))

    # shift target data by desired delay
    if connection_delay > 0:
        # shift target data
        data[n_seeds:, connection_delay:] = data[n_seeds:, : n_epochs * n_times]
        # remove extra time
        data = data[:, : n_epochs * n_times]

    # reshape data into epochs
    data = data.reshape(n_channels, n_epochs, n_times)
    data = data.transpose((1, 0, 2))  # (epochs x channels x times)

    # store data in an MNE Epochs object
    ch_names = [f"{ch_i}_{freq_band[0]}_{freq_band[1]}" for ch_i in range(n_channels)]
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types="eeg", verbose=False)
    epochs = mne.EpochsArray(data=data, info=info, verbose=False)

    return epochs


def plot_connectivity(results: np.ndarray, freqs: list):
    """Plots connectivity results for a single connection.

    Parameters
    ----------
    results : numpy.ndarray, shape of (frequencies)
        Results for a single connection.

    freqs : list
        Frequencies in `results`.
    """
    if results.shape != (len(freqs),):
        raise ValueError("`results` must be a 1D array with the same length as `freqs`.")
    _, ax = plt.subplots(1, 1)
    ax.plot(freqs, results, linewidth=3)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Connectivity (A.U.)")
    plt.show()
