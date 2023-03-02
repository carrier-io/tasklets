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

import time

# from pylon.core.tools import log  # pylint: disable=E0611,E0401
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

    @web.slot("tasklets_registry_run_logs_content")
    @auth.decorators.check_slot(["global_admin"], access_denied_reply=theme.access_denied_part)
    def _content(self, context, slot, payload):
        _ = slot, payload
        #
        run_id = payload.request.args.get("id", None)
        #
        websocket_base_url = self.context.settings["loki"]["url"]
        websocket_query_url = websocket_base_url.replace("api/v1/push", "api/v1/query_range")
        #
        websocket_base_url = websocket_base_url.replace("http://", "ws://")
        websocket_base_url = websocket_base_url.replace("https://", "wss://")
        websocket_base_url = websocket_base_url.replace("api/v1/push", "api/v1/tail")
        #
        logs_query = "{" + f'log_type="tasklet",run_id="{run_id}"' + "}"
        logs_ts_now = int(time.time() * 1000000000)
        #
        websocket_url = f"{websocket_base_url}?query={logs_query}"
        #
        with context.app.app_context():
            return self.descriptor.render_template(
                "registry_run_logs/content.html",
                run_websocket_url=websocket_url,
                query_websocket_url=websocket_query_url,
                logs_ts_now=logs_ts_now,
            )

    @web.slot("tasklets_registry_run_logs_scripts")
    @auth.decorators.check_slot(["global_admin"], access_denied_reply=theme.access_denied_part)
    def _scripts(self, context, slot, payload):
        _ = slot, payload
        #
        with context.app.app_context():
            return self.descriptor.render_template(
                "registry_run_logs/scripts.html",
            )
