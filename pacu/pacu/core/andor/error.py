ERRORS = [
    ('AT_SUCCESS'                    , 0  , 'Function call has been successful.'),
    ('AT_ERR_NONINITIALISED'         , 1  , 'Function called with an uninitialized handle.'),
    ('AT_ERR_NOTIMPLEMENTED'         , 2  , 'Feature has not been implemented for the chosen camera.'),
    ('AT_ERR_READONLY'               , 3  , 'Feature is read only.'),
    ('AT_ERR_NOTREADABLE'            , 4  , 'Feature is currently not readable.'),
    ('AT_ERR_NOTWRITABLE'            , 5  , 'Feature is currently not writable.'),
    ('AT_ERR_OUTOFRANGE'             , 6  , 'Value is outside the maximum and minimum limits or The index passed to the function was either less than zero or greater than or equal to the number of implemented options.'),
    ('AT_ERR_INDEXNOTIMPLEMENTED'    , 8  , 'Index is not implemented for the chosen camera Index / String is not available.'),
    ('AT_ERR_EXCEEDEDMAXSTRINGLENGTH', 9  , 'String value provided exceeds the maximum allowed length.'),
    ('AT_ERR_CONNECTION'             , 10 , 'Error connecting to or disconnecting from hardware.'),
    ('AT_ERR_NODATA'                 , 11 , 'No Internal Event or Internal Error.'),
    ('AT_ERR_INVALIDHANDLE'          , 12 , 'Invalid device handle passed to function or The size of a queued buffer did not match the frame size for feature callback.'),
    ('AT_ERR_TIMEDOUT'               , 13 , 'The AT_WaitBuffer function timed out while waiting for data arrive in output queue.'),
    ('AT_ERR_BUFFERFULL'             , 14 , 'The input queue has reached its capacity.'),
    ('AT_ERR_INVALIDSIZE'            , 15 , 'The size of a queued buffer did not match the frame size.'),
    ('AT_ERR_INVALIDALIGNMENT'       , 16 , 'A queued buffer was not aligned on an 8-byte boundary.'),
    ('AT_ERR_COMM'                   , 17 , 'An error has occurred while communicating with hardware.'),
    ('AT_ERR_STRINGNOTAVAILABLE'     , 18 , 'Index / String is not available.'),
    ('AT_ERR_STRINGNOTIMPLEMENTED'   , 19 , 'Index / String is not implemented for the chosen camera.'),
    ('AT_ERR_NULL_FEATURE'           , 20 , 'NULL feature name passed to function.'),
    ('AT_ERR_NULL_HANDLE'            , 21 , 'Null device handle passed to function.'),
    ('AT_ERR_NULL_IMPLEMENTED_VAR'   , 22 , 'Feature not implemented.'),
    ('AT_ERR_NULL_READABLE_VAR'      , 23 , 'Readable not set.'),
    ('AT_ERR_NULL_WRITABLE_VAR'      , 25 , 'Writable not set.'),
    ('AT_ERR_NULL_MINVALUE'          , 26 , 'NULL min value.'),
    ('AT_ERR_NULL_MAXVALUE'          , 27 , 'NULL max value.'),
    ('AT_ERR_NULL_VALUE'             , 28 , 'NULL value returned from function.'),
    ('AT_ERR_NULL_STRING'            , 29 , 'NULL string returned from function.'),
    ('AT_ERR_NULL_COUNT_VAR'         , 30 , 'NULL feature count.'),
    ('AT_ERR_NULL_ISAVAILABLE_VAR'   , 31 , 'Available not set.'),
    ('AT_ERR_NULL_MAXSTRINGLENGTH'   , 32 , 'Max string length is NULL.'),
    ('AT_ERR_NULL_EVCALLBACK'        , 33 , 'EvCallBack parameter is NULL.'),
    ('AT_ERR_NULL_QUEUE_PTR'         , 34 , 'Pointer to queue is NULL.'),
    ('AT_ERR_NULL_WAIT_PTR'          , 35 , 'Wait pointer is NULL.'),
    ('AT_ERR_NULL_PTRSIZE'           , 36 , 'Pointer size is NULL.'),
    ('AT_ERR_NOMEMORY'               , 37 , 'No memory has been allocated for the current action.'),
    ('AT_ERR_DEVICEINUSE'            , 38 , 'Function failed to connect to a device because it is already being used.'),
    ('AT_ERR_HARDWARE_OVERFLOW'      , 100, 'The software was not able to retrieve data from the card or camera fast enough to avoid the internal hardware buffer bursting.'),
]

ERROR_DICT = {}

for code, number, message in ERRORS:
    ERROR_DICT[number] = message

def parse(number):
    return ERROR_DICT.get(number, 'Unknown Error')

class ZylaException(Exception):
    pass

class ZylaError(Exception):
    def __init__(self, number):
        self.number = number
    def __str__(self):
        return parse(self.number)
