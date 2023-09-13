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

""" Route """

import io
import gzip

import flask  # pylint: disable=E0401

from pylon.core.tools import log  # pylint: disable=E0611,E0401,W0611
from pylon.core.tools import web  # pylint: disable=E0611,E0401

from pylon.core.tools.minio.client import MinIOHelper

from tools import auth  # pylint: disable=E0401


class Route:  # pylint: disable=E1101,R0903
    """
        Route Resource

        self is pointing to current Module instance

        By default routes are prefixed with module name
        Example:
        - pylon is at "https://example.com/"
        - module name is "demo"
        - route is "/"
        Route URL: https://example.com/demo/

        web.route decorator takes the same arguments as Flask route
        Note: web.route decorator must be the last decorator (at top)

        Route resources use check auth decorator
        auth.decorators.check takes the following arguments:
        - permissions
        - scope_id=1
    """


    @web.route("/storage_bucket_create", methods=["POST"])
    @auth.decorators.check(["tasklets.storage"], mode="tasklets")
    def storage_bucket_create(self):  # pylint: disable=R0201
        """ Route """
        #
        minio = MinIOHelper.get_client(self.storage)
        #
        if flask.request.method == "POST" and "bucket" in flask.request.form:
            bucket = flask.request.form["bucket"]
            #
            try:
                minio.make_bucket(bucket)
            except:  # pylint: disable=W0702
                log.exception("Create failed for %s", bucket)
        #
        return flask.redirect(flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket))

    @web.route("/storage_bucket_delete")
    @auth.decorators.check(["tasklets.storage"])
    def storage_bucket_delete(self):  # pylint: disable=R0201
        """ Route """
        #
        minio = MinIOHelper.get_client(self.storage)
        #
        bucket = flask.request.args.get("bucket", None)
        #
        try:
            minio.remove_bucket(bucket)
        except:  # pylint: disable=W0702
            log.exception("Remove failed for %s", bucket)
        #
        return flask.redirect(flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket))

    @web.route("/storage_upload", methods=["POST"])
    @auth.decorators.check(["tasklets.storage"])
    def storage_upload(self):  # pylint: disable=R0201
        """ Route """
        #
        minio = MinIOHelper.get_client(self.storage)
        #
        bucket = flask.request.args.get("bucket", None)
        #
        if flask.request.method == "POST" and "fileobj" in flask.request.files:
            fileobj = flask.request.files["fileobj"]
            try:
                obj_data = b""
                obj_size = 0
                while True:
                    data = fileobj.read(8192)
                    if not data:
                        break
                    obj_data += data
                    obj_size += len(data)
                minio.put_object(bucket, fileobj.filename, io.BytesIO(obj_data), obj_size)
            except:  # pylint: disable=W0702
                log.exception("Upload failed for %s:%s", bucket, fileobj.filename)
        #
        return flask.redirect(flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket))

    @web.route("/storage_save", methods=["POST"])
    @auth.decorators.check(["tasklets.storage"])
    def storage_save(self):  # pylint: disable=R0201
        """ Route """
        #
        minio = MinIOHelper.get_client(self.storage)
        #
        bucket = flask.request.args.get("bucket", None)
        obj = flask.request.args.get("obj", None)
        #
        if flask.request.method == "POST" and "data" in flask.request.form:
            data = flask.request.form["data"]
            try:
                data = data.encode()
                minio.put_object(bucket, obj, io.BytesIO(data), len(data))
            except:  # pylint: disable=W0702
                log.exception("Edit: save failed for %s:%s", bucket, obj)
        #
        return flask.redirect(flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket))

    @web.route("/storage_save_json_gz", methods=["POST"])
    @auth.decorators.check(["tasklets.storage"])
    def storage_save_json_gz(self):  # pylint: disable=R0201
        """ Route """
        #
        minio = MinIOHelper.get_client(self.storage)
        #
        bucket = flask.request.args.get("bucket", None)
        obj = flask.request.args.get("obj", None)
        #
        if flask.request.method == "POST" and "data" in flask.request.form:
            data = flask.request.form["data"]
            try:
                data = gzip.compress(data.encode())
                minio.put_object(bucket, obj, io.BytesIO(data), len(data))
            except:  # pylint: disable=W0702
                log.exception("Edit (.json.gz): save failed for %s:%s", bucket, obj)
        #
        return flask.redirect(flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket))

    @web.route("/storage_view")
    @auth.decorators.check(["tasklets.storage"])
    def storage_view(self):  # pylint: disable=R0201
        """ Route """
        #
        minio = MinIOHelper.get_client(self.storage)
        #
        bucket = flask.request.args.get("bucket", None)
        obj = flask.request.args.get("obj", None)
        #
        try:
            data = minio.get_object(bucket, obj).read().decode()
        except:  # pylint: disable=W0702
            log.exception("View: get failed for %s:%s", bucket, obj)
            return flask.redirect(flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket))
        #
        return data

    @web.route("/storage_download")
    @auth.decorators.check(["tasklets.storage"])
    def storage_download(self):  # pylint: disable=R0201
        """ Route """
        #
        minio = MinIOHelper.get_client(self.storage)
        #
        bucket = flask.request.args.get("bucket", None)
        obj = flask.request.args.get("obj", None)
        #
        try:
            data = minio.get_object(bucket, obj)
            try:
                return flask.send_file(data, attachment_filename=obj)
            except TypeError:  # new flask
                return flask.send_file(data, download_name=obj, as_attachment=True)
        except:  # pylint: disable=W0702
            log.exception("Download failed for %s:%s", bucket, obj)
        #
        return flask.redirect(flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket))

    @web.route("/storage_delete")
    @auth.decorators.check(["tasklets.storage"])
    def storage_delete(self):  # pylint: disable=R0201
        """ Route """
        #
        minio = MinIOHelper.get_client(self.storage)
        #
        bucket = flask.request.args.get("bucket", None)
        obj = flask.request.args.get("obj", None)
        #
        try:
            minio.remove_object(bucket, obj)
        except:  # pylint: disable=W0702
            log.exception("Delete failed for %s:%s", bucket, obj)
        #
        return flask.redirect(flask.url_for("theme.route_mode_section_subsection", mode="tasklets", section="tasklets", subsection="storage", bucket=bucket))
