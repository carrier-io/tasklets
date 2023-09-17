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

""" API """

import uuid

import flask  # pylint: disable=E0401,W0611
import flask_restful  # pylint: disable=E0401

from pylon.core.tools import log  # pylint: disable=E0611,E0401,W0611

from tools import auth  # pylint: disable=E0401
from tools import mongo  # pylint: disable=E0401


class API(flask_restful.Resource):  # pylint: disable=R0903
    """
        API Resource

        Endpoint URL structure: <pylon_root>/api/<api_version>/<plugin_name>/<resource_name>

        Example:
        - Pylon root is at "https://example.com/"
        - Plugin name is "demo"
        - We are in subfolder "v1"
        - Current file name is "myapi.py"

        API URL: https://example.com/api/v1/demo/myapi

        API resources use check_api auth decorator
        auth.decorators.check_api takes the following arguments:
        - permissions
        - scope_id=1
        - access_denied_reply={"ok": False, "error": "access_denied"},
    """


    def __init__(self, module):
        self.module = module

    @auth.decorators.check_api(["tasklets.registry"], mode="tasklets")
    def get(self):  # pylint: disable=R0201
        """ Process GET """
        result = list()
        #
        target_name = flask.request.args.get("name", None)
        target_stream = flask.request.args.get("stream", None)
        target_cycle = flask.request.args.get("cycle", None)
        #
        query_filter = {}
        #
        if target_name is not None:
            query_filter["tasklet_name"] = target_name
        if target_stream is not None:
            query_filter["stream"] = target_stream
        if target_cycle is not None:
            query_filter["cycle"] = target_cycle
        #
        for item in mongo.db.tasklets_runs.find(
            filter=query_filter,
            skip=int(flask.request.args.get("offset", 0)),
            limit=int(flask.request.args.get("limit", 0)),
        ):
            data = dict(item)
            #
            data.pop("_id")
            data["id"] = str(data["id"])
            #
            result.append(data)
        #
        return {
            "total": mongo.db.tasklets_runs.count_documents(
                filter=query_filter
            ),
            "rows": result,
        }

    @auth.decorators.check_api(["tasklets.registry"], mode="tasklets")
    def put(self):  # pylint: disable=R0201
        """ Process PUT """
        run_id = flask.request.args.get("id")  # TODO: validation with pydantic
        #
        run = self.module.get_run(run_id)
        if run is None:
            return {"ok": False}
        #
        log.info("Re-running: %s", run)
        #
        run_id = self.module.run_tasklet(
            run["tasklet_name"], kvargs=run["kvargs"],
            stream=run["stream"], cycle=run["cycle"],
            description=f'[Re-run] {run["description"]}',
            worker=run["worker"]
        )
        #
        log.info("Run ID: %s", run_id)
        #
        return {"ok": True}
