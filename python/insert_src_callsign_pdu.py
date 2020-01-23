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
import binascii
import pmt

class insert_src_callsign_pdu(gr.sync_block):
    """
    docstring for block insert_src_callsign_pdu
    """
    def __init__(self, callsign, ssid, verbose):
        gr.sync_block.__init__(self,
            name="insert_src_callsign_pdu",
            in_sig=[],
            out_sig=[])
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handler)
        self.message_port_register_out(pmt.intern('out'))
        self.callsign = callsign
        self.ssid = ssid
        self.verbose = verbose

    def work(self, input_items, output_items):
        assert(false)

    def set_callsign(self, callsign):
        self.callsign = callsign

    def set_ssid(self, ssid):
        self.ssid = ssid

    def set_verbose(self, verbose):
        self.verbose = verbose

    def _decode_callsign(self, call_array):
        call = ""
        for byte in bytearray(call_array): call += chr((byte >> 1) & 0x7F)
        return call.strip()

    def _decode_ssid(self, ssid):
        return int((ssid >> 1) & 0x0F)

    def handler(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return
        ax25 = pmt.to_python(msg)

        if self.verbose:
            print "Original AX.25: {:s}".format(binascii.hexlify(ax25))
            #print ax25, type(ax25)
        EOA_idx = 0 #End Of Address Index
        for i,byte in enumerate(ax25):
            #print "{:d} 0x{:02X} {:08b}".format(i,byte,byte)
            if (byte & 0x01): #should be end of address field
                EOA_idx = i
                break
        addr_cnt = (EOA_idx+1)/7 #count of address field
        #print EOA_idx, addr_cnt, (EOA_idx+1)%7

        # dest_call = ""
        # for byte in ax25[0:6]:
        #     dest_call += chr((byte >> 1) & 0x7F)
        # dest_call = dest_call.strip()
        # dest_ssid = int((ax25[6]>> 1) & 0x0F)
        dest_call = self._decode_callsign(ax25[0:6])
        dest_ssid = self._decode_ssid(ax25[6])

        # src_call = ""
        # for byte in ax25[7:13]:
        #     src_call += chr((byte >> 1) & 0x7F)
        # src_call = dest_call.strip()
        # src_ssid = int((ax25[13]>> 1) & 0x0F)
        src_call = self._decode_callsign(ax25[7:13])
        src_ssid = self._decode_ssid(ax25[13])

        if self.verbose:
            print "Destination Callsign: {:s}-{:d}".format(dest_call, dest_ssid)
            print "     Source Callsign: {:s}-{:d}".format(src_call, src_ssid)
            print " New Source Callsign: {:s}-{:d}".format(self.callsign, self.ssid)

        new_call = []
        for char in self.callsign:
            #print char, ord(char), (ord(char) << 1) & 0xFE
            new_call.append((ord(char) << 1) & 0xFE)
        while len(new_call) < 6:
            new_call.append(0x40)

        new_ssid = (((self.ssid << 1) & 0x1E) | 0x61) & 0xFF

        if self.verbose:
            print " New Source Callsign: {:s}-{:d}".format(self._decode_callsign(new_call),
                                                           self._decode_ssid(new_ssid))

        ax25[7:13] = bytearray(new_call)
        ax25[13] = new_ssid
        if self.verbose:
            print "     New AX.25: {:s}".format(binascii.hexlify(ax25))

        self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(ax25), bytearray(ax25))))
