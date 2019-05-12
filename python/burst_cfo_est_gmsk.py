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

import numpy
from gnuradio import gr
import json,time,os,pmt,binascii

class burst_cfo_est_gmsk(gr.sync_block):
    """
    docstring for block burst_cfo_est_gmsk
    """
    def __init__(self, Fs = 250000):
        gr.sync_block.__init__(self,
            name="burst_cfo_est_gmsk",
            in_sig=[],
            out_sig=[])
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handler)
        self.message_port_register_out(pmt.intern('out'))
        self.message_port_register_out(pmt.intern('corrected'))

        self.Fs = Fs
        print self.Fs

    def work(self, input_items, output_items):
        assert(false)

    def handler(self, pdu):
        meta = pmt.car(pdu);
        samples = pmt.cdr(pdu);
        x = numpy.array(pmt.c32vector_elements(samples), dtype=numpy.complex64)


        x_pow = numpy.power(x, 2)
        X2 = numpy.fft.fftshift(numpy.absolute(numpy.fft.fft(x_pow)))
        f = numpy.linspace(-self.Fs/2,self.Fs/2,num=len(x_pow))
        #This generates two peaks, find max peak first
        max_1 = numpy.argmax(X2)
        cfo_est_1 = f[max_1]

        #suppress first peak, including +- 10 bins on either side
        pk1_range = numpy.linspace(max_1 - 10, max_1 + 10, 21)
        #print pk1_range, max_1
        for i in pk1_range:
            X2[int(i)] = 0

        #find second peak
        max_2 = numpy.argmax(X2)
        cfo_est_2 = f[max_2]

        #baud rate should be from to ratelines
        baud = numpy.absolute(cfo_est_1-cfo_est_2)

        #find halfway point between the peaks in frequency (not index)
        if (cfo_est_2>cfo_est_1):
            cfo_est = (cfo_est_1 + baud/2.0)/2.0
        elif (cfo_est_2<cfo_est_1):
            cfo_est = (cfo_est_2 + baud/2.0)/2.0


        #print cfo_est_1, cfo_est_2, baud, cfo_est
        #add snr to metadata
        meta = pmt.dict_add(meta, pmt.intern("cfo_est"), pmt.from_double(cfo_est));
        meta = pmt.dict_add(meta, pmt.intern("baud_est"), pmt.from_double(baud));

        # perform the frequency correction
        t0 = numpy.arange(0,len(x),1)/float(self.Fs)
        freqCorrVector = numpy.exp(-1j*2*numpy.pi*cfo_est*t0)
        y = numpy.multiply(x, freqCorrVector)


        x_out = pmt.init_c32vector(len(x), map(lambda i: complex(i), x))
        cpdu_original = pmt.cons(meta,x_out)

        y_out = pmt.init_c32vector(len(y), map(lambda i: complex(i), y))
        cpdu_corrected = pmt.cons(meta,y_out)

        self.message_port_pub(pmt.intern("out"), cpdu_original);
        self.message_port_pub(pmt.intern("corrected"), cpdu_corrected);
