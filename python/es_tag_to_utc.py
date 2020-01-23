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
import json,time,os,pmt,binascii, math, datetime

class es_tag_to_utc(gr.sync_block):
    """
    Event Stream Time Stamp Generator

    uses the event stream 'es::event_time' tag and the 'rx_time' tag to generate an ISO 8601 timestamp.

    samp_rate is needed to convert the proper event time value.
    """
    def __init__(self, samp_rate):
        gr.sync_block.__init__(self,
            name="es_tag_to_utc",
            in_sig=[],
            out_sig=[])

        self.samp_rate = samp_rate
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handler)
        self.message_port_register_out(pmt.intern('out'))


    def work(self, input_items, output_items):
        assert(False)

    def handler(self, pdu):
        meta = pmt.to_python(pmt.car(pdu))
        samples = pmt.cdr(pdu)
        x = numpy.array(pmt.c32vector_elements(samples), dtype=numpy.complex64)
        #print meta
        #print meta['rx_time'], meta['es::event_time']
        time_delta = meta['es::event_time'] / self.samp_rate
        rx_int_sec = meta['rx_time'][1][0]
        rx_frac_sec = meta['rx_time'][1][1]
        #print rx_int_sec, rx_frac_sec
        #print time_delta, math.modf(time_delta)

        td = math.modf(time_delta)
        dt = (numpy.int64(rx_int_sec + td[1]) , rx_frac_sec + td[0])
        #print datetime
        ts = numpy.datetime64(datetime.datetime.utcfromtimestamp(dt[0]))
        ts = ts + numpy.timedelta64(int(dt[1]*1e9), 'ns')
        ts_ns = numpy.datetime_as_string(ts) +"Z"

        meta = pmt.to_pmt(meta)
        #meta = pmt.dict_add(meta, pmt.intern("pkt_rx_time"), pmt.make_tuple(dt));
        meta = pmt.dict_add(meta, pmt.intern("datetime"), pmt.string_to_symbol(ts_ns));
        #meta['pkt_rx_time'] = dt
        #meta['datetime'] = ts_ns

        samples_out = pmt.init_c32vector(len(x), map(lambda i: complex(i), x))
        cpdu = pmt.cons(meta,samples_out)
        self.message_port_pub(pmt.intern("out"), cpdu);

        #print meta
