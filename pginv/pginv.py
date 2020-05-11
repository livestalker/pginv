# Copyright (c) 2020 Alexey Grebenshchikov

from __future__ import absolute_import, division, print_function

from typing import Dict, List, Any, Tuple

import psycopg2  # type: ignore
from ansible.parsing.yaml.objects import AnsibleMapping  # type: ignore
from ansible.plugins.inventory import BaseInventoryPlugin  # type: ignore
from ansible.utils.display import Display  # type: ignore

__metaclass__ = type


display = Display()

Id = int
Name = str
Vars = dict

DOCUMENTATION = r"""
    name: pginv
    plugin_type: inventory
    short_description: PostgreSQL inventory source
    options:
        plugin:
            description: Token that ensures this is a source file for the plugin.
            required: True
            choices: ['pginv']
        connection:
            description: DB connection options
            suboptions:
                host:
                    description: DB host
                    default: localhost
                port:
                    description: DB port
                    default: 5432
                user:
                    description: DB user
                    default: postgres
                password:
                    description: DB user password
                    default: postgres
                dbname:
                    description: DB name
                    default: ansible_inventory
                
"""

EXAMPLES = r"""
"""


class InventoryModule(BaseInventoryPlugin):
    NAME = "pginv"

    def __init__(self):
        super(InventoryModule, self).__init__()
        self._connection = {}

    def verify_file(self, path):
        if super(InventoryModule, self).verify_file(path) and path.endswith(
            ("pginv.yml", "pginv.yaml")
        ):
            return True

        display.debug(
            "pginv inventory filename must end with 'pginv.yml' or 'pginv.yaml'"
        )
        return False

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)

        self._fill_connection(self.get_option("connection"))
        self._fill_inventory()

    def _fill_connection(self, params: AnsibleMapping):
        self._connection = {
            "host": params.get("host", "localhost"),
            "port": params.get("port", "5432"),
            "user": params.get("user", "postgres"),
            "password": params.get("password", "postgres"),
            "dbname": params.get("dbname", "ansible_inventory"),
        }

    def _fill_inventory(self):
        connection = psycopg2.connect(**self._connection)
        cursor = connection.cursor()
        groups, hosts = self._get_host_data(cursor)
        self._add_groups(groups)
        self._add_hosts(groups, hosts)

    def _get_host_data(
        self, cursor
    ) -> Tuple[Dict[Id, Tuple[Name, Vars]], List[Dict[str, Any]]]:
        fields = (
            "host_id",
            "host_name",
            "host_vars",
            "group_id",
            "group_parent_id",
            "group_name",
            "group_vars",
        )
        sql = """
        select
               h.id host_id,
               h.name host_name,
               h.vars host_vars,
               g.id group_id,
               g.parent_id group_parent_id,
               g.name group_name,
               g.vars group_vars
        from
            hosts h
        left outer join group_hosts gh on h.id = gh.host_id
        left outer join groups g on gh.group_id = g.id;
        """
        cursor.execute(sql)
        groups = {}
        hosts_info = []
        for row in cursor.fetchall():
            host = dict(zip(fields, row))
            group_id = host["group_id"]
            if group_id not in groups and group_id is not None:
                groups[group_id] = (host["group_name"], host["group_vars"])
            hosts_info.append(host)

        return groups, hosts_info

    def _add_groups(self, groups: Dict[Id, Tuple[Name, Vars]]):
        for group_name, group_vars in groups.values():
            self.inventory.add_group(group=group_name)
            self._set_variables(group_name, group_vars)

    def _add_hosts(
        self, groups: Dict[Id, Tuple[Name, Vars]], hosts: List[Dict[str, Any]]
    ):
        for host in hosts:
            group_id = host["group_id"]
            group_name = groups[group_id][0] if group_id is not None else None
            host_name = host["host_name"]
            self.inventory.add_host(host=host_name, group=group_name)
            self._set_variables(host_name, host["host_vars"])

    def _set_variables(self, entity: str, vars: Dict):
        for varname, value in vars.items():
            self.inventory.set_variable(entity=entity, varname=varname, value=value)
