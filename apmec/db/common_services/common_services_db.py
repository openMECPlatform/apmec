# Copyright 2016 Brocade Communications System, Inc.
# All Rights Reserved.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sqlalchemy as sa

from apmec.db import model_base
from apmec.db import types


class Event(model_base.BASE):
    id = sa.Column(sa.Integer, primary_key=True, nullable=False,
                   autoincrement=True)
    resource_id = sa.Column(types.Uuid, nullable=False)
    resource_state = sa.Column(sa.String(64), nullable=False)
    resource_type = sa.Column(sa.String(64), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    event_type = sa.Column(sa.String(64), nullable=False)
    event_details = sa.Column(types.Json)
