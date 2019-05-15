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

class burst_snr(gr.sync_block):
    """
    Computes log scale SNR of burst
      'Average Length' is the number of samples for the running average,
      should be less than 100. Applies coorection factor based on samples
      per symbol since we are computing SNR on raw samples before symbol
      recovery.

      sps = samp_rate / baud
      Simple correction ->  SNR = SNR + 10log10(sps)
    """
    def __init__(self,length=100, sps=1):
        gr.sync_block.__init__(self,
            name="burst_snr",
            in_sig=[],
            out_sig=[])
        self.length = length
        self.sps = sps
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handler)
        self.message_port_register_out(pmt.intern('out'))

    def work(self, input_items, output_items):
        assert(False)

    def set_length(self, length):
        self.length = length

    def set_sps(self, sps):
        self.sps = sps

    def handler(self, pdu):
        meta = pmt.car(pdu);
        samples = pmt.cdr(pdu);
        x = numpy.array(pmt.c32vector_elements(samples), dtype=numpy.complex64)
        x_2 = numpy.real(x * x.conjugate()) #mag squared

        # smoothing filter, running average, with 'length' samples
        x_2f = numpy.convolve(self.length*[1], x_2);
        # find max power to compute power thresh
        maxidx = numpy.argmax(x_2f);
        maxpow = x_2f[maxidx];
        # find min power to compute power thresh
        minidx = numpy.argmin(x_2f);
        minpow = x_2f[minidx];
        thr = maxpow / 16; # 6db down from max
        #find avg (or median) of samples above thresh (signal)
        min_avg = numpy.average(x_2f[x_2f<=thr])
        #find avg (or median) of samples below thresh (noise)
        max_avg = numpy.average(x_2f[x_2f>thr])
        #compute log scale snr [dB]
        #already have power of 2 from x_2 calc, so 10log10(snr)
        snr = 10 * numpy.log10(max_avg / min_avg)
        #Correction ratio based on samples per symbol
        snr = snr + 10*numpy.log10(self.sps)
        #add snr to metadata
        meta = pmt.dict_add(meta, pmt.intern("snr"), pmt.from_double(snr));

        samples_out = pmt.init_c32vector(len(x), map(lambda i: complex(i), x))
        cpdu = pmt.cons(meta,samples_out)
        self.message_port_pub(pmt.intern("out"), cpdu);
