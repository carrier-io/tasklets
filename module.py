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

""" Module """

# import sqlalchemy  # pylint: disable=E0401

from pylon.core.tools import log  # pylint: disable=E0401
from pylon.core.tools import module  # pylint: disable=E0401
from pylon.core.tools.context import Context as Holder  # pylint: disable=E0401

from arbiter.arbiter import Arbiter  # pylint: disable=E0401

from tools import theme  # pylint: disable=E0401

from .scheduler import Scheduler


class Module(module.ModuleModel):
    """ Pylon module """

    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor
        #
        self.storage = self.descriptor.config.get("minio")
        self.storage["endpoint"] = self.storage["endpoint"].replace("http://", "").replace("https://", "").rstrip("/")  # pylint: disable=C0103
        #
        self.arbiter = None
        Scheduler(self).start()

    def init(self):
        """ Init module """
        log.info("Initializing module")
        # Theme registration
        theme.register_section(
            "tasklets", "Tasklets",
            kind="holder",
            permissions=["global_admin"],
            location="left",
            icon_class="fas fa-info-circle fa-fw",
        )
        theme.register_subsection(
            "tasklets",
            "registry", "Registry",
            title="Registry",
            kind="slot",
            permissions=["global_admin"],
            prefix="tasklets_registry_",
            icon_class="fas fa-server fa-fw",
        )
        theme.register_page(
            "tasklets", "registry", "runs",
            title="Tasklet runs",
            kind="slot",
            permissions=["global_admin"],
            prefix="tasklets_registry_runs_",
        )
        theme.register_page(
            "tasklets", "registry", "run_logs",
            title="Tasklet run logs",
            kind="slot",
            permissions=["global_admin"],
            prefix="tasklets_registry_run_logs_",
        )
        theme.register_subsection(
            "tasklets",
            "storage", "Storage",
            title="Storage",
            kind="slot",
            permissions=["global_admin"],
            prefix="tasklets_storage_",
            icon_class="fas fa-server fa-fw",
        )
        theme.register_page(
            "tasklets", "storage", "edit",
            title="Storage edit",
            kind="slot",
            permissions=["global_admin"],
            prefix="tasklets_storage_edit_",
        )
        theme.register_page(
            "tasklets", "storage", "edit_json_gz",
            title="Storage edit (.json.gz)",
            kind="slot",
            permissions=["global_admin"],
            prefix="tasklets_storage_edit_json_gz_",
        )
        theme.register_subsection(
            "tasklets",
            "schedules", "Schedules",
            title="Schedules",
            kind="slot",
            permissions=["global_admin"],
            prefix="tasklets_schedules_",
            icon_class="fas fa-server fa-fw",
        )
        theme.register_subsection(
            "tasklets",
            "runs", "Runs",
            title="Runs",
            kind="slot",
            permissions=["global_admin"],
            prefix="tasklets_runs_",
            icon_class="fas fa-server fa-fw",
        )
        # Init
        self.descriptor.init_all()
        #
        config = self.descriptor.config.get("rabbitmq")
        self.arbiter = Arbiter(
            host=config.get("host"),
            port=int(config.get("port", 5672)),
            user=config.get("user"),
            password=config.get("password"),
            # timeout=config.get("timeout", 15),
            vhost=config.get("vhost", "carrier"),
            all_queue=config.get("all_queue", "tasklets-arbiter-all"),
            start_consumer=True,
        )
        #
        # scheduler

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")
        # De-init
        # self.descriptor.deinit_all()
