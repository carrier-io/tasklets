#!/usr/bin/python3
# coding=utf-8

#   Copyright 2022 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

""" Slot """

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401

from tools import auth  # pylint: disable=E0401
from tools import theme  # pylint: disable=E0401


class Slot:  # pylint: disable=E1101,R0903
    """
        Slot Resource

        self is pointing to current Module instance

        web.slot decorator takes one argument: slot name
        Note: web.slot decorator must be the last decorator (at top)

        Slot resources use check_slot auth decorator
        auth.decorators.check_slot takes the following arguments:
        - permissions
        - scope_id=1
        - access_denied_reply=None -> can be set to content to return in case of 'access denied'

    """

    @web.slot("tasklets_runs_scripts")
    @auth.decorators.check_slot(["global_admin"], access_denied_reply=theme.access_denied_part)
    def _scripts(self, context, slot, payload):
        _ = slot
        #
        stream = payload.request.args.get("stream", None)
        cycle = payload.request.args.get("cycle", None)
        #
        streams = self.get_streams()
        active_stream = None
        #
        for item in streams:
            if item["name"] == stream:
                active_stream = item["name"]
        #
        if not active_stream and streams:
            active_stream = streams[0]["name"]
        #
        cycles = self.get_cycles(active_stream)
        active_cycle = None
        #
        for item in cycles:
            if item["name"] == cycle:
                active_cycle = item["name"]
        #
        if not active_cycle and cycles:
            active_cycle = cycles[0]["name"]
        #
        with context.app.app_context():
            return self.descriptor.render_template(
                "runs/scripts.html",
                streams=streams,
                cycles=cycles,
                active_stream=active_stream,
                active_cycle=active_cycle,
            )
