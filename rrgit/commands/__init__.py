from . clone import Clone
from . pull import Pull
from . status import Status

CommandMap = {
    'clone': Clone,
    'pull': Pull,
    'status': Status
}