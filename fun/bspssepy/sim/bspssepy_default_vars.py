# ===========================================================
#   BSPSSEPy Application - Default PSSE Variable Retrieval
# ===========================================================
#   This module provides a function to retrieve the default
#   integer, real (float), and character values from PSSE.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================

# pyright: reportMissingImports=false
import psspy  # noqa: F401 pylint: disable=import-error 


def bspssepy_default_vars_fun(debug_print=False):
    """
    Retrieves the default integer, real, and character values from PSSE.

    This function queries PSSE's built-in default values for different
    data types. These values are used in simulation cases where a parameter
    needs to be left at its default value rather than being explicitly defined.

    Parameters:
        debug_print (bool, optional): If True, prints debug messages with the
        retrieved values.

    Returns:
        tuple:
            - default_int (int): Default integer value used by PSSE.
            - default_real (float): Default real (float) value used by PSSE.
            - default_char (str): Default character value used by PSSE.

    Notes:
        - PSSE provides built-in default values that are useful for keeping
          parameter values unchanged when modifying only specific attributes.
        - Additional default types such as strings and complex numbers can be
          added in the future if required.
    """

    # ==========================
    #  Retrieve Default Values
    # ==========================
    default_int = psspy.getdefaultint()
    default_real = psspy.getdefaultreal()
    default_char = psspy.getdefaultchar()
    # DefaultString = psspy._s
    # DefaultComplex = psspy._c

    # , DefaultString, DefaultComplex

    if debug_print:
        print(f"[DEBUG] Retrieved Default Values: Int={default_int},"
              f"Real={default_real}, Char='{default_char}'")

    return default_int, default_real, default_char
