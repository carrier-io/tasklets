#!/usr/bin/python
# coding=utf-8
# pylint: disable=I0011

#   Copyright 2022
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

"""
    Scheduler for tasklets
"""

import json
import uuid
import time
import datetime
import threading

import croniter

from pylon.core.tools import log  # pylint: disable=E0611,E0401,W0611

from tools import mongo  # pylint: disable=E0401


class Scheduler(threading.Thread):
    """ Checks if it is time to run tasklet """

    def __init__(self, module):
        super().__init__(daemon=True)
        self.module = module

    def run(self):
        """ Run scheduler thread """
        log.info("Starting tasklet scheduler thread")
        while True:
            time.sleep(1.0)
            try:
                self.check_scheduled_tasks()
            except:  # pylint: disable=W0702
                log.exception("Error during scheduled tasklet check")

    def check_scheduled_tasks(self):
        """ Check and run tasklets """
        current_time = datetime.datetime.now()
        #
        for item in mongo.db.tasklets_schedules.find():
            data = dict(item)
            #
            data.pop("_id")
            data["id"] = str(data["id"])
            #
            if not data.get("schedule", "").strip():
                continue
            #
            current_iter = croniter.croniter(data["schedule"], datetime.datetime.strptime(data["base_time"], "%Y.%m.%d %H:%M:%S"))  # pylint: disable=C0301
            if current_iter.get_next(datetime.datetime) <= current_time:
                schedule = data
                #
                if data.get("enabled", True):
                    log.info("Running scheduled tasklet: %s - %s - %s", data["id"], data["description"], data["tasklet"])
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
                    mongo.db.tasklets_schedules.update_one(
                        {"id": uuid.UUID(schedule["id"])},
                        {
                            "$set": {
                                "last_run": current_time.strftime("%Y.%m.%d %H:%M:%S")
                            },
                        },
                    )
                #
                mongo.db.tasklets_schedules.update_one(
                    {"id": uuid.UUID(schedule["id"])},
                    {
                        "$set": {
                            "base_time": (current_time + datetime.timedelta(seconds=1)).strftime("%Y.%m.%d %H:%M:%S")  # pylint: disable=C0301
                        },
                    },
                )
