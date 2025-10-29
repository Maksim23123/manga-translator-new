## Copyright 2015-2025 Ilgar Lunin, Pedro Cabrera

## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at

##     http://www.apache.org/licenses/LICENSE-2.0

## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.


from PyFlow.Packages.PyFlowBase.UI.UIImageDisplayNode import UIImageDisplayNode

from PyFlow.Packages.PyFlowBase.UI.UIStoreArgsNode import UIStoreArgs
from PyFlow.Packages.PyFlowBase.UI.UICombineArgsNode import UICombineArgs
from PyFlow.Packages.PyFlowBase.UI.UISubProcessNode import UISubProcess
from PyFlow.Packages.PyFlowBase.UI.UISwitchNode import UISwitch
from PyFlow.Packages.PyFlowBase.UI.UIGetVarNode import UIGetVarNode
from PyFlow.Packages.PyFlowBase.UI.UISetVarNode import UISetVarNode
from PyFlow.Packages.PyFlowBase.UI.UISequenceNode import UISequenceNode
from PyFlow.Packages.PyFlowBase.UI.UICommentNode import UICommentNode
from PyFlow.Packages.PyFlowBase.UI.UIStickyNote import UIStickyNote
from PyFlow.Packages.PyFlowBase.UI.UIRerouteNodeSmall import UIRerouteNodeSmall
from PyFlow.Packages.PyFlowBase.UI.UIPythonNode import UIPythonNode
from PyFlow.Packages.PyFlowBase.UI.UIGraphNodes import UIGraphInputs, UIGraphOutputs
from PyFlow.Packages.PyFlowBase.UI.UIFloatRamp import UIFloatRamp
from PyFlow.Packages.PyFlowBase.UI.UIColorRamp import UIColorRamp

from PyFlow.Packages.PyFlowBase.UI.UICompoundNode import UICompoundNode
from PyFlow.Packages.PyFlowBase.UI.UIConstantNode import UIConstantNode
from PyFlow.Packages.PyFlowBase.UI.UIConvertToNode import UIConvertToNode
from PyFlow.Packages.PyFlowBase.UI.UIMakeDictNode import UIMakeDictNode
from PyFlow.Packages.PyFlowBase.UI.UIForLoopBeginNode import UIForLoopBeginNode
from PyFlow.Packages.PyFlowBase.UI.UIWhileLoopBeginNode import UIWhileLoopBeginNode

from PyFlow.UI.Canvas.UINodeBase import UINodeBase

def createUINode(raw_instance):
    if raw_instance.__class__.__name__ == "getVar":
        return UIGetVarNode(raw_instance)
    if raw_instance.__class__.__name__ == "setVar":
        return UISetVarNode(raw_instance)
    if raw_instance.__class__.__name__ == "subProcess":
        return UISubProcess(raw_instance)
    if raw_instance.__class__.__name__ == "storeArgs":
        return UIStoreArgs(raw_instance)
    if raw_instance.__class__.__name__ == "combineArgs":
        return UICombineArgs(raw_instance)
    if raw_instance.__class__.__name__ == "switch":
        return UISwitch(raw_instance)
    if raw_instance.__class__.__name__ == "sequence":
        return UISequenceNode(raw_instance)
    if raw_instance.__class__.__name__ == "commentNode":
        return UICommentNode(raw_instance)
    if raw_instance.__class__.__name__ == "stickyNote":
        return UIStickyNote(raw_instance)
    if raw_instance.__class__.__name__ == "reroute" or raw_instance.__class__.__name__ == "rerouteExecs":
        return UIRerouteNodeSmall(raw_instance)
    if raw_instance.__class__.__name__ == "graphInputs":
        return UIGraphInputs(raw_instance)
    if raw_instance.__class__.__name__ == "graphOutputs":
        return UIGraphOutputs(raw_instance)
    if raw_instance.__class__.__name__ == "compound":
        return UICompoundNode(raw_instance)
    if raw_instance.__class__.__name__ == "pythonNode":
        return UIPythonNode(raw_instance)
    if raw_instance.__class__.__name__ == "constant":
        return UIConstantNode(raw_instance)
    if raw_instance.__class__.__name__ == "convertTo":
        return UIConvertToNode(raw_instance)
    if raw_instance.__class__.__name__ == "makeDict":
        return UIMakeDictNode(raw_instance)
    if raw_instance.__class__.__name__ == "makeAnyDict":
        return UIMakeDictNode(raw_instance)
    if raw_instance.__class__.__name__ == "floatRamp":
        return UIFloatRamp(raw_instance)
    if raw_instance.__class__.__name__ == "colorRamp":
        return UIColorRamp(raw_instance)
    if raw_instance.__class__.__name__ == "imageDisplay":
        return UIImageDisplayNode(raw_instance)
    if raw_instance.__class__.__name__ == "forLoopBegin":
        return UIForLoopBeginNode(raw_instance)
    if raw_instance.__class__.__name__ == "whileLoopBegin":
        return UIWhileLoopBeginNode(raw_instance)
    return UINodeBase(raw_instance)
