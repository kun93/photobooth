#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2018  Balthasar Reuter <photobooth at re - web dot eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging

from PyQt5 import QtCore, QtGui
from PyQt5.QtPrintSupport import QPrinter

from . import Printer
from PIL import Image, ImageOps, ImageFilter, ImageQt


class PrinterPyQt5(Printer):

    def __init__(self, page_size, print_pdf=False):

        super().__init__(page_size)

        self._printer = QPrinter(QPrinter.HighResolution)
        self._printer.setPageSize(QtGui.QPageSize(QtCore.QSizeF(*page_size),
                                                  QtGui.QPageSize.Millimeter))
        self._printer.setColorMode(QPrinter.Color)

        logging.info('Using printer "%s"', self._printer.printerName())

        self._print_pdf = print_pdf
        if self._print_pdf:
            logging.info('Using PDF printer')
            self._counter = 0
            self._printer.setOutputFormat(QPrinter.PdfFormat)
            self._printer.setFullPage(True)

    def print(self, pictures):
    
        logging.info ("Generating printout compilation")
        
        x = 547
        y = 365
        x1 = 16
        y1 = 26
        x2 = 636
        abstand_y = 365+31
        border = 10

        pic = Image.open("/home/pi/photobooth/template.jpg").copy()

        for n in range(4):

            shot = Image.open(pictures[n])
            shot = ImageOps.expand(shot, border=(border,border))
            shot.thumbnail((x,y))
            # left
            resized = shot.crop((0,0,x,y))
            box = (x1, y1+n*abstand_y, x+x1, y+y1+n*abstand_y)
            pic.paste(resized, box)
            # right
            shot = shot.convert('L').filter(ImageFilter.SHARPEN)
            resized = shot.crop((0,0,x,y))
            box = (x2, y1+n*abstand_y, x+x2, y+y1+n*abstand_y)
            pic.paste(resized, box)

        #logging.info ("writing compiled image to disk")
        #pic.save(time.strftime("%Y-%m-%d/%Hh%Ms%S.png"))
        
        picture = ImageQt.ImageQt(pic)

        if self._print_pdf:
            self._printer.setOutputFileName('print_%d.pdf' % self._counter)
            self._counter += 1

        logging.info('Printing picture')

        picture = picture.scaled(self._printer.paperRect().size(),
                                 QtCore.Qt.KeepAspectRatio,
                                 QtCore.Qt.SmoothTransformation)

        printable_size = self._printer.pageRect(QPrinter.DevicePixel)
        origin = ((printable_size.width() - picture.width()) // 2,
                  (printable_size.height() - picture.height()) // 2)

        painter = QtGui.QPainter(self._printer)
        painter.drawImage(QtCore.QPoint(*origin), picture)
        painter.end()
