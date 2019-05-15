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
import pmt
import datetime

class trigger_timestamp_pdu(gr.sync_block):
    """
    docstring for block trigger_timestamp_pdu
    """
    def __init__(self, threshold=0.0):
        gr.sync_block.__init__(self,
            name="trigger_timestamp_pdu",
            in_sig=[numpy.float32],
            out_sig=[])

        self.threshold = threshold

        self.message_port_register_out(pmt.intern('ts'))

    def set_threshold(self, threshold):
        self.threshold = threshold

    def work(self, input_items, output_items):
        in0 = input_items[0]
        #out = output_items[0]
        idx = numpy.argmax(in0>self.threshold)
        if idx > 0: #triggered
            abs_idx = self.nitems_read(0) + idx
            #print "Triggered!", abs_idx
            ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            #meta = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(buff), buff))
            #meta = pmt.cons(pmt.intern("timestamp"), pmt.init_u8vector(len(ts), bytearray(ts)))
            meta = pmt.cons(pmt.intern("timestamp"), pmt.intern(ts))

            self.message_port_pub(pmt.intern('ts'), meta)
        return len(input_items[0])
        #return len(in[0])
