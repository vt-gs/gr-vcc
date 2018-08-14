#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2018 Virginia Tech Ground Station
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# note:  code derived from Tim O'Shea's gr-pyqt 'Text Output' block'
# ref:  https://github.com/osh/gr-pyqt

import numpy
from gnuradio import gr
from PyQt4 import Qt, QtCore, QtGui
import pmt
import binascii

class qt_hex_text(gr.sync_block):
    """
    prints the hex string using binascii.hexlify
    """
    __pyqtSignals__ = ("updateText(QString)")
    def __init__(self,  blkname="qt_hex_text", label="", *args):
        gr.sync_block.__init__(self,
            name=blkname,
            in_sig=[],
            out_sig=[])

        QtGui.QTextEdit.__init__(self, *args)
        self.message_port_register_in(pmt.intern("pdus"));
        self.set_msg_handler(pmt.intern("pdus"), self.handle_input);
        # connect the plot callback signal
        QtCore.QObject.connect(self,
                       QtCore.SIGNAL("updateText(QString)"),
                       self,
                       QtCore.SLOT("append(QString)"))

    def handle_input(self, msg):
        vec = pmt.cdr(msg)
        nvec = pmt.to_python(vec)
        #s = str(nvec.tostring())  #O'Shea's original line
        s = binascii.hexlify(nvec)
        self.emit(QtCore.SIGNAL("updateText(QString)"), s)

    def work(self, input_items, output_items):
        pass
