# -*- coding: utf-8 -*-
#
# Copyright 2013 - Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from mistral.db.sqlalchemy import model_base as mb
from mistral.db.sqlalchemy import types as st


class Workbook(mb.MistralModelBase):
    """Contains info about workbook (including definition in Mistral DSL)."""

    __tablename__ = 'workbooks_v2'

    __table_args__ = (
        sa.UniqueConstraint('name'),
    )

    id = mb._id_column()
    name = sa.Column(sa.String(80), primary_key=True)
    definition = sa.Column(sa.Text(), nullable=True)
    spec = sa.Column(st.JsonDictType())
    tags = sa.Column(st.JsonListType())
    scope = sa.Column(sa.String(80))
    project_id = sa.Column(sa.String(80))
    trust_id = sa.Column(sa.String(80))


class Workflow(mb.MistralModelBase):
    """Contains info about workflow (including definition in Mistral DSL)."""

    __tablename__ = 'workflows_v2'

    __table_args__ = (
        sa.UniqueConstraint('name'),
    )

    id = mb._id_column()
    name = sa.Column(sa.String(80), primary_key=True)
    definition = sa.Column(sa.Text(), nullable=True)
    spec = sa.Column(st.JsonDictType())
    tags = sa.Column(st.JsonListType())
    scope = sa.Column(sa.String(80))
    project_id = sa.Column(sa.String(80))
    trust_id = sa.Column(sa.String(80))


class Execution(mb.MistralModelBase):
    """Contains workflow execution information."""

    __tablename__ = 'executions_v2'

    id = mb._id_column()
    wf_spec = sa.Column(st.JsonDictType())
    start_params = sa.Column(st.JsonDictType())
    state = sa.Column(sa.String(20))
    input = sa.Column(st.JsonDictType())
    output = sa.Column(st.JsonDictType())
    context = sa.Column(st.JsonDictType())
    # Can't use ForeignKey constraint here because SqlAlchemy will detect
    # a circular dependency and raise an error.
    parent_task_id = sa.Column(sa.String(36))


class Task(mb.MistralModelBase):
    """Contains task runtime information."""

    __tablename__ = 'tasks_v2'

    # Main properties.
    id = mb._id_column()
    name = sa.Column(sa.String(80))
    wf_name = sa.Column(sa.String(80))
    spec = sa.Column(st.JsonDictType())
    action_spec = sa.Column(st.JsonDictType())
    state = sa.Column(sa.String(20))
    tags = sa.Column(st.JsonListType())

    # Data Flow properties.
    in_context = sa.Column(st.JsonDictType())
    parameters = sa.Column(st.JsonDictType())
    output = sa.Column(st.JsonDictType())

    # Runtime context like iteration_no of a repeater.
    # Effectively internal engine properties which will be used to determine
    # execution of a task.
    runtime_context = sa.Column(st.JsonDictType())

    # Relations.
    execution_id = sa.Column(sa.String(36), sa.ForeignKey('executions_v2.id'))
    execution = relationship('Execution', backref="tasks", lazy='joined')

    def to_dict(self):
        d = super(Task, self).to_dict()

        d['result'] = json.dumps(
            d['output'].get('task', {}).get(d['name'], {})
            if d['output'] else {}
        )

        return d


class DelayedCall(mb.MistralModelBase):
    """Contains info about delayed calls."""

    __tablename__ = 'delayed_calls_v2'

    id = mb._id_column()
    factory_method_path = sa.Column(sa.String(200), nullable=True)
    target_method_name = sa.Column(sa.String(80), nullable=False)
    method_arguments = sa.Column(st.JsonDictType())
    auth_context = sa.Column(st.JsonDictType())
    execution_time = sa.Column(sa.DateTime, nullable=False)