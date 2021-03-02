from . clone import Clone
from . pull import Pull
from . status import Status
from . push import Push
from .watch import Watch

CommandMap = {
    'clone': Clone,
    'status': Status,
    'pull': Pull,
    'push': Push,
    'watch': Watch,
}