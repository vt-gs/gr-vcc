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
# note:  code derived from Tim O'Shea's gr-uhdgps'PDU Meta to JSON File block
# ref:  https://github.com/osh/gr-uhdgps

import numpy
from gnuradio import gr
import json,time,os,pmt,binascii

class meta_to_json(gr.sync_block):
    """
    Converts PDU Metadata JSON object then emits out of block
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="meta_to_json",
            in_sig=[],
            out_sig=[])
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handler)
        self.message_port_register_out(pmt.intern('out'))


    def work(self, input_items, output_items):
        assert(False)

    def handler(self, pdu):
        meta = pmt.to_python(pmt.car(pdu))
        #print type(pmt.cdr(pdu))
        msg = pmt.to_python(pmt.cdr(pdu))
        #print type(meta), meta
        meta['msg_hex'] = binascii.hexlify(msg)
        metaj = json.dumps(meta, sort_keys=True, indent=4, separators=(',', ': '));
        #print binascii.hexlify(msg), metaj
        #Create new PDU and emit
        vector = pmt.init_u8vector(len(metaj)+1, bytearray(metaj +'\n'))
        pdu = pmt.cons(pmt.to_pmt(None), vector)
        self.message_port_pub(pmt.intern('out'), pdu)
