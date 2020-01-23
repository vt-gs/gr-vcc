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
import datetime
import pmt

class insert_time_tag_bb(gr.sync_block):
    """
    Inserts Datetime timestamp as stream tag.
    Intent is to add timestamp annotations in SigMF

    Datetime Key:  Key to insert in metadata
    Trigger Key:  Key to look for and add datetime at same sample index
    """
    def __init__(self, dt_key, trig_key):
        gr.sync_block.__init__(self,
            name="insert_time_tag_bb",
            in_sig=[numpy.uint8],
            out_sig=[numpy.uint8])
        self.dt_key = dt_key
        self.trig_key = trig_key


    def work(self, input_items, output_items):
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        in0 = input_items[0]
        out = output_items[0]
        tags = self.get_tags_in_window(0, 0, len(in0))
        if len(tags) > 0:
            for t in tags:
                t_key = pmt.symbol_to_string(t.key)
                #t_val = pmt.to_python(t.value)
                t_offset = t.offset
                if t_key == self.trig_key:
                    key = pmt.intern(self.dt_key)
                    val = pmt.intern(ts)
                    self.add_item_tag(0,t_offset,key,val)

        out[:] = in0
        return len(output_items[0])
