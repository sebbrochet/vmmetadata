#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit
from pyVim import connect
from pyVmomi import vim, vmodl
import time

import requests
requests.packages.urllib3.disable_warnings()

def myprint(unicodeobj):
    import sys
    print unicodeobj.encode(sys.stdout.encoding or 'utf-8')

def get_full_name(vm):
    current = vm
    full_name = vm.name

    while hasattr(current, 'parentVApp') and current.parentVApp:
        full_name = "%s/%s" % (current.parentVApp.name, full_name)
        current = current.parentVApp

    while hasattr(current, 'parent') and current.parent:
        full_name = "%s/%s" % (current.parent.name, full_name)
        current = current.parent

    return full_name


def get_service_instance(args):
    service_instance = None

    try:
        service_instance = connect.SmartConnect(host=args.target,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port))
        atexit.register(connect.Disconnect, service_instance)
    except IOError as e:
        pass
    except vim.fault.InvalidLogin, e:
        raise SystemExit("Error: %s" % e.msg)
    except TypeError, e:
        raise SystemExit("Error: %s" % e.message) 

    if not service_instance:
        raise SystemExit("Error: unable to connect to target with supplied info.")

    return service_instance


def get_vm_from_scope_IFN(scope):
    if not scope:
        return None

    vms_from_scope = []

    f = file(scope, "r")
    lines = f.read().split('\n')
    for line in lines:
        if line.startswith('#'):
            continue
        value = line.strip()

	if value:
            vms_from_scope.append(value)

    return vms_from_scope


def get_custom_attribute_field_def_by_name_dict(service_instance):
    custom_attribute_field_def_by_name_dict = {}

    content = service_instance.RetrieveContent()
    for field_def in content.customFieldsManager.field:
        custom_attribute_field_def_by_name_dict[field_def.name] = field_def

    return custom_attribute_field_def_by_name_dict 


def is_in_datacenter(vm, datacenter_name):
    return datacenter_name == '' or get_full_name(vm).split('/')[1] == datacenter_name


def is_in_scope(vm, vms_from_scope):
    return vms_from_scope is None or vm.name in vms_from_scope


def get_all_vm_metadata(service_instance, args):
    def get_custom_attribute_name_by_id_dict(service_instance):
        custom_attribute_name_by_id_dict = {}

        content = service_instance.RetrieveContent()
        for field_def in content.customFieldsManager.field:
            custom_attribute_name_by_id_dict[field_def.key] = field_def.name

        return custom_attribute_name_by_id_dict

    def get_or_create_bucket(vm_dict, key):
        bucket = vm_dict.get(key, {})
        vm_dict[key] = bucket

        return bucket

    def get_vm_metadata_dict(custom_attribute_name_by_id_dict, datacenter_name, vms_from_scope):

        vm_metadata_dict = {}
        content = service_instance.RetrieveContent()
        object_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)

        for vm in object_view.view:
            if is_in_datacenter(vm, datacenter_name) and is_in_scope(vm, vms_from_scope):
                for value in vm.value:
                    try:
                        bucket = get_or_create_bucket(vm_metadata_dict, vm.name)
                        field_name = custom_attribute_name_by_id_dict[value.key] 
                        bucket[field_name] = value.value
                    except ValueError, E:
                        print "Error: bad value (%s) of %s metadata for %s VM" % (value.value, value.key, vm.name)

        object_view.Destroy()

        return vm_metadata_dict 

    vms_from_scope = get_vm_from_scope_IFN(args.scope)
    custom_attribute_name_by_id_dict = get_custom_attribute_name_by_id_dict(service_instance)
    vm_metadata_dict = get_vm_metadata_dict(custom_attribute_name_by_id_dict, args.datacenter, vms_from_scope)
    
    return vm_metadata_dict 

def dump_metadata_into_list(args, output_list):
    service_instance = get_service_instance(args)
    all_vm_metadata = get_all_vm_metadata(service_instance, args)

    import yaml
    yaml_ouput = yaml.dump(all_vm_metadata, default_flow_style=False)
    output_list.extend(yaml_ouput.splitlines())

    return output_list


def cmd_export(args):
    if not args.metadatafile:
       print "Error: 'metadatafile' is mandatory with 'export' command."
       return False

    output_list = []
    dump_metadata_into_list(args, output_list)

    with open(args.metadatafile, "w") as f:
        f.writelines('\n'.join(output_list)) 

def cmd_list(args):
    output_list = []
    dump_metadata_into_list(args, output_list) 
    myprint('\n'.join(output_list))


def load_metadatafile_IFP(metadatafile):
    is_ok = True
    obj = None
    error = ''

    with open(metadatafile, "r") as f:
        try:
            import yaml
            obj = yaml.load(f)

            if not type(obj) is dict:
                error = "Metadatafile content should be a dictionnary."
                is_ok = False
        except Exception, e:
            error = "Error while interpreting test suite configuration: %s\nException: %s" % (filename, e)
            is_ok = False

    return is_ok, obj, error

def cmd_import(args):
    def get_custom_attribute_field_def_by_name_dict(service_instance):
        custom_attribute_field_def_by_name_dict = {}

        content = service_instance.RetrieveContent()
        for field_def in content.customFieldsManager.field:
            custom_attribute_field_def_by_name_dict[field_def.name] = field_def

        return custom_attribute_field_def_by_name_dict

    def get_all_vm_dict(service_instance, vms_from_scope, datacenter_name):
        content = service_instance.RetrieveContent()
        object_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)

        all_vm_dict = {}

        for vm in object_view.view:
            if is_in_datacenter(vm, datacenter_name) and is_in_scope(vm, vms_from_scope):
                all_vm_dict[vm.name] = vm

        return all_vm_dict

    def get_or_create_field_def(service_instance, custom_attribute_dict, field_name):
        field_def = custom_attribute_dict.get(field_name)
       
        if not field_def:
            content = service_instance.RetrieveContent()
            try:
                field_def = content.customFieldsManager.AddCustomFieldDef(field_name)
            except Exception, e:
               print "vmmetadata internal error (i.e a bug): %s" % e 

        return field_def
    
    def update_field_IFN(service_instance, vm, field_def, new_value):
        current_value = None

        for value in vm.value:
            if value.key == field_def.key:
                current_value = value.value
                break 
        if new_value != current_value:
            print "Updating %s.%s with %s" % (vm.name, field_def.name, new_value)
            content = service_instance.RetrieveContent()
            content.customFieldsManager.SetField(vm, field_def.key, new_value)  

    if not args.metadatafile:
       print "Error: 'metadatafile' is mandatory with 'import' command."
       return False

    is_ok, obj, error = load_metadatafile_IFP(args.metadatafile)

    if is_ok:
        vms_from_scope = get_vm_from_scope_IFN(args.scope)
        service_instance = get_service_instance(args)
        all_vm_dict = get_all_vm_dict(service_instance, vms_from_scope, args.datacenter)
        custom_attribute_field_def_by_name_dict = get_custom_attribute_field_def_by_name_dict(service_instance)

        for vm_name, metadata_dict in obj.iteritems():
            print "Trying to update %s..." % vm_name
            vm = all_vm_dict.get(vm_name)
            if vm:
                for field_name, field_value in metadata_dict.iteritems():
                    field_def = get_or_create_field_def(service_instance, custom_attribute_field_def_by_name_dict, field_name)
                    update_field_IFN(service_instance, vm, field_def, field_value)
            else:
                print "%s vm not present (yet?) in inventory on vCenter host" % vm_name
    else:
       print error 
