from ..global_value_store import GlobalVariablesAndFunctions

class BaseTranslator:
    def __init__():
        None


    def _decompose_theta(self, theta):
        '''
        Decomposes the theta in integral power of series = a*pi + b*pi/2 + c*pi/4 + d*pi/8 + e*pi/16 + ..... (default= 20 precision points) approximatedly equal to theta, if theta is not integer power of pi/4.
        Helper function for encryption and decryption logic of 'rz' gate for qhe.
        Proper logic of the function:

            Case 1: exact expansion for n*pi/4 if n is integer.
            Case 2: approximate expansion if n is not integer.

        Args:
            theta: float - contain the theta parameter (in radian) to apply theta rotation on the circuit.
            precision: int - decides the number of terms in series = a*pi + b*pi/2 + c*pi/4 + d*pi/8 + e*pi/16 + .....

        Return:
            List[Literal[0,1]] - list of binary expansion, can be {0,1}, return the value [a,b,c,d,e,...]

        Raise: 
            None
            
        Library Dependency:
            math  - pi

        '''
        GVF = GlobalVariablesAndFunctions()
        from math import pi, log, ceil
        x = theta / pi  # Normalize to units of pi
        coeffs = []

        # Separate integer and fractional parts
        int_part = int(x)
        frac_part = x - int_part

        # Extract fractional bits
        M = GVF._define_M_using_epsilon_precision(GVF.epsilon_precision)
        for _ in range(M):
            frac_part *= 2
            bit = int(frac_part)
            coeffs.append(bit)
            frac_part -= bit

        return coeffs, int_part
    

    def _is_multiple(self, x, y, tol=1e-10):
        """
        Checks if x is a multiple of π/2 within a given tolerance.
        
        Parameters:
            x (float): number to check
            tol (float): tolerance for floating-point comparison
            
        Returns:
            (bool, int): True and multiple k if x ≈ k·(π/2), else False and None
        """

        k = x / y
        if abs(k - round(k)) < tol:
            return True
        return False
    
