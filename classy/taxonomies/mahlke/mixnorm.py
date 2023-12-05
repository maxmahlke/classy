import numpy as np
from sklearn import preprocessing

from classy import index
from . import defs


COLORS = []
HATCHES = []


def normalize(spec):
    """Normalize a spectrum using the mixnorm algorithm.

    Parameters
    ----------
    spec : classy.spectra.Spectrum
        The spectrum to normalize.

    Returns
    -------
    alpha : float
        The normalization constat to subtract from the spectrum after log-transform.
    """
    if all(np.isnan(r) for r in spec.refl):
        return np.nan

    # Load the trained normalization instance
    normalization, neighbours = index.data.load("mixnorm")

    # Compute model initalization parameters by nearest neighbour search among classy spectra
    neighbours_spectra = neighbours[defs.WAVE_GRID_STR].values
    idx_nearest_neighbours = _find_nearest_neighbours(spec, neighbours_spectra, N=5)

    # Compute most probable alpha as weighted average of the nearest neighbours
    alpha = neighbours.loc[idx_nearest_neighbours, "alpha"].mean()

    # Shift spectral reflectance to the mean level of the reference spectra
    # import matplotlib.pyplot as plt

    # plt.plot(
    #     spec.wave,
    #     spec.refl,
    #     ls="-",
    #     c="black",
    # )

    # for m in idx_nearest_neighbours:
    #     plt.plot(
    #         classy.defs.WAVE_GRID[spec.mask],
    #         neighbours_spectra[m].T,
    #         ls="--",
    #         c="red",
    #     )
    spec.refl = (
        spec.refl
        / np.nanmean(spec.refl)
        * np.nanmean(neighbours.loc[idx_nearest_neighbours, defs.WAVE_GRID_STR])
    )
    # plt.plot(
    #     spec.wave,
    #     spec.refl,
    #     ls="-",
    #     c="blue",
    # )
    # plt.show()
    return alpha

    # Create gamma_init by finding spectrum closest to the new one
    data_complete = ml_master[defs.COLUMNS["spectra"]].values

    gamma_init = []
    alpha_init = []
    for ind, spec in data.iterrows():
        mask = np.isnan(spec)
        reference = data_complete[:, ~mask]
        reference_normed = reference[~np.isnan(reference).any(axis=1), :]

        # Find closest complete spectra
        closest_spectra_idx, distances = find_closest(np.exp(spec), reference_normed)

        if True:  # only the best match
            gamma_init.append(normalization["gamma"][closest_spectra_idx[0]])
        else:  # mean gamma_init of best matches
            gamma_inits = [normalization["gamma"][i] for i in closest_spectra_idx]
            mean_gamma_inits = np.mean(
                [normalization["gamma"][i] for i in closest_spectra_idx],
                axis=0,
            )
            gamma_init.append(mean_gamma_inits)

        alpha_init.append(normalization["alpha"][closest_spectra_idx[0]][0])

        # Normalize spectrum to level of the match
        norm_idx = np.where(~np.isnan(spec))[0][0]
        norm_value = reference_normed[closest_spectra_idx[0]][norm_idx]

        # the spectra to normalize are already log-transformed
        diff = norm_value / spec[norm_idx]

        data.loc[ind, defs.COLUMNS["spectra"]] *= diff

    # ------
    # Compute alpha_init by next-neighbour search
    # Alpha of closest spectrum in clustering sample
    # ml_master = classy.ml.get_master(
    #     limit_missing=MODEL_PARAMETERS["max_missing_bins"]
    # )
    # # ml_master.loc[:, classy.ML_SETUP.COLUMNS["spectra"]] = np.log(
    # #     ml_master[classy.ML_SETUP.COLUMNS["spectra"]]
    # # )

    # # Create alpha_init by finidng spectrum closest to the new one
    # data_complete = ml_master[classy.ML_SETUP.COLUMNS["spectra"]].values

    # for ind, spec in data.iterrows():

    # Find closest complete spectra
    # closest_spectra_idx, distances = find_closest(
    #     np.exp(spec), data_complete
    # )
    alpha_init = np.array(alpha_init)[:, None]

    # ------
    # Normalize
    data[defs.COLUMNS["spectra"]] = np.log(data[defs.COLUMNS["spectra"]])
    X = data[defs.COLUMNS["spectra"]].values
    X = np.ma.masked_array(X, mask=np.isnan(X))
    alpha, gamma, _ = gem_mixnorm_eval(
        X,
        K=MODEL_PARAMETERS["k_norm"],
        mus=normalization["mus"],
        sigmas=normalization["sigmas"],
        pis=normalization["pis"],
        gamma_init=gamma_init,
        alpha_init=alpha_init,
    )

    # TMP
    # Plot normalized spectra
    if False:
        import matplotlib.pyplot as plt

        data_classy, _ = classy.ml.load_data()

        plt.plot(
            classy.ML_SETUP.COLUMNS["spectra"],
            data_classy[classy.ML_SETUP.COLUMNS["spectra"]].values.T,
            ls="-",
            c="lightgray",
            alpha=0.4,
        )
        plt.plot(
            classy.ML_SETUP.COLUMNS["spectra"],
            data_classy.loc[
                data_classy.class_sf.isin(["K", "L", "M"]),
                classy.ML_SETUP.COLUMNS["spectra"],
            ].values.T,
            ls="-",
            c="orange",
            alpha=0.4,
        )
        plt.plot(classy.ML_SETUP.COLUMNS["spectra"], (X - alpha).T, ls="-", c="red")
        plt.show()

    spectrum.alpha = alpha
    spectrum.refl = refl_normalized


def _find_nearest_neighbours(spec, neighbours, N):
    """Find the nearest neighbours of a spectrum in terms of L2 norm.

    Parameters
    ----------
    spec : astro.spectra.Spectrum
        The spectrum who's neighbours to find.
    neighbours : np.ndarray
        The reflectance values of the neighbours in a numpy array.
    N : int
        The number of neares neighbours to return.

    Returns
    -------
    list of int
        The indices of the nearest neighbours.
    """

    # Mask the neighbours to the observed wavelength range
    spec.mask = np.array([np.isfinite(r) for r in spec.refl])
    neighbours = neighbours[:, spec.mask]

    # We cannot compare with neighbours which do not have all bins observed
    mask_neighbours = np.array(
        [all(np.isfinite(r) for r in neighbour) for neighbour in neighbours]
    )

    # Normalize the spectrum and the neighbours using the L2 norm
    refl_spec = preprocessing.normalize(spec.refl[spec.mask].reshape(1, -1))
    neighbours[mask_neighbours] = preprocessing.normalize(neighbours[mask_neighbours])

    # Find the closest neighbours in L2 distance
    distances = np.linalg.norm(
        refl_spec - neighbours, axis=1
    )  # No masking here to get same shape as neighbours. Non-matching neighbours have NaN distance
    closest_neighbours = distances.argsort()[:N]

    if False:
        import matplotlib.pyplot as plt

        for m in closest_neighbours:
            plt.plot(
                classy.defs.WAVE_GRID[spec.mask],
                refl_spec.T,
                ls="-",
                c="black",
            )
        plt.plot(
            classy.defs.WAVE_GRID[spec.mask],
            neighbours[closest_neighbours].T,
            ls="--",
            c="red",
        )
        plt.show()
    return closest_neighbours


# ------
# Mixnorm normalization algorithm
def gem_mixnorm(
    X,
    K,
    inds_baseline=[0],
    alpha_init=None,
    gamma_init=None,
    nit_em=200,
    nit_ca=20,
    eps=1e-6,
    verbose=False,
):
    """Runs a single time the GEM algorithm

    INPUT
    ---------
    X : numpy masked array, incomplete data matrix (each rox is a spectrum)
    K : number of clusters
    inds_baseline : indices of baseline spectra that will not be shifted
    alpha_init : initial value for the shifts alpha, default is a vector of zeros
    gamma_init : initial value for the cluster assignments, matrix of shape (np.shape(X)[0],K), default is random
    nit_em : maximum number of iterations for the GEM algorithm
    nit_ca : number of iterations for the coordinate ascent algorithm within the GM step
    eps : convergence threshold to stop training

    OUTPUT
    ----------
    alpha,mus,sigmas,pis : values of the parameters after training
    gamma : cluster assignments, matrix of shape (np.shape(X)[0],K) with probabilities
    loglik,bic : value of the loglikelihood/BIC after convergence
    """

    n = X.shape[0]
    d = X.shape[1]

    if alpha_init is None:
        alpha_init = np.zeros((n, 1))
        alpha_init[inds_baseline, 0] = 0

    if gamma_init is None:
        gamma_init = np.zeros(
            (n, K)
        )  # We intialise the cluster using a random partition
        gamma_init[np.arange(n), np.random.choice(K, n)] = 1

    # Initialisation
    alpha = alpha_init

    gamma = gamma_init

    mus = np.zeros((d, K))
    sigmas = np.ones((d, K))

    it = 0
    reldiff = eps + 1
    loglik = -np.Inf

    # GEM algorithm (GM step followed by E step)

    while (it <= nit_em) & (reldiff > eps):
        it = it + 1

        # GM step
        log_pis = np.log(np.sum(gamma, 0)) - np.log(n)  # class proportions

        for h in range(nit_ca):  # coordinate ascent loop
            Xminusalpha = X - alpha

            for k in range(K):
                mus[:, k] = np.ma.average(
                    a=Xminusalpha, axis=0, weights=gamma[:, k]
                )  # kth mean
                sigmas[:, k] = np.sqrt(
                    np.ma.average(
                        a=(Xminusalpha - mus[:, k]) ** 2, axis=0, weights=gamma[:, k]
                    )
                )  # kth covariance

            sigmas = np.clip(sigmas, a_min=1e-6, a_max=None)

            alpha[:, 0] = np.ma.average(
                a=np.expand_dims(X, 2) - mus,
                weights=np.expand_dims(gamma, 1) / sigmas**2,
                axis=(1, 2),
            )

            alpha[inds_baseline, 0] = 0

        Xminusalpha = X - alpha

        if it > 1:
            loglik_old = loglik
            loglik = np.mean(
                scisp.logsumexp(logits.data, 1)
            )  # the log-likelihood is computed after the GM step, not after the E step
            reldiff = np.abs(
                (loglik - loglik_old) / loglik
            )  # relative difference to check convergence

        # E step
        logits = (
            np.sum(
                -((np.expand_dims(Xminusalpha, 2) - np.expand_dims(mus, 0)) ** 2)
                / (2 * sigmas**2)
                - np.log(sigmas)
                - np.log(2 * np.pi) / 2,
                1,
            )
        ) + log_pis  # a verifier

        gamma = scisp.softmax(
            logits.data, 1
        )  # cluster probabilities, aka "responsabilities"

        if (it >= 1) & (verbose == True):
            print("---")
            print("Iteration", it)
            print("Average log-likelihood")

    nu = (n - 1) + (K - 1) + d * K + d * K  # numbers of degrees of freedom for the BIC

    bic = n * loglik - np.log(n) / 2 * nu

    nu = (K - 1) + d * K + d * K
    # bic = -2*n*loglik + np.log(n)*nu

    pis = np.exp(log_pis)

    return alpha, mus, sigmas, gamma, pis, loglik, bic


def mixnorm(
    X,
    K,
    inds_baseline=[0],
    nit_em=400,
    num_miniEM=50,
    nit_miniEM=5,
    # nit_em=500,
    # num_miniEM=5,
    # nit_miniEM=10,
    eps=1e-5,
    verbose=False,
):
    """Runs the GEM algorithm using multiple random initialisations

    INPUT
    ---------
    X : numpy masked array, incomplete data matrix (each rox is a spectrum)
    K : number of clusters
    inds_baseline : indices of baseline spectra that will not be shifted
    nit_em : maximum number of iterations for the final GEM algorithm
    num_miniEM : number of "mini EM" used for intialisation
    nit_miniEM : number of iterations for the "mini EM"
    eps : convergence threshold to stop training

    OUTPUT
    ----------
    alpha,mus,sigmas : values of the parameters after training
    gamma : cluster assignments, matrix of shape (np.shape(X)[0],K) with probabilities
    loglik,bic : value of the loglikelihood/BIC after convergence
    """

    alpha1, __, __, __, __, __, __ = gem_mixnorm(
        X, inds_baseline=inds_baseline, K=1, nit_em=nit_miniEM, eps=-1, verbose=verbose
    )

    for rep in range(num_miniEM):
        print(rep)

        alpha, __, __, gamma, __, loglik, __ = gem_mixnorm(
            X,
            inds_baseline=inds_baseline,
            K=K,
            nit_em=nit_miniEM,
            alpha_init=alpha1,
            eps=-1,
            verbose=verbose,
        )

        if rep == 0:
            gamma_init = gamma
            loglik_init = loglik
            alpha_init = alpha

        if (rep > 0) & (loglik > loglik_init):
            gamma_init = gamma
            loglik_init = loglik
            alpha_init = alpha

    alpha, mus, sigmas, gamma, pis, loglik, bic = gem_mixnorm(
        X,
        K=K,
        inds_baseline=inds_baseline,
        alpha_init=alpha_init,
        gamma_init=gamma_init,
        nit_em=nit_em,
        eps=eps,
        verbose=verbose,
    )
    return (alpha, mus, sigmas, gamma, pis, loglik, bic)


def gem_mixnorm_eval(
    X,
    K,
    mus,
    sigmas,
    pis,
    alpha_init=None,
    gamma_init=None,
    nit_em=100,
    eps=1e-6,
    verbose=False,
    inds_baseline=[0],
):
    """Runs a single time the EM algorithm for normalising new spectra

    INPUT
    ---------
    X : numpy masked array, incomplete data matrix (each rox is a spectrum)
    K : number of clusters
    mus,sigmas,pis : fixed values of the parameters
    alpha_init : initial value for the shifts alpha, default is a vector of zeros
    nit_em : maximum number of iterations for the EM algorithm
    eps : convergence threshold to stop training

    OUTPUT
    ----------
    alpha : values of the offsets after training
    gamma : cluster assignments, matrix of shape (np.shape(X)[0],K) with probabilities
    loglik : value of the log-likelihood after convergence
    """
    n = X.shape[0]
    d = X.shape[1]
    log_pis = np.log(pis)

    if alpha_init is None:
        alpha_init = np.zeros((n, 1))
        alpha_init[inds_baseline, 0] = 0

    if gamma_init is None:
        Xminusalpha = X - alpha_init
        logits = (
            np.sum(
                -((np.expand_dims(Xminusalpha, 2) - np.expand_dims(mus, 0)) ** 2)
                / (2 * sigmas**2)
                - np.log(sigmas)
                - np.log(2 * np.pi) / 2,
                1,
            )
        ) + log_pis  # a verifier
        gamma_init = scisp.softmax(logits.data, 1)

    # Initialisation
    alpha = alpha_init
    gamma = gamma_init

    it = 0
    reldiff = eps + 1
    loglik = -np.Inf

    # GEM algorithm (M step followed by E step)
    while (it <= nit_em) & (reldiff > eps):
        it = it + 1

        # M step

        alpha[:, 0] = np.ma.average(
            a=np.expand_dims(X, 2) - mus,
            weights=np.expand_dims(gamma, 1) / sigmas**2,
            axis=(1, 2),
        )

        if it > 1:
            loglik_old = loglik
            loglik = np.mean(
                scisp.logsumexp(logits.data, 1)
            )  # the log-likelihood is computed after the M step, not after the E step
            reldiff = np.abs(
                (loglik - loglik_old) / loglik
            )  # relative difference to check convergence

        # E step
        Xminusalpha = X - alpha

        logits = (
            np.sum(
                -((np.expand_dims(Xminusalpha, 2) - np.expand_dims(mus, 0)) ** 2)
                / (2 * sigmas**2)
                - np.log(sigmas)
                - np.log(2 * np.pi) / 2,
                1,
            )
        ) + log_pis  # a verifier
        gamma = scisp.softmax(logits.data, 1)

        if (it > 1) & (verbose == True):
            print("---")
            print("Iteration", it)
            print("Average log-likelihood")
            print(loglik)

    return alpha, gamma, loglik


def normalize_l2(data):
    # L2 norm and extrapolation of missing bins

    data_specs = data[classy.ML_SETUP.COLUMNS["spectra"]].values.copy()
    data_complete = (
        data[classy.ML_SETUP.COLUMNS["spectra"]].dropna(how="any", axis=0).values
    )

    # handle the missing bins
    for i, sample in enumerate(data_specs):
        index = data.index.values[i]

        # get incomplete values
        mask = np.isnan(sample)

        # if it's a complete spectrum
        if not mask.size:
            sample = sklearn.preprocessing.normalize(sample.reshape(1, -1))[0]
            data_specs[i] = sample
            continue

        # do l2 normalization using the observed bins of the sample
        # plus all complete spectra
        wave_norm_index = np.where(~np.isnan(sample))[0][0]
        data_complete = data_complete / data_complete[:, wave_norm_index][:, None]

        reference = data_complete[:, ~mask]

        # reference_normed = preprocessing.normalize(reference)
        # sample_normed = preprocessing.normalize(sample[~mask].reshape(1, -1))
        reference_normed = reference  # / reference[:, 0][:, None]
        sample_normed = sample[~mask] / sample[~mask][0]

        # find the N spectra closest to the sample_normed in euclidean distance
        N = 5

        # find the closest covariance matrices
        distances = np.linalg.norm(reference_normed - sample_normed, axis=1)

        # distances = []

        # for ref in reference_normed:
        #     distances.append(np.correlate(ref, sample_normed)[0])

        # distances = np.array(distances)

        # get highest correlations
        matched_with = distances.argsort()[:N]

        sample[mask] = np.mean(
            data_complete[matched_with][:, mask],
            axis=0,  # / data_complete[0, None], axis=0
        )
        sample[~mask] = sample_normed

        if False and data.loc[index, "complex_"] == "D":
            for m in matched_with:
                plt.plot(
                    classy.SPECTRA_SETUP.WAVE_GRID,
                    data_complete[m],  # / data_complete[m][0, None],
                    ls="--",
                    c="black",
                )
            plt.plot(
                classy.SPECTRA_SETUP.WAVE_GRID[mask],
                sample[mask],
                ls="--",
                c="red",
            )
            plt.plot(
                classy.SPECTRA_SETUP.WAVE_GRID[~mask],
                sample[~mask],
                ls="-",
                c="red",
            )
            plt.show()

        # if the spectrum is complete
        # if not mask.size:

        # Impute the mean before normalizing
        # sample[mask] = np.nanmean(sample)
        sample = sklearn.preprocessing.normalize(sample.reshape(1, -1))[0]
        sample[mask] = np.nan
        data_specs[i] = sample

    data[classy.ML_SETUP.COLUMNS["spectra"]] = data_specs
    # plt.plot(classy.SPECTRA_SETUP.WAVE_GRID, np.nanmean(data_specs, axis=0), ls="-")
    # plt.show()
    # data[ML_SETUP.COLUMNS["spectra"]] = data_specs - np.nanmean(data_specs, axis=0)
    return data, []
