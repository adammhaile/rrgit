from . clone import Clone
from . pull import Pull
from . status import Status
from . push import Push

CommandMap = {
    'clone': Clone,
    'status': Status,
    'pull': Pull,
    'push': Push
}