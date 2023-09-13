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

import gzip

import flask  # pylint: disable=E0401

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401
from pylon.core.tools.minio.client import MinIOHelper

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

    @web.slot("tasklets_storage_edit_json_gz_scripts")
    @auth.decorators.check_slot(["tasklets.storage"], access_denied_reply=theme.access_denied_part)
    def _scripts(self, context, slot, payload):
        _ = slot, payload
        #
        minio = MinIOHelper.get_client(self.storage)
        #
        bucket = payload.request.args.get("bucket", None)
        obj = payload.request.args.get("obj", None)
        #
        try:
            data = gzip.decompress(minio.get_object(bucket, obj).read()).decode()
        except:  # pylint: disable=W0702
            log.exception("Edit (.json.gz): get failed for %s:%s", bucket, obj)
            return f'<meta http-equiv="refresh" content="0; url={flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket)}">'
        #
        with context.app.app_context():
            return self.descriptor.render_template(
                "storage_edit/scripts.html",
                **{
                    "save_url": flask.url_for("tasklets.storage_save_json_gz", bucket=bucket, obj=obj),
                    "cancel_url": flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket),
                    "bucket": bucket,
                    "obj": obj,
                    "object_data": data,
                }
            )
