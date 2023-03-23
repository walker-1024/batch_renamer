
import os
import hashlib
import PySimpleGUI as sg


def renameFile(filePath: str, nameRule: str, shouldRenameWhenHaveSameFileNameSameMd5: bool = False, shouldRenameWhenHaveSameFileNameDifferentMd5: bool = False):
    if len(filePath) == 0 or len(nameRule) == 0:
        return
    if not os.path.exists(filePath):
        return
    if os.path.isdir(filePath):
        return
    if "$(md5)" not in nameRule:
        print("Error: 新名称规则中必须包含 `$(md5)`")
        return

    with open(filePath, "rb") as f:
        theMd5 = hashlib.md5(f.read()).hexdigest().upper()
    dirPath, fileName = os.path.split(filePath)
    fileExt = fileName.split(".")[-1]
    newFileName = nameRule.replace("$(md5)", theMd5) + "." + fileExt
    newFilePath = os.path.join(dirPath, newFileName)

    if filePath == newFilePath:
        return

    if os.path.exists(newFilePath):
        with open(newFilePath, "rb") as f:
            theExistFileMd5 = hashlib.md5(f.read()).hexdigest().upper()
        if shouldRenameWhenHaveSameFileNameSameMd5 and theMd5 == theExistFileMd5:
            os.rename(filePath, newFilePath)
        elif shouldRenameWhenHaveSameFileNameDifferentMd5 and theMd5 != theExistFileMd5:
            os.rename(filePath, newFilePath)
        else:
            print(f"已跳过文件: {filePath}")
    else:
        os.rename(filePath, newFilePath)


def run(path: str, shouldParseSubDir: bool, nameRule: str, ignoreFileStartWithPoint: bool = True, shouldRenameWhenHaveSameFileNameSameMd5: bool = False):
    # isInOuterRecursion 表示是否处于最外层的递归
    def innerRun(path: str, isInOuterRecursion: bool = True):
        if len(path) == 0 or len(nameRule) == 0:
            return
        if not os.path.exists(path):
            return
        if ignoreFileStartWithPoint:
            for item in path.split(os.path.sep):
                if item.startswith("."):
                    return

        if os.path.isdir(path):
            if isInOuterRecursion or shouldParseSubDir:
                fileList = os.listdir(path)
                for item in fileList:
                    innerRun(os.path.join(path, item), isInOuterRecursion=False)
        else:
            renameFile(path, nameRule, shouldRenameWhenHaveSameFileNameSameMd5=shouldRenameWhenHaveSameFileNameSameMd5)

    innerRun(path)


def runGUI():
    layout = [
        [sg.Text("注意先备份原文件！\n")],
        [sg.Text("要批量改名的文件所在的文件夹路径："), sg.InputText(key="dirPath"), sg.FolderBrowse("选择文件夹")],
        [sg.Checkbox("处理子文件夹中的文件", key="shouldParseSubDir")],
        [sg.Text("新名称规则：\n* 不需要包含文件后缀\n* 需包含 `$(md5)`，将被替换为文件md5")],
        [sg.InputText(key="nameRule")],
        [sg.Checkbox("忽略 `.` 开头的文件和文件夹，如 `.DS_Store`", default=True, key="ignoreFileStartWithPoint")],
        [sg.Checkbox("当新名称已存在文件且这两个文件md5相同时仍进行重命名", key="shouldRenameWhenHaveSameFileNameSameMd5")],
        [sg.Button("执行")],
        [sg.Output(size=(100, 10))]
    ]

    window = sg.Window("batch_renamer", layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "执行":
            dirPath = values.get("dirPath")
            shouldParseSubDir = values.get("shouldParseSubDir")
            nameRule = values.get("nameRule")
            ignoreFileStartWithPoint = values.get("ignoreFileStartWithPoint")
            shouldRenameWhenHaveSameFileNameSameMd5 = values.get("shouldRenameWhenHaveSameFileNameSameMd5")
            if len(dirPath) > 0 and len(nameRule) > 0:
                try:
                    run(dirPath, shouldParseSubDir=shouldParseSubDir, nameRule=nameRule, ignoreFileStartWithPoint=ignoreFileStartWithPoint, shouldRenameWhenHaveSameFileNameSameMd5=shouldRenameWhenHaveSameFileNameSameMd5)
                    print("执行完成")
                except Exception as e:
                    print(f"Exception: {e}")

    window.close()


if __name__ == "__main__":
    runGUI()

