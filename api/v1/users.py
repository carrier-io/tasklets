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

import flask  # pylint: disable=E0401,W0611
import flask_restful  # pylint: disable=E0401

from pylon.core.tools import log  # pylint: disable=E0611,E0401,W0611

from tools import auth  # pylint: disable=E0401
from tools import mongo  # pylint: disable=E0401
from tools import theme  # pylint: disable=E0401
from tools import api_tools  # pylint: disable=E0401


class AdminAPI(api_tools.APIModeHandler):  # pylint: disable=R0903
    @auth.decorators.check_api(["modes.users"])
    def get(self, target_mode):  # pylint: disable=R0201
        """ Process GET """
        result = list()
        #
        users = self.context.rpc_manager.call.auth_list_users()
        #
        for mode_key in theme.modes:
            for user in users:
                user_roles = self.context.rpc_manager.call.auth_get_user_roles(user["id"], mode_key)
                #
                for role in user_roles:
                    log.info("%s - %s - %s", user, mode_key, role)
        #
        return {
            "total": len(result),
            "rows": result,
        }

    @auth.decorators.check_api(["modes.users"])
    def post(self, target_mode):  # pylint: disable=R0201
        """ Process POST """
        data = flask.request.get_json()  # TODO: validation with pydantic
        #
        if mongo.db.tasklets_registry.find_one(filter={"name": data.get("name", "")}):
            log.info("Task with same name already exists")
            return {"ok": False}
        #
        data["id"] = uuid.uuid4()
        mongo.db.tasklets_registry.insert_one(data)
        #
        return {"ok": True}

    @auth.decorators.check_api(["modes.users"])
    def delete(self, target_mode):  # pylint: disable=R0201
        """ Process DELETE """
        # data = flask.request.args  # TODO: validation with pydantic
        # #
        # if not mongo.db.tasklets_registry.find_one(filter={"id": uuid.UUID(data["id"])}):
        #     log.info("No such task")
        #     return {"ok": False}
        # #
        # mongo.db.tasklets_registry.delete_one({"id": uuid.UUID(data["id"])})
        # #
        # # TODO: delete task runs and artifacts
        # #
        return {"ok": True}


class API(api_tools.APIBase):  # pylint: disable=R0903
    url_params = [
        "<string:target_mode>",
    ]

    mode_handlers = {
        'administration': AdminAPI,
    }
