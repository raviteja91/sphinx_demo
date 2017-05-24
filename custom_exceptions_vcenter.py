
con_err_msg = "Vcenter connection is not available"

class VcenterException(Exception):
	pass

class Vcenterconnectionerror(VcenterException):
	def __init__(self):
		self.message = "Vcenter connection is not available"
		self.eNumber = 100

class VMUnavaiable(VcenterException):
	def __init__(self,vm_name):
		self.message = "%s VM is not available."%(vm_name)
		self.eNumber = 100

class HostUnavaiable(VcenterException):
	def __init__(self,host_name):
		self.message = " %s ESXi is not available"%(host_name)
		self.eNumber = 100

class DatacenterUnavaiable(VcenterException):
	def __init__(self,datacenter_name):
		self.message = " %s Datacenter is not available"%(datacenter_name)
		self.eNumber = 100
class PoolUnavailable(VcenterException):
	def __init__(self,pool_name):
		self.message = " %s Pool is not available"%(pool_name)
		self.eNumber = 100

class VMDiskUnavaiable(VcenterException):
	pass

class RVMUnavaiable(VcenterException):
	pass
class SVMUnavaiable(VcenterException):
	pass

class DatacentersUnavaiable(VcenterException):
	pass

class ClustersUnavaiable(VcenterException):
	pass