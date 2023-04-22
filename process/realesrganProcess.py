import mimetypes
import os
import subprocess

import cv2
from fs.memoryfs import MemoryFS

from enum import Enum


class ModelName(Enum):
    # REALESR_ANIMEVEDIOV3 = "realesr-animevideov3"
    REALESRGAN_X4PLUS = "realesrgan-x4plus"
    REALESRGAN_X4PLUS_ANIME = "realesrgan-x4plus-anime"
    REALESRNET_X4PLUS = "realesrnet-x4plus"


def realesrganProcess(inputPath: str,
                      outputPath: str,
                      scale: int = 4,
                      tileSize: int = 0,
                      modelPath: str = None,
                      modelName: ModelName = ModelName.REALESRGAN_X4PLUS,
                      gpuId: list = None,
                      loadProcSave: list = None,
                      enableTTA: bool = False,
                      outputFormat: str = "ext/png",
                      verboseOutput: bool = False):
    command = f"./realesrgan-ncnn-vulkan-20220424-windows/realesrgan-ncnn-vulkan.exe -i {inputPath} -o {outputPath} -s {scale} -t {tileSize}"
    if modelPath is not None:
        command += f" -m {modelPath}"
    command += f" -n {modelName.value}"
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
    command += f" -f {outputFormat}"
    if verboseOutput:
        command += " -v"

    print(command)
    return subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


if __name__ == "__main__":
    memFs = MemoryFS
    p = realesrganProcess("input.jpg", "NUL")
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            print('Subprogram output: ', line)
    if p.returncode == 0:
        print('Subprogram success')
    else:
        print('Subprogram failed')

