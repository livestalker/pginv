# Copyright (c) 2020 Alexey Grebenshchikov

from __future__ import absolute_import, division, print_function

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.utils.display import Display

__metaclass__ = type


display = Display()

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
        # TODO
