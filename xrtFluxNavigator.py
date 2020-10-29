# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 16:02:44 2020

@author: Roman Chernikov

Test data can be downloaded from https://yadi.sk/d/65sbTgz7MEnfnA (~200MB numpy pickle) or use the calculator script nearby.
"""

import numpy as np
#from pyqtgraph.Qt import QtCore, QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets as QtGui
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

colorFactor = 0.85  # 2./3 for red-to-blue
colorSaturation = 0.85


class FluxNavigator(QtGui.QWidget):
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        layout = QtGui.QHBoxLayout()
        data = np.load('I0 vs E vs solidAngle 101x512x512.npz')
        self.plotArray3D = data['I0']
        energy = data['energy']
        theta = data['theta']*1e6
        psi = data['psi']*1e6
        self.fluxArray = np.sum(self.plotArray3D, axis=(1, 2))
        self.wlScale = energy
#        self.wlScale.reverse()
#        self.shifts = ['000', '025', '050', '075', '100', '125', '150']
        self.fluxFig = Figure(figsize=(12, 12))
        self.fluxAx = self.fluxFig.add_subplot(111)
        self.fluxAx.set_xlabel("Energy, eV")
        self.fluxAx.set_ylabel("Total flux, ph/s/0.1%BW")
#        self.fluxFig.suptitle('Shift {}cm'.format('000'))

        self.fieldFig = Figure(figsize=(12, 12))
        self.fieldAx = self.fieldFig.add_subplot(111)
        

        self.sliderE = QtGui.QSlider(QtCore.Qt.Horizontal)        
        self.sliderE.setRange(0, len(self.wlScale)-1)
        self.sliderE.setTickInterval(1)
        self.sliderE.valueChanged.connect(self.update_frame)

#        self.sliderShift = QtGui.QSlider(QtCore.Qt.Horizontal)        
#        self.sliderShift.setRange(0, len(self.shifts)-1)
#        self.sliderShift.setTickInterval(1)
#        self.sliderShift.valueChanged.connect(self.update_frame)



        hue, tmp, tmp = np.meshgrid(energy, theta, psi, indexing='ij')
        hue -= hue.min()
        hue /= hue.max()
        sat = np.ones_like(hue)
        val = self.plotArray3D / self.plotArray3D.max()
    #    hsvI0 = np.stack((hue, sat, val), axis=3) # numpy1.10
        hsvI0 = np.zeros([d for d in hue.shape] + [3])
        hsvI0[:, :, :, 0] = hue
        hsvI0[:, :, :, 1] = sat
        hsvI0[:, :, :, 2] = val
    
        self.rgbI0 = colors.hsv_to_rgb(hsvI0)
        rgbI0slice = np.transpose(self.rgbI0[0, :, :], [1, 0, 2])
        
        size = len(energy)
        colorFactor=0.95
        normSpec = self.fluxArray / np.max(self.fluxArray)
        histVals = np.int32(normSpec * (size-1))
        histImage = np.zeros((size, size, 3))
        bins = np.linspace(energy.min(), energy.max(), size)
        print(colorFactor, bins, colorSaturation, normSpec)
        for col in range(size):
            colRGB = colors.hsv_to_rgb(
                (colorFactor * (bins[col] - energy.min()) /
                 (energy.max() - energy.min()),
                 colorSaturation, normSpec[col]))
            histImage[0:int(histVals[col]*colorSaturation), col, :] = colRGB


        fluxWidget = QtGui.QWidget()
        fluxLayout = QtGui.QVBoxLayout()
        paletteWidgetFlux = FigureCanvas(self.fluxFig)
        fluxLayout.addWidget(NavigationToolbar(paletteWidgetFlux, self))
        fluxLayout.addWidget(paletteWidgetFlux)
#        self.imFlux,  = self.fluxAx.semilogx(np.array(self.wlScale), self.fluxArray[0, :])
#        self.imFlux,  = self.fluxAx.plot(np.array(self.wlScale), self.fluxArray)

        self.imFlux = self.fluxAx.imshow(histImage, 
#                                           cmap='gnuplot',
                                           extent=(min(energy), max(energy),
                                                   0, 1),
                                           aspect='auto',
                                           interpolation='none',
                                           origin='lower')

        self.fluxFig.subplots_adjust(left=0.15, bottom=0.15, top=0.92)

        fieldWidget = QtGui.QWidget()
        fieldLayout = QtGui.QVBoxLayout()
        paletteWidgetField = FigureCanvas(self.fieldFig)
        fieldLayout.addWidget(NavigationToolbar(paletteWidgetField, self))
        fieldLayout.addWidget(paletteWidgetField)        

#        print(rgbI0slice.shape)
#        print(np.transpose(rgbI0slice))
#        self.fieldAx.imshow(rgbI0sum / rgbI0sum.max(),
#                  extent=[theta[0]*1e6, theta[-1]*1e6, psi[0]*1e6, psi[-1]*1e6])
#    
#        hue = np.array(energy)[:, np.newaxis]
#        hue -= hue.min()
#        hue /= hue.max()
#        sat = np.ones_like(hue)
#        val = np.ones_like(hue)
#    #    hsvC = np.stack((hue, sat, val), axis=2) # numpy1.10
#        hsvC = np.zeros([d for d in hue.shape] + [3])
#        hsvC[:, :, 0] = hue
#        hsvC[:, :, 1] = sat
#        hsvC[:, :, 2] = val
#        rgbC = colors.hsv_to_rgb(hsvC)
#        self.imField = self.fieldAx.imshow(self.plotArray3D[0, :, :].T/np.max(self.plotArray3D[0, :, :]),
        self.imField = self.fieldAx.imshow(rgbI0slice/ rgbI0slice.max(), 
                                           cmap='gnuplot',
                                           extent=(min(theta), max(theta),
                                                   min(psi), max(psi)),
                                           aspect=1,
                                           interpolation='none',
                                           origin='lower')
        self.fieldAx.set_xlabel(r"$\mu$rad")
        self.fieldAx.set_ylabel(r"$\mu$rad")
        self.fieldFig.subplots_adjust(left=0.15, bottom=0.2, top=0.92)

        fluxLayout.addWidget(self.sliderE)

        fluxWidget.setLayout(fluxLayout)
        fieldWidget.setLayout(fieldLayout)
        layout.addWidget(fieldWidget)
        layout.addWidget(fluxWidget)
#        layout.addWidget(self.sliderShift)

        self.setLayout(layout)        

    def update_frame(self, i):
        currentE = self.sliderE.value()
#        currentShift = self.sliderShift.value()
#        self.imField.set_data(self.plotArray3D[currentE, :, :].T/np.max(self.plotArray3D[currentE, :, :]))
        self.imField.set_data(np.transpose(self.rgbI0[currentE, :, :], [1, 0, 2])/np.max(self.rgbI0[currentE, :, :]))

        self.fieldFig.canvas.draw()
        self.fieldFig.canvas.blit()

#        self.imFlux.set_ydata(self.fluxArray[currentShift, :])
        try:
            self.eLine.remove()
        except:
            pass
        self.eLine = self.fluxAx.axvline(
                    self.wlScale[currentE], color='blue', linewidth=1)

        self.fluxFig.suptitle('{} eV'.format(self.wlScale[currentE]))
        self.fluxFig.canvas.draw()
        self.fluxFig.canvas.blit()



if __name__ == '__main__':
    import sys
    app = QtGui.QApplication([])
#    mw = MonitorWidget()
    mw = FluxNavigator()
#    mw.setStyleSheet("background-color: #000")
#    mw.setWindowTitle("Acquaman EXAFS Explorer")
    mw.show()
    sys.exit(app.exec_())        
