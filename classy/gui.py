"""
"""
import sys

import classy
from classy.log import logger

from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets
import numpy as np
from scipy.signal import find_peaks

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets


class InteractiveFeatureFit(QtWidgets.QMainWindow):
    """Open a GUI to fit a spectral feature interactively."""

    def __init__(self, feature):
        """Initialise the fit and launch the GUI.

        Parameters
        ----------
        spec : classy.Spectrum
            The spectrum to fit.
        feature : str
            The feature to fit. One of ['e', 'h', 'k'].

        Notes
        -----
        The best fit parameters are stored in the classy cache directory.
        """
        self.feat = feature
        self._init_params()
        self._init_gui()
        self._init_plot()

    def _init_params(self):
        """Initialise the fit parameters."""

        PARAMS_SMOOTH = {
            "smooth": True,
            "method_smooth": "savgol",
            "deg_savgol": 3,
            "window_savgol": int(len(self.feat.spec.wave) / 2),
            "deg_spline": 4,
        }

        PARAMS_FEATURE = {
            "deg_poly": 4,
            "type_continuum": "linear",
            "lower": self.feat.lower,
            "upper": self.feat.upper,
            "present": "",
        }

        for key, value in PARAMS_SMOOTH.items():
            setattr(self, key, value)
        for key, value in PARAMS_FEATURE.items():
            setattr(self, key, value)

        # Load feature index
        _id = self.feat.spec.classy_id
        index_feat = classy.index.load_features()

        # Override default parameter values with saved ones
        if _id in index_feat.index.values:
            for param in PARAMS_SMOOTH.keys():
                setattr(self, param, index_feat.loc[_id, f"{param}"])

            for param in PARAMS_FEATURE.keys():
                if param in ["lower", "upper"]:
                    setattr(
                        self.feat,
                        param,
                        index_feat.loc[_id, f"{self.feat.name}_{param}"],
                    )
                else:
                    setattr(
                        self, param, index_feat.loc[_id, f"{self.feat.name}_{param}"]
                    )

            logger.debug("Read smoothing and feature parameters from index file.")

    def _init_gui(self):
        """Initialise the GUI for fitting."""

        # ------
        # The application window
        super(InteractiveFeatureFit, self).__init__()
        self._title = "classy: Feature Fit"
        self.setWindowTitle(self._title)
        self.resize(1600, 800)

        # ------
        # Initialise widgets and fill layout
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QGridLayout(self._main)

        # ------
        # Main plotting widget
        self.plot_feat = pg.PlotWidget(name="feat")
        self.plot_spec = pg.PlotWidget(name="spec")

        # Feature range window
        self.window = pg.LinearRegionItem(
            [self.feat.lower, self.feat.upper],
            bounds=[self.feat.spec.wave.min(), self.feat.spec.wave.max()],
        )
        self.window.sigRegionChanged.connect(self._changed_feature_region)
        self.window.setZValue(-10)
        self.plot_spec.addItem(self.window)

        # ------
        # Current parameters indicator

        # Smoothing - Savitzky-Golay
        self.check_smooth = QtWidgets.QCheckBox("Smoothing")

        if self.smooth:  # might already have been set from the cache
            self.check_smooth.setChecked(True)

        self.check_smooth.stateChanged.connect(self._update_smoothing)

        label_id = QtWidgets.QLabel(
            f"({self.feat.spec.number}) {self.feat.spec.name} - {self.feat.spec.source} - {self.feat.spec.filename}"
        )

        radio_savgol = QtWidgets.QRadioButton("Savitzky-Golay")
        radio_savgol.setChecked(True)
        radio_savgol.toggled.connect(self._update_smoothing)

        self.input_savgol_deg = pg.SpinBox(
            value=self.deg_savgol, step=1, bounds=[0, None]
        )
        self.input_savgol_deg.valueChanged.connect(self._update_smoothing)
        label_savgol_deg = QtWidgets.QLabel("Degree")

        self.input_savgol_window = pg.SpinBox(
            value=self.window_savgol, step=1, bounds=[0, len(self.feat.spec.wave)]
        )
        self.input_savgol_window.sigValueChanged.connect(self._update_smoothing)
        label_savgol_window = QtWidgets.QLabel("Window")

        degree_savgol = QtWidgets.QHBoxLayout()
        degree_savgol.addWidget(self.input_savgol_deg)
        degree_savgol.addWidget(label_savgol_deg)
        window_savgol = QtWidgets.QHBoxLayout()
        window_savgol.addWidget(self.input_savgol_window)
        window_savgol.addWidget(label_savgol_window)

        # Smoothing - Spline
        self.radio_spline = QtWidgets.QRadioButton("UnivariateSpline")
        self.radio_spline.setChecked(False)
        self.radio_spline.toggled.connect(self._update_smoothing)

        self.input_spline_deg = pg.SpinBox(
            value=self.deg_spline, step=1, bounds=[0, None]
        )
        self.input_spline_deg.valueChanged.connect(self._update_smoothing)
        label_spline_deg = QtWidgets.QLabel("Degree")

        degree_spline = QtWidgets.QHBoxLayout()
        degree_spline.addWidget(self.input_spline_deg)
        degree_spline.addWidget(label_spline_deg)

        # Store and reset buttons
        button_store_smooth = QtWidgets.QPushButton("Save Smoothing", self)
        button_store_feat = QtWidgets.QPushButton("Save Feature", self)
        button_exit = QtWidgets.QPushButton("Exit", self)
        button_store_smooth.clicked.connect(self._store_parameters_smooth)
        button_store_feat.clicked.connect(self._store_parameters_feat)
        button_exit.clicked.connect(self._exit)

        self.notify = QtWidgets.QLabel("")
        # ------
        # Add widgets and layouts to GUI

        # row, col, row_span, col_span
        addW = layout.addWidget
        addL = layout.addLayout
        right = QtCore.Qt.AlignRight

        addW(label_id, 0, 0, 1, 4)
        addW(self.notify, 0, 4, 1, 1)
        addW(button_store_smooth, 0, 5)
        addW(button_store_feat, 0, 6)
        addW(button_exit, 0, 7)
        addW(self.plot_spec, 1, 0, 4, 4)
        addW(self.plot_feat, 1, 4, 4, 4)
        addW(self.check_smooth, 6, 0, right)
        addW(radio_savgol, 6, 1)
        addL(degree_savgol, 6, 2)
        addL(window_savgol, 6, 3)
        addW(self.radio_spline, 7, 1)
        addL(degree_spline, 7, 2)

        # ------
        # Feature
        label_feat = QtWidgets.QLabel("Feature")
        self.select_feat = QtWidgets.QComboBox()

        # TODO: If feature is not observed, it should not be selectable
        for feat in ["h", "e", "k"]:
            self.select_feat.addItem(feat)

        self.select_feat.currentIndexChanged.connect(self._change_feature)
        feature = QtWidgets.QHBoxLayout()
        feature.addWidget(label_feat)
        feature.addWidget(self.select_feat)

        label_present = QtWidgets.QLabel("Is Present")
        self.select_present = QtWidgets.QComboBox()
        for feat in ["", "Yes", "No"]:
            self.select_present.addItem(feat)

        if self.present == "Yes":
            self.select_present.setCurrentIndex(1)
        elif self.present == "No":
            self.select_present.setCurrentIndex(2)
        present = QtWidgets.QHBoxLayout()
        present.addWidget(label_present)
        present.addWidget(self.select_present)

        addL(feature, 6, 4, right)
        addL(present, 7, 4, right)

        # Polynomial degree and continuum selection
        label_poly = QtWidgets.QLabel("Polynomial")
        label_cont = QtWidgets.QLabel("Continuum")

        self.input_poly_deg = pg.SpinBox(value=self.deg_poly, step=1, bounds=[0, None])
        self.input_poly_deg.valueChanged.connect(self._change_poly_degree)

        label_poly_deg = QtWidgets.QLabel("Degree")
        degree_poly = QtWidgets.QHBoxLayout()
        degree_poly.addWidget(self.input_poly_deg)
        degree_poly.addWidget(label_poly_deg)

        radio_linear = QtWidgets.QRadioButton("Linear Fit")
        radio_linear.setChecked(True)
        radio_linear.toggled.connect(self._change_continuum_type)

        radio_hull = QtWidgets.QRadioButton("Convex Hull")
        radio_hull.toggled.connect(self._change_continuum_type)

        addW(label_cont, 6, 5, right)
        addW(radio_linear, 6, 6, right)
        addW(radio_hull, 6, 7, right)
        addW(label_poly, 7, 5, right)
        addL(degree_poly, 7, 6)

        for i in range(1, 5):
            layout.setColumnStretch(i, 1)
            layout.setRowStretch(i, 1)
        for i in range(5, 9):
            layout.setRowStretch(i, 0)
        for i in range(5, 8):
            layout.setColumnStretch(i, 1)
        layout.setRowStretch(0, 0)

    def _init_plot(self):
        """Initialise the fitting functions and plot results."""

        # Plot original Spectrum
        self.plotted_spec = self.plot_spec.plot(
            self.feat.spec.wave, self.feat.spec.refl, pen=(255, 255, 255, 200)
        )

        # Zoom out to show context
        ymin, ymax = self.feat.spec.refl.min(), self.feat.spec.refl.max()
        yrange = ymax - ymin
        self.plot_spec.setYRange(ymin - 0.25 * yrange, ymax + 0.25 * yrange)

        # Continuum
        self._plot_continuum()

        # Fitted polynomial
        self._plot_fit()

        self._update_smoothing()
        self._plot_noise()

        # Center
        self.feat._compute_center()
        self._plot_center()

        # Plot feature region
        self._plot_feature()
        self._update_smoothing()
        self.feat._compute_center()
        self._plot_center()

    def _plot_feature(self):
        """Plot the continuum-removed feature region."""
        data = (
            self.feat.wave,
            self.feat.refl / self.feat.continuum(self.feat.wave),
        )
        if hasattr(self, "plot_feature"):
            self.plot_feature.setData(data[0], data[1])
        else:
            self.plot_feature = self.plot_feat.plot(
                data[0],
                data[1],
                pen=(255, 0, 255, 200),
            )

        if hasattr(self, "text_center"):
            self.text_center.setText(f"Center: {self.feat.center:.3f}um")
            self.text_depth.setText(f"Depth: {self.feat.depth:.2f}%")
        else:
            self.text_center = pg.LabelItem(f"Center: {self.feat.center:.3f}um")
            self.text_center.setParentItem(self.plot_feat.getPlotItem())
            self.text_center.anchor(itemPos=(0, 1), parentPos=(0, 1), offset=(70, -50))

            self.text_depth = pg.LabelItem(f"Depth: {self.feat.depth:.2f}%")
            self.text_depth.setParentItem(self.plot_feat.getPlotItem())
            self.text_depth.anchor(itemPos=(0, 1), parentPos=(0, 1), offset=(70, -80))

    def _get_smoothing_parameters(self):
        """Extract the smoothing parameters from the GUI."""
        return {
            "smooth": self.check_smooth.isChecked(),
            "method": "spline" if self.radio_spline.isChecked() else "savgol",
            "window_length": int(self.input_savgol_window.value()),
            "polyorder": int(self.input_savgol_deg.value()),
            "k": int(self.input_spline_deg.value()),
        }

    def _update_smoothing(self):
        # Plot the smoothed data or empty data
        params = self._get_smoothing_parameters()
        self.smooth = params["smooth"]
        self.smooth_method = params["method"]
        self.deg_savgol = params["polyorder"]
        self.window_savgol = params["window_length"]
        self.deg_spline = params["k"]

        self.feat.spec.unsmooth()
        if params["smooth"]:
            self.feat.spec.smooth(**params)
            data_ghost = [self.feat.spec.wave_original, self.feat.spec.refl_original]

        else:
            data_ghost = [[], []]

        data_spec = [self.feat.spec.wave, self.feat.spec.refl]

        if hasattr(self, "plot_ghost"):
            self.plot_ghost.setData(*data_ghost)
        else:
            self.plot_ghost = self.plot_spec.plot(*data_ghost, pen=(255, 0, 255, 200))
        self.plotted_spec.setData(*data_spec)
        self._plot_fit()
        self._plot_continuum()
        self._plot_feature()
        self._plot_noise()

    def _plot_continuum(self):
        """Plot the continuum function."""
        self.feat.compute_continuum(self.type_continuum)
        data = (self.feat.wave, self.feat.continuum(self.feat.wave))
        if hasattr(self, "plot_cont"):
            self.plot_cont.setData(data[0], data[1])
        else:
            self.plot_cont = self.plot_spec.plot(
                data[0],
                data[1],
                pen=(255, 0, 255, 200),
            )

    def _plot_fit(self):
        """Plot the fitted feature function."""
        self.feat.compute_fit(
            method="polynomial", degree=int(self.input_poly_deg.value())
        )

        data = (
            self.feat.wave,
            self.feat.fit(self.feat.wave),
        )
        if hasattr(self, "plot_poly"):
            self.plot_poly.setData(data[0], data[1])
        else:
            self.plot_poly = self.plot_feat.plot(
                data[0],
                data[1],
                pen=(255, 0, 255, 200),
            )

    def _plot_center(self):
        """Plot vertical line indicating the center position of the feature."""
        data = (
            [self.feat.center, self.feat.center],
            [
                self.feat.fit(self.feat.center),
                1,
            ],
        )

        if hasattr(self, "plot_cent"):
            self.plot_cent.setData(data[0], data[1])
            self.plot_one.setData(self.feat.wave, [1] * len(self.feat.wave))
        else:
            self.plot_cent = self.plot_feat.plot(data[0], data[1])
            self.plot_one = self.plot_feat.plot(
                self.feat.wave, [1] * len(self.feat.wave)
            )  # 1

    def _plot_noise(self):
        """Plot fit +- noise lines."""
        self.feat._compute_noise()
        data_upper = (
            self.feat.wave,
            self.feat.fit(self.feat.wave) + self.feat.noise / 2,
        )
        data_lower = (
            self.feat.wave,
            self.feat.fit(self.feat.wave) - self.feat.noise / 2,
        )

        if hasattr(self, "plot_noise_upper"):
            self.plot_noise_upper.setData(data_upper[0], data_upper[1])
            self.plot_noise_lower.setData(data_lower[0], data_lower[1])
        else:
            self.plot_noise_upper = self.plot_feat.plot(data_upper[0], data_upper[1])
            self.plot_noise_lower = self.plot_feat.plot(data_lower[0], data_lower[1])

    def _change_continuum_type(self):
        """Function for radio buttons to switch continuum types."""
        button = self.sender()
        if button.isChecked():
            self.continuum_type = button.type_

        self._plot_continuum()

        # Plot feature region
        self._plot_feature()

    def _change_poly_degree(self, degree):
        """Function to update polynomial degree from user input."""
        self.deg_poly = int(degree)

        # Fitted polynomial
        self._plot_fit()

        # Center
        self.feat._compute_center()
        self._plot_center()

        # Plot feature region
        self._plot_feature()
        self._plot_noise()

    def _changed_feature_region(self, region):
        if region is not None:
            # Recompute the spectral range of the feature
            self.feat.lower, self.feat.upper = region.getRegion()
        else:
            self.window.setRegion((self.feat.lower, self.feat.upper))

        # Continuum
        self._plot_continuum()

        # Fitted polynomial
        self._plot_fit()
        self._plot_noise()

        # Center
        self.feat._compute_center()
        self._plot_center()

        # Plot feature region
        self._plot_feature()

    def _change_feature(self):
        """Item box selection event"""
        self.feat.name = self.select_feat.currentText()
        self.feat.lower, self.feat.upper = (
            classy.defs.FEATURE[self.feat.name]["lower"],
            classy.defs.FEATURE[self.feat.name]["upper"],
        )
        self._changed_feature_region(None)

        # TODO: This should change the GUI parameters if feature
        # is already present in index

    def _store_parameters_smooth(self):
        # Load feature index
        index_feat = classy.index.load_features()

        # Use classy index number as identifier
        _id = self.feat.spec.classy_id

        # Add smoothing parameters
        for param in [
            "smooth",
            "method_smooth",
            "deg_savgol",
            "window_savgol",
            "deg_spline",
        ]:
            index_feat.loc[_id, f"{param}"] = getattr(self, param)

        # Store metadata
        for param in ["name", "number", "source", "shortbib", "bibcode", "filename"]:
            index_feat.loc[_id, param] = getattr(self.feat.spec, param)

        # Store feature index
        classy.index.store_features(index_feat)
        logger.info("Smoothing Parameters saved to file.")
        self.notify.setText("Smoothing parameters stored.")

    def _store_parameters_feat(self):
        # Load feature index
        index_feat = classy.index.load_features()

        # Use classy index number as identifier
        _id = self.feat.spec.classy_id

        # Add feature parameters
        for param in ["lower", "upper", "center", "depth", "noise"]:
            index_feat.loc[_id, f"{self.feat.name}_{param}"] = getattr(self.feat, param)

        index_feat.loc[_id, f"{self.feat.name}_type_continuum"] = self.type_continuum
        index_feat.loc[_id, f"{self.feat.name}_deg_poly"] = self.deg_poly
        index_feat.loc[
            _id, f"{self.feat.name}_present"
        ] = self.select_present.currentText()

        # Store metadata
        for param in ["name", "number", "source", "shortbib", "bibcode", "filename"]:
            index_feat.loc[_id, param] = getattr(self.feat.spec, param)

        # Store feature index
        classy.index.store_features(index_feat)
        logger.info("Feature parameters saved to file.")
        self.notify.setText("Feature parameters stored.")

    def _exit(self):
        """Bye bye."""
        self.close()


def main(feature):
    qapp = QtWidgets.QApplication(sys.argv)
    app = InteractiveFeatureFit(feature)
    app.show()
    qapp.exec_()
    qapp.quit()
