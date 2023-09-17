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
import json
import datetime

import flask  # pylint: disable=E0401,W0611
import flask_restful  # pylint: disable=E0401
import croniter  # pylint: disable=E0401,W0611

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

    @auth.decorators.check_api(["tasklets.schedules"], mode="tasklets")
    def get(self):  # pylint: disable=R0201
        """ Process GET """
        result = list()
        #
        query_filter = {}
        #
        for item in mongo.db.tasklets_schedules.find(
            filter=query_filter,
            skip=int(flask.request.args.get("offset", 0)),
            limit=int(flask.request.args.get("limit", 0)),
        ):
            data = dict(item)
            #
            data.pop("_id")
            data["id"] = str(data["id"])
            #
            if not data.get("schedule", "").strip():
                data["next_run"] = "-"
            else:
                current_iter = croniter.croniter(data["schedule"], datetime.datetime.strptime(data["base_time"], "%Y.%m.%d %H:%M:%S"))  # pylint: disable=C0301
                data["next_run"] = current_iter.get_next(datetime.datetime).strftime("%Y.%m.%d %H:%M:%S")  # pylint: disable=C0301
            #
            result.append(data)
        #
        return {
            "total": mongo.db.tasklets_schedules.count_documents(
                filter=query_filter
            ),
            "rows": result,
        }

    @auth.decorators.check_api(["tasklets.schedules"], mode="tasklets")
    def post(self):  # pylint: disable=R0201
        """ Process POST """
        data = flask.request.get_json()  # TODO: validation with pydantic
        #
        data["id"] = uuid.uuid4()
        data["enabled"] = True
        data["base_time"] = datetime.datetime.now().strftime(
            "%Y.%m.%d %H:%M:%S"
        )
        data["last_run"] = "-"
        #
        mongo.db.tasklets_schedules.insert_one(data)
        #
        return {"ok": True}

    @auth.decorators.check_api(["tasklets.schedules"], mode="tasklets")
    def delete(self):  # pylint: disable=R0201
        """ Process DELETE """
        data = flask.request.args  # TODO: validation with pydantic
        #
        if not mongo.db.tasklets_schedules.find_one(filter={"id": uuid.UUID(data["id"])}):
            log.info("No such schedule")
            return {"ok": False}
        #
        mongo.db.tasklets_schedules.delete_one({"id": uuid.UUID(data["id"])})
        #
        return {"ok": True}

    @auth.decorators.check_api(["tasklets.schedules"], mode="tasklets")
    def put(self):  # pylint: disable=R0201
        """ Process PUT """
        id_ = flask.request.args.get("id")  # TODO: validation with pydantic
        action = flask.request.args.get("action")
        #
        log.info("ID/action: %s:%s", id_, action)
        #
        if not mongo.db.tasklets_schedules.find_one(filter={"id": uuid.UUID(id_)}):
            log.info("No such schedule")
            return {"ok": False}
        #
        if action == "enable":
            mongo.db.tasklets_schedules.update_one(
                {"id": uuid.UUID(id_)},
                {
                    "$set": {
                        "enabled": True
                    },
                },
            )
        elif action == "disable":
            mongo.db.tasklets_schedules.update_one(
                {"id": uuid.UUID(id_)},
                {
                    "$set": {
                        "enabled": False
                    },
                },
            )
        elif action == "run":
            schedule = mongo.db.tasklets_schedules.find_one(filter={"id": uuid.UUID(id_)})
            schedule = dict(schedule)
            #
            name = schedule["tasklet"]
            #
            try:
                kvargs = json.loads(schedule["kvargs"])
            except:  # pylint: disable=W0702
                log.exception("Failed to load KVargs, using empty")
                kvargs = None
            #
            stream = schedule["stream"]
            cycle = schedule["cycle"]
            description = schedule["run_description"]
            worker = schedule["worker"]
            #
            run_id = self.module.run_tasklet(
                name, kvargs=kvargs,
                stream=stream, cycle=cycle,
                description=description,
                worker=worker
            )
            #
            log.info("Run ID: %s", run_id)
        #
        return {"ok": True}
