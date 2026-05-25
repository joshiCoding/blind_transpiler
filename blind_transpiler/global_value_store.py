
class GlobalVariablesAndFunctions:

    def __init__(self):
        self.epsilon_precision = 1e-10
        self.M = self._define_M_using_epsilon_precision(self.epsilon_precision)

        # variables for classifition (not using rightnow) - Note first is taken as default
        self.blinding_format = ['qhe','fdqc','ssdqc','ubqc']
        self.random_key_style = ['rand','rand_fix','all_1','all_0']
        self.circuit_const_type = ['complete', 'client_only', 'server_only','encrypt_only']
        self.instr_type = ['client', 'enc', 'dec', 'compute', 'swap', 'trap' , 'measure']


        self.qhe_client_basis = ['x','z','swap','measure']
        self.qhe_server_basis = ['h', 's', 'cx','cz','ccx', 't', 'rz']
        self.qhe_compute_space = 1

        self.ssdqc_client_basis = ['x','z','swap','measure']
        self.ssdqc_server_basis = ['h', 's', 'sdg' ,'cx','cz','ccx', 't', 'tdg']
        self.ssdqc_compute_space = 3

        self.fdqc_client_basis = ['x','z','swap','measure']
        self.fdqc_server_basis = ['h', 's', 'sdg', 'cx','cz','ccx', 't', 'tdg']
        # self.fdqc_server_basis = ['h', 's', 't', 'sdg', 'tdg']
        self.fdqc_compute_space = 11

        self.ubqc_client_basis = ['x','z','swap','measure']
        self.ubqc_server_basis = ['h','cz', 'rz']
        self.ubqc_compute_space = 4


        # Note following identities have been used to find key size of tdg and sdg
        # sdq = s.s.s = z.s
        # tdg = t^7 = s.s.s.t = z.s.t
        self.qhe_key_map = {'h': 2, 's': 2, 'cx': 4, 'cz': 4, 'ccx': 18, 't': 4, 'rz': self._define_M2_using_epsilon_precision(self.epsilon_precision)}   # rz = 2 is temporary fix
        self.ssdqc_key_map = {'h': 6, 's': 6, 'sdg':6, 'cx': 6, 'cz': 6, 'ccx': 18, 't': 8, 'tdg': 8+6}
        self.fdqc_key_map = {'h': 2, 's': 2, 'sdg':2, 'cx': 4, 'cz': 4, 'ccx': 18, 't': 4, 'tdg':6}  
        self.ubqc_key_map = {'h': self._define_M2_using_epsilon_precision(self.epsilon_precision), 'cz': self._define_M2_using_epsilon_precision(self.epsilon_precision), 'rz': self._define_M2_using_epsilon_precision(self.epsilon_precision)}   # rz needs 2m keys



        # micro management settings
        self.optimization_level = 0 # sets the transpilation level to the least available
        self.recursion_degree = 5 # sets recursion to highest in solovay kitaev pass


    def _define_M_using_epsilon_precision(self, epsilon):
        from math import log, ceil,pi 
        return ceil(log(pi/epsilon))


    def _define_M2_using_epsilon_precision(self, epsilon):
        from math import log, ceil,pi 
        return (ceil(log(pi/epsilon)))**2


