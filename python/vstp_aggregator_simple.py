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
import pmt,binascii,datetime,json

class vstp_aggregator_simple(gr.sync_block):
    """
    docstring for block vstp_aggregator_simple
    """
    def __init__(self, fc=0.0, l_type="downlink", d_type="live"):
        gr.sync_block.__init__(self,
            name="vstp_aggregator_simple",
            in_sig=[],
            out_sig=[])

        self.fc = fc
        self.meta = {}
        self.meta['version']='v0.0.1'
        self.meta['packet']={}
        self.meta['packet']['center_frequency'] = self.fc
        self.meta['packet']['link_type'] = l_type
        self.meta['packet']['decode_type'] = d_type
        self.message_port_register_in(pmt.intern('meta'))
        self.set_msg_handler(pmt.intern('meta'), self.meta_handler)
        self.message_port_register_in(pmt.intern('raw'))
        self.set_msg_handler(pmt.intern('raw'), self.raw_handler)
        self.message_port_register_out(pmt.intern('out'))

    def work(self, input_items, output_items):
        assert(False)

    def set_center_frequency(self, fc):
        self.fc = fc
        self.meta['packet']['center_frequency'] = self.fc

    def meta_handler(self, meta_pdu):
        meta = pmt.to_python(meta_pdu)
        key = meta[0]
        if key == 'cfo_est':key='frequency_offset'
        val = meta[1]
        self.meta['packet'][key]=val

    def raw_handler(self,raw_pdu):
        ax25_raw = pmt.to_python(pmt.cdr(raw_pdu))
        ax25_hex = binascii.hexlify(ax25_raw)
        self.meta['packet']['raw'] = ax25_hex
        if 'timestamp' not in self.meta['packet'].keys():
            print 'No Timestamp detected, generating now...'
            self.meta['packet']['timestamp'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        metaj = json.dumps(self.meta, indent=4, separators=(',', ': '));
        #metaj = json.dumps(self.meta, sort_keys=True, indent=4, separators=(',', ': '));
        #vstp_msg = pmt.cons(pmt.PMT_NIL, pmt.intern(bytearray(metaj)+'\n'))
        vstp_msg = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(metaj)+1, bytearray(metaj +'\n')))
        self.message_port_pub(pmt.intern("out"), vstp_msg);
