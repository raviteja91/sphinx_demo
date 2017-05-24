#imports and constants

from pyVim.connect import SmartConnect,Disconnect
from pyVmomi import vim
from custom_exceptions_vcenter import VcenterException,Vcenterconnectionerror,VMUnavaiable,HostUnavaiable,DatacenterUnavaiable,PoolUnavailable,VMDiskUnavaiable
import requests
import time
import logging

requests.packages.urllib3.disable_warnings()

import ssl
logging.basicConfig(filename = 'testlog.log', level = logging.ERROR, format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%d %b %Y %H:%M:%S')
import sys
sys.tracebacklimit=0


class VCenterconnection(object):
    def __init__(self):
        self.connect=None
    def connect_to_vcenter(self,hostname=None,username=None,password=None,certFile=None):
        """
        It connects to host.

        Variables :
                    hostname: IP or name of the Vcenter.
                    username: username to access to Vcenter.
                    password: password for specified username.
                    certFile: Optional
        """
        if not certFile:
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                # Legacy Python that doesn't verify HTTPS certificates by default
                pass
            else:
                # Handle target environment that doesn't support HTTPS verification
                ssl._create_default_https_context = _create_unverified_https_context

        try:
            self.connect=SmartConnect(host=hostname,user=username,pwd=password,certFile=certFile)
        except vim.fault.InvalidLogin as error:
            msg= "Failed to connect to Vcenter %s using credentials username: %s and password: %s" %(hostname,username,password)
            logging.error("Failed to connect to Vcenter %s using credentials username: %s and password: %s" %(hostname,username,password))
            raise VcenterException(msg)
        except Exception as error:
            msg = "Unable to connect to Vcenter %s because of %s"%(hostname,error)
            logging.error(msg)
            raise VcenterException(msg)

    def get_obj(self,content, vimtype, name):
        """
        Get the vsphere object associated with a given text name.

        variables:
                content: It is a Vcenter object.
                vimtype: It is, type of the object,want to return. example:vm or esxi host
                name: name of machine

        """
        machine_obj = None
        if content.viewManager:
             container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
             for c in container.view:
                 if c.name == name:
                    machine_obj = c
                    break
        return machine_obj

    def get_object(self, vim_type):
        """
        Get the vsphere object associated with a given vim_type.

        variables:
                vimtype: It is, type of the object,want to return. example:vm or esxi host.
        """
        content = self.connect.RetrieveContent()
        object_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                              vim_type, True)
        return object_view

    def get_dc_object(self, vim_type, name):
        """
        Get the vsphere object associated with a given vim_type.

        variables:
                vimtype: It is, type of the object,want to return. example:vm or esxi host.
        """
        obj = None
        content = self.connect.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, vim_type, True)
        for c in container.view:
                if c.name == name:
                    obj = c
                    break
        return obj

    def get_child_obj(self):
        """
        Get the vsphere child object associated connected vm.

        """
        content = self.connect.RetrieveContent()
        object_view = content.rootFolder.childEntity

        return object_view

    def get_clusters_list(self):
        """
        Get the clusters list using vsphere child object.

        """
        clusters_data = {}

        children = self.get_child_obj()
        if len(children) > 0:
            for child in children:
                dc = child
                clusters_data[dc.name] = {}
                clusters = dc.hostFolder.childEntity
                if len(clusters) > 0:
                    for cluster in clusters:
                        clusters_data[dc.name][cluster.name] = {}

        return clusters_data

    def wait_for_task(task, actionName='job', hideResult=False):
        """
        Waits and provides updates on a vSphere task
        """
        # import ipdb; ipdb.set_trace()
        while task.info.state == vim.TaskInfo.State.running:
            time.sleep(2)
        
        if task.info.state == vim.TaskInfo.State.success:
            if task.info.result is not None and not hideResult:
                out = '%s completed successfully, result: %s' % (actionName, task.info.result)
                print out
            else:
                out = '%s completed successfully.' % actionName
                print out
        else:
            out = '%s did not complete successfully: %s' % (actionName, task.info.error)
            raise task.info.error
            print out
        
        return task.info.result

    def get_vm_by_name(self,name):
        """
        Find a virtual machine by it's name and return it.

        variables:
                name : Name of the virtual for which you want retrieve object.
        """
    
        vm_obj = self.get_obj(self.connect.RetrieveContent(), [vim.VirtualMachine], name)
        if vm_obj:
            return vm_obj
        else:
            raise VMUnavaiable(name)

    def get_host_by_name(self,name):
        """
        Find a virtual machine by it's name and return it.
        Variables:
                name: name of the esxi host.
        """
    
        hostobj = self.get_obj(self.connect.RetrieveContent(), [vim.HostSystem], name)
        if hostobj:
            return hostobj
        else:
            raise HostUnavaiable(name)

    def get_vm_virtual_disk(self,vm_name=None):
        """
        It returns the virtual disks related to the virtual machine.

        Variables:
                vm_name: Name of the vm.
        """
        vdisks = []
        vm = self.get_vm_by_name(vm_name)
            
        devices = vm.config.hardware.device
        for device in devices:
            if str(device.__class__).__contains__("vim.vm.device.VirtualDisk"):
                vdisks.append(device)
        return vdisks

    def get_vmdk(self, vm_name):
        """
        getVMDK:this will returns the virtual machine disk file based on the given vm name
        """
        vm = self.get_vm_by_name(vm_name)
        vmdk_path = None
        for device in vm.config.hardware.device:
            if type(device).__name__ == 'vim.vm.device.VirtualDisk':
                vmdk_path = device.backing.fileName
        return vmdk_path
 
    def get_disk_space_of_vm(self,vm_name):
        '''Disk space of the vm:
        it will returns the diskspace of the vm in kb'''
        vm = self.get_vm_by_name(vm_name)
        disk_space = None
        for device in vm.config.hardware.device:
            if type(device).__name__ == 'vim.vm.device.VirtualDisk':
                disk_space = device.capacityInKB
        return disk_space

    def get_datacenter_by_name(self,name):
        '''getdatacenter by name: this will returns the Datacenter object based on the given datacenter name'''
        datacenter = self.get_obj(self.connect.RetrieveContent(), [vim.Datacenter],name)
        if datacenter:
            return datacenter
        else:
            raise DatacenterUnavaiable(name)

    def increase_disk(self,vmdk,datacenter,sizeinkb,eagerzero):
        try:
            virtualDiskManager = self.connect.content.virtualDiskManager
            task = virtualDiskManager.ExtendVirtualDisk(vmdk ,datacenter,sizeinkb,eagerzero)
            while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                time.sleep(1)
            return task.info.state
        except Exception as err:
            logging.info(err.message)
            logging.info("Unable to increase the increase the disk space, somethin went wrong")

    def get_pool_by_name(self, name):
        '''getvm by name: this will returns the vm object based on the given vm name'''
        pool = self.get_obj(self.connect.RetrieveContent(), [vim.ResourcePool], name)
        if pool:
            return pool
        else:
            raise PoolUnavailable(name)

    def disconnect(self):
        """
        It disconnect connection object if there is any.
        """

        if self.connect:
            Disconnect(self.connect)

