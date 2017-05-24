
from vmware import VCenterconnection

from custom_exceptions_vcenter import *
#from pyVmomi import vim
from pyVim.task import WaitForTask
import logging
from pyVmomi import vim,vmodl
import time


logging.basicConfig(filename = 'testlog.log',
 level = logging.ERROR,
 format='%(asctime)s %(levelname)-8s %(message)s',
 datefmt='%d %b %Y %H:%M:%S')


class VcenterOperations:
    def __init__(self):
        self.vcenter = None

    def connect(self,hostname,username,password,certfile=None):
        """
        It Makes connetion to the Vcenter.
        Variables:
            hostname: IP/Name of the host.
            username: username to access Vcenter.
            password: Password for given username.
            certfile: Cerificate file location if there is any. 
        Return: None
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.certfile = certfile
        self.vcenter=VCenterconnection()
        self.vcenter.connect_to_vcenter(self.hostname, self.username, self.password, self.certfile)
        
    def list_of_datacenters(self):
        """
        list_of_datacenters(self): It returns list of Datacenters in vCenter.

        Variables:
            None.

        Return:
            datacenters_name_list(list): List of the Datacenters.
        """
        datacenters_name_list = []
        try:
            if self.vcenter:
                object_view = self.vcenter.get_object([vim.Datacenter])
                datacenters_list = object_view.view
                if len(datacenters_list) > 0:
                    for i in datacenters_list:
                        datacenters_name_list.append(i.name)

                        return datacenters_name_list

                else:
                    raise DatacentersUnavaiable()
            else:
                raise Vcenterconnectionerror()

        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
        except DatacentersUnavaiable as error:
            print(error)
            raise

    def create_cluster(self, dcname, cluster_name):
        """
        create_cluster(self, dcname, cluster_name): creates a new cluster.

        Variables:
            dcname(str): name of datacenter.
            cluster_name(str): name of cluster.

        Return:
            new cluster name.
        """
        try:
            if self.vcenter:
                datacenter = self.vcenter.get_dc_object([vim.Datacenter], dcname)
                cluster = self.vcenter.get_dc_object([vim.ClusterComputeResource], cluster_name)
                if cluster is not None:
                    logging.info("cluster already exists...!")
                    return cluster
                else:
                    if cluster_name is None:
                        raise ValueError("Missing value for cluster.")
                    if datacenter is None:
                        raise ValueError("Missing value for datacenter.")

                    logging.info("Creating Cluster with name - %s " % cluster_name )
                    cluster_spec = vim.cluster.ConfigSpecEx()
                    host_folder = datacenter.hostFolder
                    cluster = host_folder.CreateClusterEx(name=cluster_name, spec=cluster_spec)

                    return cluster.name
            else:
                raise Vcenterconnectionerror()

        except Vcenterconnectionerror as error:
            print(error.message)
            raise

    def list_of_clusters(self):
        """
        list_of_clusters(self): It returns list of clusters in vm.

        Variables:
            None

        Return:
            clusters_list(list): List of the clusters.
        """
        clusters_list = []
        try:
            if self.vcenter:
                clusters_data = self.vcenter.get_clusters_list()
                for key in clusters_data.keys():
                    data_list = clusters_data[key].keys()
                    clusters_list.append(data_list)

                return clusters_list
            else:
                raise Vcenterconnectionerror()
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise

    def cluster_exists_or_not(self, cluster_name):
        """
        cluster_exists_or_not(self, cluster_name): It returns list of clusters in vm.

        Variables:
            cluster_name(str): Name of the Cluster.

        Return:
            clusters_exists_or_not(bool): Returns True or False.
        """
        clusters_list = []
        try:
            if self.vcenter:
                clusters_data = self.vcenter.get_clusters_list()
                for key in clusters_data.keys():
                    for data_list in clusters_data[key].keys():
                        clusters_list.append(data_list)

                return cluster_name in clusters_list
            else:
                raise Vcenterconnectionerror()
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
        except DatacentersUnavaiable as error:
            print(error)
            raise
        except ClustersUnavaiable as error:
            print(error)
            raise

    def list_of_hosts_under_cluster(self, cluster_name):
        """
        list_of_hosts_under_cluster(self, cluster_name): It returns list of hosts under cluster.

        Variables:
            cluster_name(str): Name of the Cluster.

        Return:
            host_list(list): Returns list of hosts under cluster.
        """
        hosts_list = []
        try:
            if self.vcenter:
                children = self.vcenter.get_child_obj()
                for child in children:
                    dc = child
                    clusters = dc.hostFolder.childEntity
                    for cluster in clusters:
                        if cluster.name == cluster_name:
                            hosts = cluster.host
                            for host in hosts:
                                hostname = host.summary.config.name
                                hosts_list.append(hostname)

                                return hosts_list
                    else:
                        raise ClustersUnavaiable("No Clusters available with %s name" % cluster_name)
            else:
                raise Vcenterconnectionerror()
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
        except DatacentersUnavaiable as error:
            print(error)
            raise
        except ClustersUnavaiable as error:
            print(error)
            raise

    def vm_snapshot(self, vm_name, snap_name, desc, dumpmemory=False, quiesce=False):
        """
        vm_snapshot(self, vm_name snap_name, desc, dumpmemory, quiesce): It creates a vm snapshot.

        Variables:
            vm_name(str): Name of the VM.
            snap_name(str): Name of the snapshot.
            desc(str): description of snapshot.
            dumpmemory(bool): True/False
            quiesce(bool): True/False

        Return:
            status.
        """
        try:
            if self.vcenter:
                vm = self.vcenter.get_dc_object([vim.VirtualMachine], vm_name)
                logging.info("Creating snapshot %s for vm: %s" % (
                                                snap_name, vm.name))
                WaitForTask(vm.CreateSnapshot(
                            snap_name, desc, dumpmemory, quiesce))
                # obj = vm.snapshot.currentSnapshot

                logging.info("snapshot with name %s created successfully." % snap_name)
            else:
                raise Vcenterconnectionerror()
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise

    def create_template(self, dcname, vm_name, target_host, template_name):
        """
        create_template(self, dcname, vm_name, 
            target_host, template_name): It creates a template from vm.

        Variables:
            dcname(str): datacenter_name
            vm_name(str): Name of the VM.
            target_host(str): target host ip of the vm.
            template_name(str): new template name.

        Return:
            status information.
        """
        try:
            if self.vcenter:
                datacenter = self.vcenter.get_dc_object([vim.Datacenter], dcname)
                vmFolder = datacenter.vmFolder
                vm = self.vcenter.get_dc_object([vim.VirtualMachine], vm_name)
                # if vm.runtime.powerState != 'poweredOff':
                #     print "WARNING:: Power off your VM before creating template"
                #     sys.exit()

                target_host = self.vcenter.get_dc_object([vim.HostSystem], target_host)
                relocate_spec = vim.vm.RelocateSpec()
                for datastore in target_host.datastore:
                    #Store the OVS vApp VM in local datastore of each host
                    if datastore.summary.type == 'VMFS':
                        logging.info("Storing the template in %s" % datastore.name)
                        relocate_spec.datastore = datastore
                        break

                relocate_spec.host = target_host
                relocate_spec.pool = vm.resourcePool

                cloneSpec = vim.vm.CloneSpec(powerOn=False, template=True, location=relocate_spec)
                logging.info("Creating template... ")
                task = vm.Clone(name=template_name, folder=vmFolder, spec=cloneSpec)
                # import ipdb; ipdb.set_trace()
                job_status = WaitForTask(task, 'creating template from vm')
                if job_status:
                    logging.info("Template %s created successfully" % template_name)
            else:
                raise Vcenterconnectionerror()
        except Vcenterconnectionerror as error:
            print error.message
            raise
        except VMUnavaiable as error:
            print error.message
            raise

    def vm_to_different_datastore(self, vm_name, dest_host, ds_name):
        """
        vm_to_different_datastore(self, vm_name, 
            dest_host, ds_name): move vm to different datastore.

        Variables:
            vm_name(str): Name of the VM.
            dest_host(str): Host ip.
            ds_name(str): Name of the Destination Datastore.

        Return:
            status information.
        """
        try:
            if self.vcenter:
                vm = self.vcenter.get_dc_object([vim.VirtualMachine], vm_name)
                destination_host = self.vcenter.get_dc_object([vim.HostSystem], dest_host)
                datastore = self.vcenter.get_dc_object([vim.Datastore], ds_name)
                # import ipdb; ipdb.set_trace()
                resource_pool = vm.resourcePool
                
                # Live Migration :: Change both host and datastore
                vm_relocate_spec = vim.vm.RelocateSpec()
                vm_relocate_spec.host = destination_host
                vm_relocate_spec.pool = resource_pool
                vm_relocate_spec.datastore = datastore

                if vm in destination_host.vm:
                    if datastore in destination_host.datastore:
                        task = vm.Relocate(spec=vm_relocate_spec)
                        job_status = WaitForTask(task, 'creating vm to different datastore')
                        if job_status:
                            logging.info(" %s moved successfully to %s " % (vm_name, ds_name))
                    else:
                        raise DatastoreUnavailable("%s is not under %s datastores." % (ds_name, destination_host))
                else:
                    raise VMUnavaiable("%s is not under %s vms." % (vm_name, destination_host))
            else:
                raise Vcenterconnectionerror()
        except Vcenterconnectionerror as error:
            print error.message
            raise
        except VMUnavaiable as error:
            print error.message
            raise
        except DatastoreUnavailable as error:
            print(error)
            raise

    def clone_vm(self, dcname, cluster_name, datastore_name, 
                            vm_name, new_vm_name, cpus=1, mem=3):
        """
        clone_vm(self, dcname, cluster_name, datastore_name,
                             vm_name, new_vm_name): It clone vm.

        Variables:
            dcname(str): datacenter_name
            cluster_name(str): cluster name.
            datastore_name(str): datastore name.
            temp_name(str): template name.
            new_vm_name(str): new VM name.
            cpus(int): no.of cpus(default=1)
            mem(int): memory size in GB(default=3)

        Return:
            status information.
        """
        try:
            if self.vcenter:
                mem = mem * 1024
                datacenter = self.vcenter.get_dc_object([vim.Datacenter], dcname)
                destfolder = datacenter.vmFolder
                cluster = self.vcenter.get_dc_object([vim.ClusterComputeResource], cluster_name)
                resource_pool = cluster.resourcePool # use same root resource pool that my desired cluster uses
                datastore = self.vcenter.get_dc_object([vim.Datastore], datastore_name)
                vm = self.vcenter.get_dc_object([vim.VirtualMachine], vm_name)

                # Relocation spec
                relospec = vim.vm.RelocateSpec()
                relospec.datastore = datastore
                relospec.pool = resource_pool

                # DNS settings
                globalip = vim.vm.customization.GlobalIPSettings()
                # globalip.dnsServerList = deploy_settings['dns_servers']
                # globalip.dnsSuffixList = ip_settings[0]['domain']
                
                # Hostname settings
                ident = vim.vm.customization.LinuxPrep()
                # ident.domain = ip_settings[0]['domain']
                ident.hostName = vim.vm.customization.FixedName()
                ident.hostName.name = new_vm_name
                
                customspec = vim.vm.customization.Specification()
                # customspec.nicSettingMap = adaptermaps
                customspec.globalIPSettings = globalip
                customspec.identity = ident

                # VM config spec
                vmconf = vim.vm.ConfigSpec()
                vmconf.numCPUs = cpus
                vmconf.memoryMB = mem
                vmconf.cpuHotAddEnabled = True
                vmconf.memoryHotAddEnabled = True
                # vmconf.deviceChange = devices

                # Clone spec
                clonespec = vim.vm.CloneSpec()
                clonespec.location = relospec
                clonespec.config = vmconf
                clonespec.customization = customspec
                clonespec.powerOn = True
                clonespec.template = False

                task = vm.Clone(folder=destfolder, name=new_vm_name, spec=clonespec)
                if task:
                    logging.info(" %s cloned successfully from %s " % (new_vm_name, vm_name))
            else:
                raise Vcenterconnectionerror()
        except Vcenterconnectionerror as error:
            print error.message
            raise
        except VMUnavaiable as error:
            print error.message
            raise

    def vm_storage(self,name_of_vm):
        """
        It gives information of storage attached to the VM.

        Variables:
            name_of_vm(str): name of Virtual machine.

        Return:
            size (int): Storage Attached to VM in GBs.
        """
        size = 0.0
        try:
            if self.vcenter:
                vdisks = self.vcenter.get_vm_virtual_disk(name_of_vm)
                if vdisks:
                    for vdisk in vdisks:
                        size = vdisk.capacityInKB
                        size = size/float(1024*1024)
                    return size
                else:
                    raise VMDiskUnavaiable("No disks available for this %s Virtual machine"%(name_of_vm))
            else:
                raise Vcenterconnectionerror()
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
        except VMDiskUnavaiable as error:
            print(error)
            raise

    def vm_memory(self,name_of_vm):
        """
        It gives the information of Memory attached to VM.

        Variables: 
            name_of_vm(str): Name of the Virtual machine.

        Return:
            memory(int): size of memory attached to the VM.
        """
        try:
            if self.vcenter:
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                memory = vm.config.hardware.memoryMB
                return memory
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise

    def vm_cpu(self,name_of_vm):
        """
        vm_cpuu(self,name_of_vm):It gives the information of CPUs attached to VM.
        
        Variables:
            name_of_vm(str): Name of the virtual machine.
        
        Return:
            num_of_cpu(int): Number of CPUs attached to VM.
        """
        try:
            if self.vcenter:
                
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                num_of_cpu = vm.config.hardware.numCPU
                return num_of_cpu
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
    def power_state(self,name_of_vm):
        """
        It gives power state of virtual machine(poweredOn/poweredOff).

        Variables:
                name_of_vm(str): Name of the virtual machine.

        Return: 
            vm_power_state(str): power state of the Virtual machine.
        """
        try:
            if self.vcenter:
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                vm_power_state = vm.runtime.powerState
                return vm_power_state
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
    def num_of_cores(self,name_of_vm):
        """
        It returns the number cores per socket.

        Variables:
                name_of_vm(str): Name of the virtual machine.

        Return:
            cores(int): Number cores per CPU


        """
        try:
            if self.vcenter:
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                cores = vm.config.hardware.numCoresPerSocket
                return cores
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise

    def power_off(self,name_of_vm):
        """
        power_off(self,name_of_vm): It power off  the Virtual machine.

        Variables:
            name_of_vm(str): Name of the virtual machine.

        Return: None.
        """
        try:
            if self.vcenter:
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                power_off = WaitForTask(vm.PowerOff())
                print(power_off)
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
        except vim.fault.InvalidPowerState as error:
            print (error.message)
            raise

    def power_on(self,name_of_vm):
        """
        power_on(self,name_of_vm): It power on  the Virtual machine.

        Variables:
            name_of_vm(str): Name of the virtual machine.

        Return: None
        """
        try:
            if self.vcenter:
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                power_on = WaitForTask(vm.PowerOn())
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
        except vim.fault.InvalidPowerState as error:
            print(error.msg)
            raise 
    def increase_memory(self,name_of_vm,size):
        """
        increase_memory(self,name_of_vm): It increase the size of the memory.

        Variables:
            name_of_vm(str): Name of the virtual machine.
            size(int): size in MBs.

        Return: None
        """
        try:
            if self.vcenter:
                memory  = int(self.vm_memory(name_of_vm))
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                self.power_off(name_of_vm)
                configure_memory = vim.vm.ConfigSpec()
                configure_memory.memoryMB = int(memory)+int(size)
                response = WaitForTask(vm.Reconfigure(configure_memory))
                self.power_on(name_of_vm)
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
        except vim.fault.GenericVmConfigFault as error:
            print(error.reason)
            raise
    def decrease_memory(self,name_of_vm,size):
        """
        decrease_memory(self,name_of_vm,size): It decreses the size of the memory.

        Variables:
            name_of_vm(str): Name of the virtual machine.
            size(int): size in MBs (It sould be below the actual size).

        Return: None
        """
        try:
            if self.vcenter:
                memory  = self.vm_memory(name_of_vm)
                if int(size) < int(memory):
                    vm = self.vcenter.get_vm_by_name(name_of_vm)
                    self.power_off(name_of_vm)
                    configure_memory = vim.vm.ConfigSpec()
                    configure_memory.memoryMB = int(memory)-int(size)
                    response = WaitForTask(vm.Reconfigure(configure_memory))
                    self.power_on(name_of_vm)
                else:
                    raise Exception("Failed to decrease memory size as given size % MB is more than or\
                        equal to the actual size %s MB"(int(size),memory))
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise
        except vim.fault.GenericVmConfigFault as error:
            print(error.reason)
            raise
        except Exception as error:
            print(error)
            raise

    def increase_cpu(self,name_of_vm,num_of_cpus):
        """
        increase_cpu(self,name_of_vm,num_of_cpus): It increses cpus as per the requiremnet.

        Variables:
            name_of_vm(str): Name of the virtual machine.
            num_of_cpus(int): Number of CPUs to increase.

        Return: None

        """
        try:
            if self.vcenter:
                cpus = int(self.vm_cpu(name_of_vm))#getting the nu.of CPUs attached to VM.
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                self.power_off(name_of_vm) # power off VM.
                configure_cpu = vim.vm.ConfigSpec()
                configure_cpu.numCPUs = int(cpus)+int(num_of_cpus)
                response = WaitForTask(vm.Reconfigure(configure_cpu))# increasing CPUs
                self.power_on(name_of_vm) # power 
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise 
    def decrease_cpu(self,name_of_vm,num_of_cpus):
        """
        decrease_cpu(self,name_of_vm,num_of_cpus): It decreases cpus as per the requiremnet.

        Variables:
            name_of_vm(str): Name of the virtual machine.
            num_of_cpus(int): Number of CPUs to increase.

        Return: None

        """
        try:
            if self.vcenter:
                cpus  = int(self.vm_cpu(name_of_vm))
                if int(num_of_cpus) < cpus:
                    vm = self.vcenter.get_vm_by_name(name_of_vm)
                    self.power_off(name_of_vm)
                    configure_cpu = vim.vm.ConfigSpec()
                    configure_cpu.numCPUs = int(cpus)-int(num_of_cpus)
                    response = WaitForTask(vm.Reconfigure(configure_cpu))
                    self.power_on(name_of_vm)
                else:
                    raise Exception("Failed to decrease CPUs as given CPUs %s is more than or\
                        equal to the actual size %s CPUs"(num_of_cpus,cpus))
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise 
        except Exception as error:
            print(error)
            raise


    def name_of_host(self,name_of_vm):
        """
        name_of_host(self,name_of_vm): It gives name of the host where the Virtual machine deployed.
        
        Variables:
            name_of_vm(str): Nmae of the virtual machine.

        return: 
            host_name(str): name of the host(ESXi).

        """
        try:
            if self.vcenter:
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                host_name = vm.runtime.host.name
                return host_name
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise

    def vm_nics(self,name_of_vm):
        """
        vm_nics(self,name_of_vm): It gives the number nics attached to the Virtual machine.

        Variables:
            name_of_vm(str): Name of the virual machine.
        return:
            num_of_nics(int): Number of NICs attched to Virtual machine.
        """
        try:
            if self.vcenter:
                num_of_nics = 0
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                devices = vm.config.hardware.device

                for device in devices:
                    if "Network adapter" in device.deviceInfo.label:
                        num_of_nics+=1
                return num_of_nics
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise

    def vm_state(self,name_of_vm):
        """
        vm_state(self,name_of_vm): It gives the state of the virtual machine.

        Variables:
            name_of_vm(str): Name of the virtual machine.

        Return: 
            state(str): State of the virtual machine.
        """
        try:
            if self.vcenter:
                vm = self.vcenter.get_vm_by_name(name_of_vm)
                state = vm.runtime.connectionState
                return state
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except VMUnavaiable as error:
            print(error.message)
            raise

    def rescan_hba(self,host_name,hba_adapter):
        """
        rescan_hba(self,host_name,hba_adapter): It Rescans for new storage devices for the given hba device.

        Variables:
            host_name(str): Name of the Esxi host.
            hba_adapter(str): The device name of the host bus adapter.

        Return:
            None
        """
        try:
            if self.vcenter:
                host = self.vcenter.get_host_by_name(name_of_host)

                host.configManager.storageSystem.RescanHba(hba_adapter)

                print("Hba device scanning is successful")
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except vim.fault.NotFound as error:
            print(error.msg)
            raise
        except vim.fault.HostConfigFault as error:
            print(error.msg)
            raise
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except HostUnavaiable as error:
            print(error.message)
            raise
        
    def rescan_all_hba(self,host_name):
        """
        rescan_all_hba(self,host_name): It rescans for new storage devices for all the host bus devices.
        
        Variables:
            host_name(str): Name of the Esxi host.

        Return:
            None


        """
        try:
            if self.vcenter:
                host = self.vcenter.get_host_by_name(name_of_host)

                host.configManager.storageSystem.RescanAllHba()

                print("Hba device scanning is successful")
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except HostUnavaiable as error:
            print(error.message)
            raise
        except vim.fault.HostConfigFault as error:
            print(error.msg)
            raise

    def hba_paths(self,name_of_host,hba_adapter):
        """
        hba_paths(self,name_of_host,hba_adapter): It restuns paths for the given adapter.

        Variables:
            name_of_name(str): Name of the host(ESXi).
            hba_adapter(str):  HBA adapter.

        Return:
            paths(list): List of the paths.

        """
        try:
            if self.vcenter:
                host = self.vcenter.get_host_by_name(name_of_host)
                adapters=host.configManager.storageSystem.storageDeviceInfo.plugStoreTopology.adapter
                paths = []

                for adapter in adapters:
                    if adapter.adapter.__contains__(hba_adapter):
                        #print(adapter)
                        paths=adapter.path
                        break
                return paths
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise
        except HostUnavaiable as error:
            print(error.message)
            raise


    def disconnect(self):
        """
        It disconnect the Vcenter conection.

        Return: None.

        """
        try:
            if self.vcenter:
                self.vcenter.disconnect()
            else:
                raise Vcenterconnectionerror()#("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
            raise     

    def reboot_host(self, name_of_host):
        '''Reboot Esxi host:
        It will reboot the given esxi host.
        Parameters: ip of the host, thst you want to reboot'''
        try:
            if self.vcenter:
                host = self.vcenter.get_host_by_name(name_of_host)
                force=True
                task = host.RebootHost_Task(force)
                while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                    time.sleep(1)
                status = task.info.state
                if status == "success":
                    logging.info("Rebooted the host successfully")
                if status == "error":
                    logging.info("errr: Unable to reboot the host")
                return status
            else:
                raise Vcenterconnectionerror()   #("Vcenter connection is not available")

        except Vcenterconnectionerror as error:
            print(error.message)
        except HostUnavaiable as error:
            print(error.message)
        except Exception as error:
            print(error.message)

    def shutdown_host(self, name_of_host):
        '''Reboot Esxi host:
        It will reboot the given esxi host.
        Parameters: ip of the host, thst you want to reboot'''
        try:
            if self.vcenter:
                host = self.vcenter.get_host_by_name(name_of_host)
                force=True
                task = host.ShutdownHost_Task(force)
                while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                    time.sleep(1)
                status = task.info.state
                if status == "success":
                    logging.info("shutdown the host successfully")
                if status == "error":
                    logging.info("errr: Unable to shutdown the host")
                return status
            else:
                raise Vcenterconnectionerror()   #("Vcenter connection is not available")

        except Vcenterconnectionerror as error:
            print(error.message)
        except HostUnavaiable as error:
            print(error.message)
        except Exception as err:
            print err.message

    def enter_maintanence_mode(self, name_of_host, timeout):
        '''Reboot Esxi host:
        It will reboot the given esxi host.
        Parameters: ip of the host, thst you want to reboot'''
        try:
            if self.vcenter:
                host = self.vcenter.get_host_by_name(name_of_host)
                force=True
                task = host.EnterMaintenanceMode_Task(timeout)
                while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                    time.sleep(1)
                status = task.info.state
                return status
            else:
                raise Vcenterconnectionerror()   #("Vcenter connection is not available")
        except Vcenterconnectionerror as error:
            print(error.message)
        except HostUnavaiable as error:
            print(error.message)
        except Exception as err:
            logging.info(err.message)
            logging.info("Failed to put into maintanencemode, something went wrong")

    def exit_maintanence_mode(self,name_of_host, timeout):
        '''Reboot Esxi host:
        It will reboot the given esxi host.
        Parameters: ip of the host, thst you want to reboot'''
        try:
            if self.vcenter:
                host = self.vcenter.get_host_by_name(name_of_host)
                force=True
                task = host.ExitMaintenanceMode_Task(force)
                while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                    time.sleep(1)
                status = task.info.state
                return status
            else:
                raise Vcenterconnectionerror()   #("Vcenter connection is not available")

        except Vcenterconnectionerror as error:
            print(error.message)
        except HostUnavaiable as error:
            print(error.message)
        except Exception as err:
            print(err.message)

    def disk_space_increase(self, vm_name, new_size, datacenter_name):
        '''Thsi will increses the diskspace of the given vm.
        While performing this operation , Vm will be powered off automatically if it is on and then verifies ,
        the newly given disk space with initial diskspace.
        The new disk space shuld be greater than the initial diskspace'''
        try:
            if self.vcenter:
                power_status = self.power_state(vm_name)
                if power_status == "poweredOn":
                    logging.info("powering off the vm...")
                    self.power_off(vm_name)
                initial_diskspace = self.vcenter.get_disk_space_of_vm(vm_name)
                new_size = int(new_size) * (1024*1024)
                if new_size > initial_diskspace:
                # Getting Vmdk for the given vm
                    vmdk = self.vcenter.get_vmdk(vm_name)
                    eagerzero = False
                    datacenter = self.vcenter.get_datacenter_by_name(datacenter_name)
                    # This will increase the disk space
                    task = self.vcenter.increase_disk(vmdk,datacenter,new_size,eagerzero)
                    time.sleep(15)
                    # Verifying weather disk sapce is is increaswed or not
                    new_diskspace = self.vcenter.get_disk_space_of_vm(vm_name)
                    if new_diskspace > initial_diskspace:
                        logging.info("Disk space increased succesfully")
                        # disk space of the VM After increasing
                        logging.info("New Disk space is : "+ str(new_diskspace/ (1024*1024)) + "GB")
                        return new_diskspace/ (1024*1024)
                    else:
                        logging.info("Disk space Not increased")
                        return -1
                else:
                    logging.info("The Initial capacity is :" + str(initial_diskspace/ (1024*1024) )+ "GB")
                    logging.info("The Given New capacity is: " + str(new_size/ (1024*1024))+ "GB")
                    logging.info("Newsize should be greater than Initial size")
                    return -1
            else:
                raise Vcenterconnectionerror()   #("Vcenter connection is not available")

        except Vcenterconnectionerror as error:
            print(error.message)
        except DatacenterUnavaiable as error:
            print(error.message)
        except VMUnavaiable as error:
            print(error.message)
        except Exception as err:
            print err.message

    def vmotion(self,vm_name, esx_host, pool_name):
        '''This method will performs the host migration.The vm should be powerd off while migrating.
        And this willl performs Host vmotion only.In vmware documentation , the resource pool parameter is,
        optional, but without resource pool , this functionality ill not work.
        We need to send the paramaters as targetted host
        parameters:  
        vm_name: Name of the Vm that you want to migrate
        esx_host: The Destination (or) Targeted Host, 
        pool : The Destination pool (or) Targeted pool
        '''
        try:
            if self.vcenter:
                # Finding source VM based on the name
                vm = self.vcenter.get_vm_by_name(vm_name)
                # Finding Targeted Host (or) Destination Host based on the host ip
                host = self.vcenter.get_host_by_name(esx_host)
                # Importent * finding resource pool based on the pool name
                # Here we need to give the ****destination pool******
                pool = self.vcenter.get_pool_by_name(pool_name)

                migrate_priority = vim.VirtualMachine.MovePriority.defaultPriority

                # Powering off the Vm 
                #power_status = self.power_state_vm(vm_name)
                #if power_status == "poweredOn":
                 #   self.power_off_vm(vm_name)
                if(vm and host and pool):
                    # relocate spec, to migrate to another host
                    # this can do other things, like storage migration
                    task = vm.Migrate(pool = pool, host = host, priority = migrate_priority)
                    while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                        time.sleep(1)
                    status = task.info.state
                    if status == "success":
                        logging.info("The given Vm "+ vm.name.upper() +", Migrated Successfully")
                        return status
                    elif status == "error":
                        logging.info("The given Vm "+ vm.name.upper() +", Failed to Migrate")
                        return status 
                elif(vm == None):
                    logging.info("The given vm not found")
                elif(host == None):
                    logging.info("The given Host not found")
                elif(pool == None):
                    logging.info("The given pool not found")

        except Vcenterconnectionerror as error:
            print(error.message)

        except HostUnavaiable as error:
            print(error.message)

        except VMUnavaiable as error:
            print(error.message)

        except PoolUnavailable as error:
            print(error.message)

        except vmodl.MethodFault, e:
            print "Caught vmodl fault: %s" % e.msg

        except Exception as e:
            print "Caught exception: %s" % str(e)
            print e.message


if __name__ =='__main__':
    #try:
        #import pdb; pdb.set_trace()
        V=VcenterOperations()
        V.connect("183.82.41.58","root","Nexii@123")
        # V.list_of_datacenters()
        # V.list_of_clusters()
        # V.cluster_exists_or_not('test2')
        print(V.list_of_hosts_under_cluster('compute_cluster'))
        # V.create_cluster('Nexiilabs', 'test1')
        # V.vm_snapshot("avinash", "avi_snap4", "test snapshot4", True, True)
        # V.disk_space_increase("avinash",14,"Nexiilabs")
        # V.vmotion("avinash", "192.168.50.16","fgw")
        # V.reboot_host("192.21.12.22")
        # V.shutdown_host("192.21.12.22")
        # V.enter_maintanence_mode("192.168.50.433",3000)
        # V.exit_maintanence_mode("192.168.50.433",3000)


        #print(V.num_of_cores('python'))
        #print(V.hba_paths('192.168.50.16','vmhba32'))
        #print(V.vm_state('python'))
        #print(V.vm_nics('VMware vCenter Server-18'))
        #V.increase_cpu('python',2)
        #V.decrease_cpu('python',1)
        #V.increase_memory('python',512)
        #V.decrease_memory('python',1024)
        #print(dir(V))
        #V.power_off('python')
        #V.power_on('python')
        #V.vm_storage('python1234')
        #print(V.vm_memory('python'))
        #print(V.vm_cpu('VMware vCenter Server-18'))
        #print(V.power_state("python234"))
    #(host="183.82.41.58",user="root",pwd="Vware@123")
    #except Exception as err:
        #print("error")
        #print(err)
        #pass
    #finally:
        #V.disconnect()
