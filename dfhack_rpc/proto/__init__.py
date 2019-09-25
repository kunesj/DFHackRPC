# Build instructions
# ==================
#
# raw source:
#   https://github.com/DFHack/dfhack/tree/master/library/proto
#   https://github.com/DFHack/dfhack/tree/master/plugins/proto
#
# install compiler:
#   sudo apt install protobuf-compiler
#
# compile:
#   protoc -I=./raw_proto --python_out=./ ./raw_proto/*.proto
#
# fix imports:
#   import ItemdefInstrument_pb2 as ItemdefInstrument__pb2
#   from . import ItemdefInstrument_pb2 as ItemdefInstrument__pb2
#

from google.protobuf import symbol_database

proto_db = symbol_database.Default()

from . import Basic_pb2
from . import BasicApi_pb2
from . import CoreProtocol_pb2

from . import AdventureControl_pb2
from . import ItemdefInstrument_pb2
from . import rename_pb2
from . import isoworldremote_pb2
from . import RemoteFortressReader_pb2
