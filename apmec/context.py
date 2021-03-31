# Copyright 2012 OpenStack Foundation.
# All Rights Reserved.
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

"""Context: context for security/db session."""

import copy
import datetime

from oslo_context import context as oslo_context
from oslo_db.sqlalchemy import enginefacade

from apmec.db import api as db_api
from apmec import policy


class ContextBase(oslo_context.RequestContext):
    """Security context and request information.

    Represents the user taking a given action within the system.

    """

    def __init__(self, user_id, tenant_id, is_admin=None, roles=None,
                 timestamp=None, request_id=None, tenant_name=None,
                 user_name=None, overwrite=True, auth_token=None,
                 **kwargs):
        """Object initialization.

        :param overwrite: Set to False to ensure that the greenthread local
            copy of the index is not overwritten.

        :param kwargs: Extra arguments that might be present, but we ignore
            because they possibly came in from older rpc messages.
        """
        super(ContextBase, self).__init__(auth_token=auth_token,
                                          user=user_id, tenant=tenant_id,
                                          is_admin=is_admin,
                                          request_id=request_id,
                                          overwrite=overwrite,
                                          roles=roles)
        self.user_name = user_name
        self.tenant_name = tenant_name

        if not timestamp:
            timestamp = datetime.datetime.utcnow()
        self.timestamp = timestamp
        if self.is_admin is None:
            self.is_admin = policy.check_is_admin(self)

    @property
    def project_id(self):
        return self.tenant

    @property
    def tenant_id(self):
        return self.tenant

    @tenant_id.setter
    def tenant_id(self, tenant_id):
        self.tenant = tenant_id

    @property
    def user_id(self):
        return self.user

    @user_id.setter
    def user_id(self, user_id):
        self.user = user_id

    def to_dict(self):
        context = super(ContextBase, self).to_dict()
        context.update({
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'project_id': self.project_id,
            'timestamp': str(self.timestamp),
            'tenant_name': self.tenant_name,
            'project_name': self.tenant_name,
            'user_name': self.user_name,
        })
        return context

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    def elevated(self):
        """Return a version of this context with admin flag set."""
        context = copy.copy(self)
        context.is_admin = True

        if 'admin' not in [x.lower() for x in context.roles]:
            context.roles = context.roles + ["admin"]

        return context


@enginefacade.transaction_context_provider
class ContextBaseWithSession(ContextBase):
    pass


class Context(ContextBaseWithSession):
    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)
        self._session = None

    @property
    def session(self):
        # TODO(akamyshnikova): checking for session attribute won't be needed
        # when reader and writer will be used
        if hasattr(super(Context, self), 'session'):
            return super(Context, self).session
        if self._session is None:
            self._session = db_api.get_session()
        return self._session


def get_admin_context():
    return Context(user_id=None,
                   tenant_id=None,
                   is_admin=True,
                   overwrite=False)


def get_admin_context_without_session():
    return ContextBase(user_id=None,
                       tenant_id=None,
                       is_admin=True)
