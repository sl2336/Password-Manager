"""
A module for accessing the Touch ID sensor in your Mac's Touch Bar.

Requires pyobjc to be installed
"""

import sys
#ctypes is a foreign function library for Python. It provides C compatible data types which we use below
#also alows you access to C libraries and call them in python scripts
import ctypes
#MacOS framework to interact with Touch ID functionality
#pyobjc is the python wrapper we use to interact with this C package
from LocalAuthentication import LAContext
#Policy we will use for authentication
#Policy evaluation fails if Touch ID or Face ID is unavailable or not enrolled
#also fails after three failed Touch ID attempts
from LocalAuthentication import LAPolicyDeviceOwnerAuthenticationWithBiometrics

#touch id policy
kTouchIdPolicy = LAPolicyDeviceOwnerAuthenticationWithBiometrics

#not 100% sure, but loadlibrary function allows you to load in any compiled c code (.so files)
#here we are loading in the default c library
c = ctypes.cdll.LoadLibrary(None)

#Checks what version of python we are running
PY3 = sys.version_info[0] >= 3
if PY3:
    DISPATCH_TIME_FOREVER = sys.maxsize
else:
    DISPATCH_TIME_FOREVER = sys.maxint

#a semaphore is a variable that controls access to a resource
#in this case its an integer that can increase by one (signal)
#or decrement by one (wait)
#see this video on semaphores
#https://www.youtube.com/watch?v=ukM_zzrIeXs&ab_channel=JacobSorber
dispatch_semaphore_create = c.dispatch_semaphore_create
dispatch_semaphore_create.restype = ctypes.c_void_p
dispatch_semaphore_create.argtypes = [ctypes.c_int]

dispatch_semaphore_wait = c.dispatch_semaphore_wait
dispatch_semaphore_wait.restype = ctypes.c_long
dispatch_semaphore_wait.argtypes = [ctypes.c_void_p, ctypes.c_uint64]

dispatch_semaphore_signal = c.dispatch_semaphore_signal
dispatch_semaphore_signal.restype = ctypes.c_long
dispatch_semaphore_signal.argtypes = [ctypes.c_void_p]


def is_available():
    context = LAContext.new()
    return context.canEvaluatePolicy_error_(kTouchIdPolicy, None)[0]


def authenticate(reason='authenticate via Touch ID'):
    context = LAContext.new()

    can_evaluate = context.canEvaluatePolicy_error_(kTouchIdPolicy, None)[0]
    if not can_evaluate:
        raise Exception("Touch ID isn't available on this machine")

    sema = dispatch_semaphore_create(0)

    # we can't reassign objects from another scope, but we can modify them
    res = {'success': False, 'error': None}

    def cb(_success, _error):
        res['success'] = _success
        if _error:
            res['error'] = _error.localizedDescription()
        dispatch_semaphore_signal(sema)
    
    #this function will first check our policy, if true
    #then it will prompt user for authentication
    #and will call the reply function (reply is the 3rd param in this function)
    #with if successful: _success = True and _error = nil
    #with if unsucessful: _success = False and _error = LAError
    context.evaluatePolicy_localizedReason_reply_(kTouchIdPolicy, reason, cb)
    dispatch_semaphore_wait(sema, DISPATCH_TIME_FOREVER)

    if res['error']:
        raise Exception(res['error'])

    return res['success']
