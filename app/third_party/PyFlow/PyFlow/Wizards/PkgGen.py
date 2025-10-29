## Copyright 2015-2019 Ilgar Lunin, Pedro Cabrera

## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at

##     http://www.apache.org/licenses/LICENSE-2.0

## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.


import os
import shutil
from string import ascii_uppercase
from random import choice

from PyFlow import Wizards

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        pass

def generatePackage(
    packageName,
    newPackageRoot,
    bIncludeClassNode=True,
    bIncludeFooLib=True,
    bIncludeUINodeFactory=True,
    bIncludePin=True,
    bIncludeUIPinFactory=True,
    bIncludeTool=True,
    bIncludeExporter=True,
    bIncludePinInputWidgetFactory=True,
    bIncludePrefsWindget=False,
):
    wizardsRoot = Wizards.__path__[0]
    templatesRoot = os.path.join(wizardsRoot, "Templates")
    packageTemplateDirPath = os.path.join(templatesRoot, "PackageTemplate")
    newPackagePath = os.path.join(newPackageRoot, packageName)

    if os.path.exists(newPackagePath):
        shutil.rmtree(newPackagePath)
    shutil.copytree(packageTemplateDirPath, newPackagePath)

    for path, dirs, files in os.walk(newPackagePath):
        for newFileName in files:
            pyFileName = newFileName.replace(".txt", ".py")
            pyFilePath = os.path.join(path, pyFileName)
            txtFilePath = os.path.join(path, newFileName)
            with open(txtFilePath, "r") as f:
                txtContent = f.read()
                pyContent = txtContent.replace("@PACKAGE_NAME", packageName)
                pyContent = pyContent.replace(
                    "@RAND", "".join([choice(ascii_uppercase) for i in range(5)])
                )
                with open(pyFilePath, "w") as pf:
                    pf.write(pyContent)
            os.remove(txtFilePath)

    # remove unneeded directories
    for path, dirs, files in os.walk(newPackagePath):
        dirName = os.path.basename(path)
        if dirName == "Nodes" and not bIncludeClassNode:
            shutil.rmtree(path,ignore_errors=False,onexc=onerror) 
        if dirName == "FunctionLibraries" and not bIncludeFooLib:
            shutil.rmtree(path,ignore_errors=False,onexc=onerror) 
        if dirName == "Pins" and not bIncludePin:
            shutil.rmtree(path,ignore_errors=False,onexc=onerror) 
        if dirName == "Tools" and not bIncludeTool:
            shutil.rmtree(path,ignore_errors=False,onexc=onerror) 
        if dirName == "Exporters" and not bIncludeExporter:
            shutil.rmtree(path,ignore_errors=False,onexc=onerror) 
        if dirName == "PrefsWidgets" and not bIncludePrefsWindget:
            shutil.rmtree(path,ignore_errors=False,onexc=onerror) 
        if dirName == "Factories":
            removedFactoriesCount = 0

            if not bIncludeUINodeFactory:
                os.remove(os.path.join(path, "UINodeFactory.py"))
                removedFactoriesCount += 1
            if not bIncludeUIPinFactory:
                os.remove(os.path.join(path, "UIPinFactory.py"))
                removedFactoriesCount += 1
            if not bIncludePinInputWidgetFactory:
                os.remove(os.path.join(path, "PinInputWidgetFactory.py"))
                removedFactoriesCount += 1

            if removedFactoriesCount == 3:
                shutil.rmtree(path,ignore_errors=False,onexc=onerror)

        if dirName == "UI":
            removedUIClasses = 0

            if not bIncludePin or not bIncludeUIPinFactory:
                os.remove(os.path.join(path, "UIDemoPin.py"))
                removedUIClasses += 1

            if not bIncludeClassNode or not bIncludeUINodeFactory:
                os.remove(os.path.join(path, "UIDemoNode.py"))
                removedUIClasses += 1

            if removedUIClasses == 2:
                shutil.rmtree(path,ignore_errors=False,onexc=onerror)
