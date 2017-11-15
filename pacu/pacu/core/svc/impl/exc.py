class ServiceException(Exception): pass
class UserAbortException(StopIteration): pass

class ServiceRuntimeException(ServiceException): pass

class TimeoutException(ServiceRuntimeException): pass
class ComponentNotFoundError(ServiceRuntimeException): pass

# class ServiceError(ServiceException): pass
# class ServiceImportError(ServiceError): pass
# class ServiceNotFoundError(ServiceError): pass
# class ServiceTypeError(ServiceError): pass
# class ServiceManifestoError(ServiceError): pass
# class ComponentInvalidError(ServiceError): pass
# class ComponentDependencyError(ServiceError): pass
# class ComponentArgumentError(ServiceError): pass
# class ComponentInitializationError(ServiceError): pass
# class SpecInvalidTypeError(ServiceError): pass
# class SpecInvalidValueError(ServiceError): pass
# class SpecUndefinedError(ServiceError): pass
# class TimeOutError(ServiceError): pass
