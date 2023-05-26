import mimetypes
import os
import subprocess

from enum import Enum

from app.common.config import cfg
from process.modelConst import ModelName


def realesrganProcess(inputPath: str,
                      outputPath: str,
                      scale: int = 4,
                      tileSize: int = 0,
                      modelPath: str = None,
                      modelName: str = ModelName.REALESRGAN_X4PLUS.value,
                      gpuId: list = None,
                      loadProcSave: list = None,
                      enableTTA: bool = False,
                      outputFormat: str = None,
                      verboseOutput: bool = False):
    command = f"{cfg.exePos.value}/realesrgan-ncnn-vulkan.exe -i {inputPath} -o {outputPath} -s {scale} -t {tileSize}"
    if modelPath is not None:
        command += f" -m {modelPath}"
    command += f" -n {modelName}"
    if gpuId is not None:
        if len(gpuId) == 1:
            command += f" -g {gpuId[0]}"
        elif len(gpuId) == 3:
            command += f" -g {gpuId[0]},{gpuId[1]},{gpuId[2]}"
    if loadProcSave is not None:
        if len(loadProcSave) == 3:
            command += f" -j {loadProcSave[0]}:{loadProcSave[1]}:{loadProcSave[2]}"
        elif len(loadProcSave) == 5:
            command += f" -j {loadProcSave[0]}:{loadProcSave[1]},{loadProcSave[2]},{loadProcSave[3]}:{loadProcSave[4]}"
    if enableTTA:
        command += " -x"
    if outputFormat is not None:
        command += f" -f ext/{outputFormat}"
    if verboseOutput:
        command += " -v"

    print(command)
    return subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)


if __name__ == "__main__":
    p = realesrganProcess("input.jpg", "output.png")
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            print('Subprogram output: ', line)
    if p.returncode == 0:
        print('Subprogram success')
    else:
        print('Subprogram failed')

