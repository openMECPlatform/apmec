# Copyright 2016 - Nokia
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

import codecs
import os

import testtools
import yaml

from apmec.catalogs.tosca import utils as toscautils
from toscaparser import tosca_template
from translator.hot import tosca_translator


def _get_template(name):
    filename = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../infra_drivers/openstack/data/", name)
    f = codecs.open(filename, encoding='utf-8', errors='strict')
    return f.read()


class TestToscaUtils(testtools.TestCase):
    tosca_openwrt = _get_template('test_tosca_openwrt.yaml')
    mead_dict = yaml.safe_load(tosca_openwrt)
    toscautils.updateimports(mead_dict)
    tosca = tosca_template.ToscaTemplate(parsed_params={}, a_file=False,
                          yaml_dict_tpl=mead_dict)
    tosca_flavor = _get_template('test_tosca_flavor.yaml')

    def setUp(self):
        super(TestToscaUtils, self).setUp()

    def test_updateimport(self):
        importspath = os.path.abspath('./apmec/tosca/lib/')
        file1 = importspath + '/apmec_defs.yaml'
        file2 = importspath + '/apmec_mec_defs.yaml'
        expected_imports = [file1, file2]
        self.assertEqual(expected_imports, self.mead_dict['imports'])

    def test_get_mgmt_driver(self):
        expected_mgmt_driver = 'openwrt'
        mgmt_driver = toscautils.get_mgmt_driver(self.tosca)
        self.assertEqual(expected_mgmt_driver, mgmt_driver)

    def test_get_vdu_monitoring(self):
        expected_monitoring = {'vdus': {'VDU1': {'ping': {
                               'actions':
                               {'failure': 'respawn'},
                               'name': 'ping',
                               'parameters': {'count': 3,
                                              'interval': 10},
                               'monitoring_params': {'count': 3,
                                                  'interval': 10}}}}}
        monitoring = toscautils.get_vdu_monitoring(self.tosca)
        self.assertEqual(expected_monitoring, monitoring)

    def test_get_mgmt_ports(self):
        expected_mgmt_ports = {'mgmt_ip-VDU1': 'CP1'}
        mgmt_ports = toscautils.get_mgmt_ports(self.tosca)
        self.assertEqual(expected_mgmt_ports, mgmt_ports)

    def test_post_process_template(self):
        tosca2 = tosca_template.ToscaTemplate(parsed_params={}, a_file=False,
                          yaml_dict_tpl=self.mead_dict)
        toscautils.post_process_template(tosca2)
        invalidNodes = 0
        for nt in tosca2.nodetemplates:
            if (nt.type_definition.is_derived_from(toscautils.MONITORING) or
                nt.type_definition.is_derived_from(toscautils.FAILURE) or
                    nt.type_definition.is_derived_from(toscautils.PLACEMENT)):
                invalidNodes += 1

        self.assertEqual(0, invalidNodes)

        deletedProperties = 0
        if nt.type in toscautils.delpropmap.keys():
            for prop in toscautils.delpropmap[nt.type]:
                for p in nt.get_properties_objects():
                    if prop == p.name:
                        deletedProperties += 1

        self.assertEqual(0, deletedProperties)

        convertedProperties = 0
        if nt.type in toscautils.convert_prop:
            for prop in toscautils.convert_prop[nt.type].keys():
                for p in nt.get_properties_objects():
                    if prop == p.name:
                        convertedProperties += 1

        self.assertEqual(0, convertedProperties)

    def test_post_process_heat_template(self):
        tosca1 = tosca_template.ToscaTemplate(parsed_params={}, a_file=False,
                          yaml_dict_tpl=self.mead_dict)
        toscautils.post_process_template(tosca1)
        translator = tosca_translator.TOSCATranslator(tosca1, {})
        heat_template_yaml = translator.translate()
        expected_heat_tpl = _get_template('hot_tosca_openwrt.yaml')
        mgmt_ports = toscautils.get_mgmt_ports(self.tosca)
        heat_tpl = toscautils.post_process_heat_template(
            heat_template_yaml, mgmt_ports, {}, {}, {})

        heatdict = yaml.safe_load(heat_tpl)
        expecteddict = yaml.safe_load(expected_heat_tpl)
        self.assertEqual(expecteddict, heatdict)

    def test_findvdus(self):
        vdus = toscautils.findvdus(self.tosca)

        self.assertEqual(1, len(vdus))

        for vdu in vdus:
            self.assertEqual(True, vdu.type_definition.is_derived_from(
                toscautils.APMECVDU))

    def test_get_flavor_dict(self):
        mead_dict = yaml.safe_load(self.tosca_flavor)
        toscautils.updateimports(mead_dict)
        tosca = tosca_template.ToscaTemplate(a_file=False,
                                             yaml_dict_tpl=mead_dict)
        expected_flavor_dict = {
            "VDU1": {
                "vcpus": 2,
                "disk": 10,
                "ram": 512
            }
        }
        actual_flavor_dict = toscautils.get_flavor_dict(tosca)
        self.assertEqual(expected_flavor_dict, actual_flavor_dict)

    def test_add_resources_tpl_for_flavor(self):
        dummy_heat_dict = yaml.safe_load(_get_template(
            'hot_flavor_and_capabilities.yaml'))
        expected_dict = yaml.safe_load(_get_template('hot_flavor.yaml'))
        dummy_heat_res = {
            "flavor": {
                "VDU1": {
                    "vcpus": 2,
                    "ram": 512,
                    "disk": 10
                }
            }
        }
        toscautils.add_resources_tpl(dummy_heat_dict, dummy_heat_res)
        self.assertEqual(expected_dict, dummy_heat_dict)

    def test_get_flavor_dict_extra_specs_all_numa_count(self):
        tosca_fes_all_numa_count = _get_template(
            'tosca_flavor_all_numa_count.yaml')
        mead_dict = yaml.safe_load(tosca_fes_all_numa_count)
        toscautils.updateimports(mead_dict)
        tosca = tosca_template.ToscaTemplate(a_file=False,
                                             yaml_dict_tpl=mead_dict)
        expected_flavor_dict = {
            "VDU1": {
                "vcpus": 8,
                "disk": 10,
                "ram": 4096,
                "extra_specs": {
                    'hw:cpu_policy': 'dedicated', 'hw:mem_page_size': 'any',
                    'hw:cpu_sockets': 2, 'hw:cpu_threads': 2,
                    'hw:numa_nodes': 2, 'hw:cpu_cores': 2,
                    'hw:cpu_threads_policy': 'avoid'
                }
            }
        }
        actual_flavor_dict = toscautils.get_flavor_dict(tosca)
        self.assertEqual(expected_flavor_dict, actual_flavor_dict)

    def test_apmec_conf_heat_extra_specs_all_numa_count(self):
        tosca_fes_all_numa_count = _get_template(
            'tosca_flavor_all_numa_count.yaml')
        mead_dict = yaml.safe_load(tosca_fes_all_numa_count)
        toscautils.updateimports(mead_dict)
        tosca = tosca_template.ToscaTemplate(a_file=False,
                                             yaml_dict_tpl=mead_dict)
        expected_flavor_dict = {
            "VDU1": {
                "vcpus": 8,
                "disk": 10,
                "ram": 4096,
                "extra_specs": {
                    'hw:cpu_policy': 'dedicated', 'hw:mem_page_size': 'any',
                    'hw:cpu_sockets': 2, 'hw:cpu_threads': 2,
                    'hw:numa_nodes': 2, 'hw:cpu_cores': 2,
                    'hw:cpu_threads_policy': 'avoid',
                    'aggregate_instance_extra_specs:mec': 'true'
                }
            }
        }
        actual_flavor_dict = toscautils.get_flavor_dict(
            tosca, {"aggregate_instance_extra_specs:mec": "true"})
        self.assertEqual(expected_flavor_dict, actual_flavor_dict)

    def test_add_resources_tpl_for_image(self):
        dummy_heat_dict = yaml.safe_load(_get_template(
            'hot_image_before_processed_image.yaml'))
        expected_dict = yaml.safe_load(_get_template(
            'hot_image_after_processed_image.yaml'))
        dummy_heat_res = {
            "image": {
                "VDU1": {
                    "location": "http://URL/v1/openwrt.qcow2",
                    "container_format": "bare",
                    "disk_format": "raw"
                }
            }
        }
        toscautils.add_resources_tpl(dummy_heat_dict, dummy_heat_res)
        self.assertEqual(expected_dict, dummy_heat_dict)

    def test_convert_unsupported_res_prop_kilo_ver(self):
        unsupported_res_prop_dict = {'OS::Neutron::Port': {
            'port_security_enabled': 'value_specs', }, }
        dummy_heat_dict = yaml.safe_load(_get_template(
            'hot_tosca_openwrt.yaml'))
        expected_heat_dict = yaml.safe_load(_get_template(
            'hot_tosca_openwrt_kilo.yaml'))
        toscautils.convert_unsupported_res_prop(dummy_heat_dict,
                                                unsupported_res_prop_dict)
        self.assertEqual(expected_heat_dict, dummy_heat_dict)

    def test_check_for_substitution_mappings(self):
        tosca_sb_map = _get_template('../../../../../etc/samples/test-mesd-'
                                     'mead1.yaml')
        param = {'substitution_mappings': {
                 'VL2': {'type': 'tosca.nodes.mec.VL', 'properties': {
                         'network_name': 'net0', 'vendor': 'apmec'}},
                 'VL1': {'type': 'tosca.nodes.mec.VL', 'properties': {
                         'network_name': 'net_mgmt', 'vendor': 'apmec'}},
                 'requirements': {'virtualLink2': 'VL2',
                                  'virtualLink1': 'VL1'}}}
        template = yaml.safe_load(tosca_sb_map)
        toscautils.updateimports(template)
        toscautils.check_for_substitution_mappings(template, param)
        self.assertNotIn('substitution_mappings', param)

    def test_get_block_storage_details(self):
        tosca_vol = _get_template('tosca_block_storage.yaml')
        mead_dict = yaml.safe_load(tosca_vol)
        expected_dict = {
            'volumes': {
                'VB1': {
                    'image': 'cirros-0.3.5-x86_64-disk',
                    'size': '1'
                }
            },
            'volume_attachments': {
                'CB1': {
                    'instance_uuid': {'get_resource': 'VDU1'},
                    'mountpoint': '/dev/vdb',
                    'volume_id': {'get_resource': 'VB1'}}
            }
        }
        volume_details = toscautils.get_block_storage_details(mead_dict)
        self.assertEqual(expected_dict, volume_details)
