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


SEARCH = 1
COPY = 2

class burst_extract_fc(gr.sync_block):
    """
    docstring for block burst_extract_fc
    """
    def __init__(self, len_tag, mult=1):
        gr.sync_block.__init__(self,
            name="burst_extract_fc",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        self.len_tag = len_tag
        self.mult = mult
        self.state = SEARCH
        self.nsym = 0
        self.nsamp = 0
        self.burst_count = 0

    def _add_sob(self):
        pass

    def _add_eob(self):
        pass

    def work(self, input_items, output_items):
        in0 = input_items[0]
        nread = self.nitems_read(0)
        #out = output_items[0]
        tags = self.get_tags_in_window(0, 0, len(in0))
        #print "# of tags", len(tags)
        #print len(in0), tags
        for t in tags:
            key = pmt.symbol_to_string(t.key)
            if key == self.len_tag:
                if self.state == SEARCH:
                    self.state = COPY
                    self.nsym = pmt.to_python(t.value)
                    self.nsamp = self.nsym * self.mult
                    if self.burst_count == 0:
                        self.sob_idx = nread
                        self.eob_idx = self.sob_idx + self.nsamp - 1
                    else:
                        pass
                    print "burst_len: {:d} | sob_idx: {:d} | eob_idx: {:d}".format(self.nsamp, self.sob_idx, self.eob_idx)
                    #add sob tag
                if self.state == COPY:
                    if self.eob_idx >= nread:
                        self.state = SEARCH
                    pass
                #add_sob tag


                #print type(key), key, self.len_tag == key
                #print type(burst_len), burst_len, burst_len * 25
                #print t.key, t.value, t.offset

        output_items[0][:] = (in0)
        nwritten = self.nitems_written(0)
        print "read: {:d}, written: {:d}".format(nread, nwritten)
        return len(output_items[0])
