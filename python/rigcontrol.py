#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016 <+YOU OR YOUR COMPANY+>.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import numpy
import pmt
from gnuradio import gr


class rigcontrol(gr.sync_block):
    """
    docstring for block rigcontrol
    """
    def __init__(self, freq_set, freq_get, ptt_set, ptt_get):
        gr.sync_block.__init__(self, 'rigcontrol',[],[])
        self.message_port_register_in(pmt.intern('in'))
        self.message_port_register_out(pmt.intern('out'))
        self.set_msg_handler(pmt.intern('in'), self.handler)
        self.freq_set_cb = freq_set
        self.freq_get_cb = freq_get
        self.ptt_set_cb = ptt_set
        self.ptt_get_cb = ptt_get
        self.debug = True

    def handler(self, rigctrl_request):
        # msg_type = pmt.to_long(pmt.tuple_ref(rds_data, 0))
        # msg = pmt.symbol_to_string(pmt.tuple_ref(rds_data, 1))
        # msg = msg.strip()
        request = pmt.to_python(pmt.cdr(rigctrl_request)).tostring().strip()
        request = request.split()
        self.debug_msg('Received Request {}'.format(request[0]))
        if request[0] == 'F':
            self.freq_set(int(request[1]))
        elif request[0] == 'f':
            self.freq_get()
        elif request[0] == 'T':
            self.ptt_set(int(request[1]))
        elif request[0] == 't':
            self.ptt_get()
        elif request[0] == 'q':
            self.debug_msg('Controller Disconnected (Quit Command)')
        else:
            self.debug_msg('Unknown Request Received')
            self.debug_msg('Request: {}'.format(request))
            self.send_response('RPRT 1\n')

    def freq_set(self, f):
        self.debug_msg('Setting frequency to {} Hz'.format(f))
        self.freq_set_cb(f)
        self.send_response('RPRT 0\n')

    def freq_get(self):
        f = self.freq_get_cb()
        self.debug_msg('Request for current frequency: {} Hz'.format(f))
        self.send_response('{}\n'.format(f))

    def ptt_set(self, ptt):
        self.debug_msg('Setting PTT to {}'.format(ptt))
        self.ptt_set_cb(ptt)
        self.send_response('RPRT 0\n')

    def ptt_get(self):
        ptt = self.ptt_get_cb()
        self.debug_msg('Request for current PTT: {}'.format(ptt))
        self.send_response('t: {}\n'.format(ptt))

    def send_response(self, response):
        response_msg = response.strip()
        response = numpy.fromstring(response, dtype=numpy.uint8)
        response = pmt.to_pmt(response)
        response = pmt.cons(pmt.to_pmt(None), response)
        # self.debug_msg('Responding with {}'.format(response_msg))
        self.message_port_pub(pmt.intern('out'), response)

    def debug_msg(self, message):
        if self.debug:
            print 'rigcontrol: {}'.format(message)


    def work(self, input_items, output_items):
        pass
