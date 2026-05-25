from ..global_value_store import GlobalVariablesAndFunctions 

class BaseController:
    """
    Base controller defining utility fucntions for Controllers and Orchestrator
    """
    def __init__(self):
        """
        Class containing necessary functions and variables to call the translator properly.

        """

        # input variables
        GVF = GlobalVariablesAndFunctions()

        self.circ = None 
        self.transpiled_circ = None
        self.format = None

        self.client_basis = None 
        self.server_basis = None 
        self.default_basis_gates = None

        self.qhe_key_map = GVF.qhe_key_map 
        self.fdqc_key_map = GVF.fdqc_key_map
        self.ssdqc_key_map = GVF.ssdqc_key_map
        self.ubqc_key_map = GVF.ubqc_key_map
        self.key_estimate = {'qhe': self.qhe_key_map, 'fdqc': self.fdqc_key_map, 'ssdqc': self.ssdqc_key_map, 'ubqc': self.ubqc_key_map}

    def _generate_basis(self, format):
        """
        Defines the basis set for client, and server based on the format
        Also calculates the estimated key space base on default values store in global_variable_store

        Args:
            format: defines the type of algorithm running can take one of four values ['qhe', 'fdqc', 'ssdqc', 'ubqc']

        Returns:
            None

        Raises:
            ValueError(f'format "{format}" not defined. Give from list ["qhe","fdqc","ssdqc","ubqc"]')

        """
        GVF = GlobalVariablesAndFunctions()

        if format == 'qhe':
            self.client_basis = GVF.qhe_client_basis
            self.server_basis = GVF.qhe_server_basis
        elif format == 'ssdqc':
            # print('running ssdqc client basis')
            self.client_basis = GVF.ssdqc_client_basis
            self.server_basis = GVF.ssdqc_server_basis
        elif format == 'fdqc':
            self.client_basis = GVF.fdqc_client_basis
            self.server_basis = GVF.fdqc_server_basis
        elif format == 'ubqc':
            self.client_basis = GVF.ubqc_client_basis
            self.server_basis = GVF.ubqc_server_basis
        else:
            raise ValueError(f'format "{format}" not defined. Give from list ["qhe","fdqc","ssdqc","ubqc"]')

        self.default_basis_gates = [*self.client_basis, *self.server_basis]


    def _create_translation_map(self, library_obj, format):
        """
        Contain dictionary of gate fucntion and keys needed to encrypt the gate. 
        All the gates from the server should be here
        
        Args:
            library_obj (class obj):
                object of one of classes present in translator file. It can be:
                    'HomomorphicTranslation()', 
                    'FDQC()', 
                    'RotationBasedBlindTranslation'.
        Returns:
            translation_map (dict{str->class function pointer})
                ist of gate and the function that performs the blind transformation on it.
            
        """

        self._generate_basis(format)
        translation_map = {}
        for gate in self.server_basis:
            translation_map[gate] = getattr(library_obj, gate, None)
        return translation_map
    
