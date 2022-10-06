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

""" RPC """

import uuid

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401

from tools import mongo  # pylint: disable=E0401
from tools import rpc_tools  # pylint: disable=E0401


class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """

    #
    # Tasklets
    #

    @web.rpc("tasklets_get_by_id", "get_by_id")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_by_id(self, id_):
        tasklet = mongo.db.tasklets_registry.find_one(
            filter={"id": uuid.UUID(id_)}
        )
        if tasklet is not None:
            tasklet = dict(tasklet)
            tasklet.pop("_id")
            tasklet["id"] = str(tasklet["id"])
        return tasklet

    @web.rpc("tasklets_get_by_name", "get_by_name")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_by_name(self, name):
        tasklet = mongo.db.tasklets_registry.find_one(filter={"name": name})
        if tasklet is not None:
            tasklet = dict(tasklet)
            tasklet.pop("_id")
            tasklet["id"] = str(tasklet["id"])
        return tasklet

    @web.rpc("tasklets_get_meta", "get_meta")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_meta(self, id_):
        tasklet = mongo.db.tasklets_registry.find_one(
            filter={"id": uuid.UUID(id_)}
        )
        if tasklet is not None:
            tasklet = dict(tasklet)
            return tasklet.get("meta", dict())
        return dict()

    @web.rpc("tasklets_set_meta", "set_meta")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _set_meta(self, id_, meta):
        tasklet = mongo.db.tasklets_registry.find_one(
            filter={"id": uuid.UUID(id_)}
        )
        if tasklet is not None:
            data = {
                "meta": meta,
            }
            #
            mongo.db.tasklets_registry.update_one(
                {"id": uuid.UUID(id_)},
                {
                    "$set": data,
                },
            )

    #
    # Runs
    #

    @web.rpc("tasklets_get_run", "get_run")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_run(self, id_):
        run = mongo.db.tasklets_runs.find_one(filter={"id": uuid.UUID(id_)})
        if run is not None:
            run = dict(run)
            run.pop("_id")
            run["id"] = str(run["id"])
        return run

    @web.rpc("tasklets_set_run_state", "set_run_state")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _set_run_state(self, id_, state, task_id=..., arbiter_key=...):
        #
        data = {
            "state": state,
        }
        #
        if task_id is not ...:
            data["task_id"] = task_id
        #
        if arbiter_key is not ...:
            data["arbiter_key"] = arbiter_key
        #
        mongo.db.tasklets_runs.update_one(
            {"id": uuid.UUID(id_)},
            {
                "$set": data,
            },
        )

    @web.rpc("tasklets_get_run_result", "get_run_result")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_run_result(self, id_):
        run = mongo.db.tasklets_runs.find_one(filter={"id": uuid.UUID(id_)})
        if run is not None:
            run = dict(run)
            return run.get("result", None)
        return None

    @web.rpc("tasklets_set_run_result", "set_run_result")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _set_run_result(self, id_, result):
        #
        data = {
            "result": result,
        }
        #
        mongo.db.tasklets_runs.update_one(
            {"id": uuid.UUID(id_)},
            {
                "$set": data,
            },
        )

    #
    # Streams and cycles
    #

    @web.rpc("tasklets_get_streams", "get_streams")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_streams(self):
        result = list()
        #
        streams = mongo.db.tasklets_streams.find()
        if not streams:
            return result
        #
        for stream in streams:
            item = dict(stream)
            item.pop("_id")
            result.append(item)
        #
        if not result:
            self.add_stream("Default")
            return self.get_streams()
        #
        return result

    @web.rpc("tasklets_get_stream", "get_stream")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_stream(self, name):
        stream = mongo.db.tasklets_streams.find_one(filter={"name": name})
        if stream is not None:
            stream = dict(stream)
            stream.pop("_id")
        #
        return stream

    @web.rpc("tasklets_get_cycles", "get_cycles")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_cycles(self, stream):
        result = list()
        #
        cycles = mongo.db.tasklets_cycles.find(filter={"stream": stream})
        if not cycles:
            return result
        #
        for cycle in cycles:
            item = dict(cycle)
            item.pop("_id")
            result.append(item)
        #
        if not result:
            self.add_cycle(stream, "Common")
            return self.get_cycles(stream)
        #
        return result

    @web.rpc("tasklets_get_cycle", "get_cycle")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_cycle(self, stream, name):
        cycle = mongo.db.tasklets_cycles.find_one(filter={
            "stream": stream, "name": name
        })
        if cycle is not None:
            cycle = dict(cycle)
            cycle.pop("_id")
        #
        return cycle

    @web.rpc("tasklets_add_stream", "add_stream")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _add_stream(self, name):
        if mongo.db.tasklets_streams.find_one(filter={"name": name}):
            return
        #
        stream = {
            "name": name,
            "meta": dict(),
        }
        #
        mongo.db.tasklets_streams.insert_one(stream)

    @web.rpc("tasklets_add_cycle", "add_cycle")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _add_cycle(self, stream, name):
        if mongo.db.tasklets_cycles.find_one(filter={
                "stream": stream, "name": name
        }):
            return
        #
        cycle = {
            "name": name,
            "stream": stream,
            "meta": dict(),
        }
        #
        mongo.db.tasklets_cycles.insert_one(cycle)

    @web.rpc("tasklets_get_stream_meta", "get_stream_meta")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_stream_meta(self, name):
        stream = mongo.db.tasklets_streams.find_one(
            filter={"name": name}
        )
        if stream is not None:
            stream = dict(stream)
            return stream.get("meta", dict())
        return dict()

    @web.rpc("tasklets_set_stream_meta", "set_stream_meta")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _set_stream_meta(self, name, meta):
        stream = mongo.db.tasklets_streams.find_one(
            filter={"name": name}
        )
        if stream is not None:
            data = {
                "meta": meta,
            }
            #
            mongo.db.tasklets_streams.update_one(
                {"name": name},
                {
                    "$set": data,
                },
            )

    @web.rpc("tasklets_get_cycle_meta", "get_cycle_meta")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_cycle_meta(self, stream, name):
        cycle = mongo.db.tasklets_cycles.find_one(
            filter={"stream": stream, "name": name}
        )
        if cycle is not None:
            cycle = dict(cycle)
            return cycle.get("meta", dict())
        return dict()

    @web.rpc("tasklets_set_cycle_meta", "set_cycle_meta")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _set_cycle_meta(self, stream, name, meta):
        cycle = mongo.db.tasklets_cycles.find_one(
            filter={"stream": stream, "name": name}
        )
        if cycle is not None:
            data = {
                "meta": meta,
            }
            #
            mongo.db.tasklets_cycles.update_one(
                {"stream": stream, "name": name},
                {
                    "$set": data,
                },
            )

    #
    # Run tasklet
    #

    @web.rpc("tasklets_run_tasklet", "run_tasklet")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _run_tasklet(self, name, kvargs=None, stream="Default", cycle="Common", description="", worker="tasklets-worker"):
        #
        if self.get_stream(stream) is None:
            self.add_stream(stream)
        #
        if self.get_cycle(stream, cycle) is None:
            self.add_cycle(stream, cycle)
        #
        run_id = uuid.uuid4()
        #
        run = {
            "id": run_id,
            "stream": stream,
            "cycle": cycle,
            "description": description,
            "tasklet_name": name,
            "kvargs": kvargs,
            "worker": worker,
            "task_id": None,
            "arbiter_key": None,
            "state": "Creating",
        }
        #
        # TODO: ts_start, ts_end
        #
        run_id = str(run_id)
        #
        mongo.db.tasklets_runs.insert_one(run)
        #
        tasklet = self.get_by_name(name)
        if tasklet is None:
            log.error("No such task")
            self.set_run_state(run_id, "Failed")
            return run_id
        #
        configuration = self.descriptor.config.get("runner", dict())
        configuration["runner"] = {
            "run_id": run_id,
            "worker": worker,
            "kvargs": kvargs,
        }
        configuration["tasklet"] = tasklet
        #
        if "loki" in configuration.get("pylon", dict()):
            configuration["pylon"]["loki"]["labels"] = {
                "log_type": "tasklet",
                "run_id": run_id,
            }
        #
        log.info("Tasklet config: %s", configuration)
        #
        task_keys = self.arbiter.apply(
            "run_tasklet",
            queue=worker, tasks_count=1,
            task_args=None, task_kwargs={"configuration": configuration},
            sync=False,
        )
        #
        self.set_run_state(run_id, "Created", tasklet["id"], task_keys[0])
        #
        return run_id
