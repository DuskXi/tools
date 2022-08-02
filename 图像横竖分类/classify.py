import os
import shutil
import sys
from collections import Counter
from enum import Enum
from rich.progress import Progress
from rich import print as rprint

from PIL import Image


class PictureType(Enum):
    Horizontal = 1
    Vertical = 2
    Square = 3
    Horizontal_Square_Approximate = 4
    Vertical_Square_Approximate = 5


def get_aspect_ratio(path):
    with Image.open(path) as image:
        return image.size


def get_picture_type(path, enable_approximate=False):
    width, height = get_aspect_ratio(path)
    if not enable_approximate:
        if width > height:
            return PictureType.Horizontal
        elif width < height:
            return PictureType.Vertical
        else:
            return PictureType.Square
    else:
        if height / width < 0.9:
            return PictureType.Horizontal
        elif height / width > 1.1:
            return PictureType.Vertical
        elif 0.9 <= height / width < 1:
            return PictureType.Horizontal_Square_Approximate
        elif 1 < height / width <= 1.1:
            return PictureType.Vertical_Square_Approximate
        else:
            return PictureType.Square


def get_files(path):
    results = []
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)):
            results.append(name)
    return results


def is_picture(path):
    return path.endswith('.jpg') or path.endswith('.png') or path.endswith('.jpeg')


def check_dst(path):
    if not os.path.exists(os.path.join(path, "horizontal")):
        os.makedirs(os.path.join(path, "horizontal"))
    if not os.path.exists(os.path.join(path, "vertical")):
        os.makedirs(os.path.join(path, "vertical"))
    if not os.path.exists(os.path.join(path, "square")):
        os.makedirs(os.path.join(path, "square"))


def store_to(src_file, dst_file):
    if not os.path.exists(dst_file):
        shutil.copyfile(src_file, dst_file)


def classify(base_path, parameters=[]):
    enable_approximate = "-a" in parameters or "--approximate" in parameters
    list_files = get_files(base_path)
    list_files = list(filter(lambda x: is_picture(os.path.join(base_path, x)), list_files))
    check_dst(base_path)
    base_horizontal = os.path.join(base_path, "horizontal")
    base_vertical = os.path.join(base_path, "vertical")
    base_square = os.path.join(base_path, "square")
    summaries = Counter([get_picture_type(os.path.join(base_path, x), enable_approximate) for x in list_files])
    summaries[PictureType.Horizontal] += summaries[PictureType.Horizontal_Square_Approximate] if PictureType.Horizontal_Square_Approximate in summaries.keys() else 0
    summaries[PictureType.Vertical] += summaries[PictureType.Vertical_Square_Approximate] if PictureType.Vertical_Square_Approximate in summaries.keys() else 0

    with Progress() as progress:
        task_h = progress.add_task('[red]竖图...', total=summaries[PictureType.Horizontal])
        task_v = progress.add_task('[green]横图...', total=summaries[PictureType.Vertical])
        task_s = progress.add_task('[blue]矩形...', total=summaries[PictureType.Square])
        for file in list_files:
            path = os.path.join(base_path, file)
            picture_type = get_picture_type(path, enable_approximate)
            if picture_type == PictureType.Horizontal:
                store_to(path, os.path.join(base_horizontal, file))
                progress.update(task_h, advance=1)
            elif picture_type == PictureType.Vertical:
                store_to(path, os.path.join(base_vertical, file))
                progress.update(task_v, advance=1)
            elif picture_type == PictureType.Square:
                store_to(path, os.path.join(base_square, file))
                progress.update(task_s, advance=1)
            elif picture_type == PictureType.Horizontal_Square_Approximate:
                store_to(path, os.path.join(base_horizontal, file))
                store_to(path, os.path.join(base_square, file))
                progress.update(task_h, advance=1)
                progress.update(task_s, advance=1)
            elif picture_type == PictureType.Vertical_Square_Approximate:
                store_to(path, os.path.join(base_vertical, file))
                store_to(path, os.path.join(base_square, file))
                progress.update(task_v, advance=1)
                progress.update(task_s, advance=1)


def main():
    path = None
    parameters = []
    for arg in sys.argv[1:]:
        if os.path.exists(arg):
            if path is not None:
                rprint(f'[red]路径参数过多[reset]')
                exit(0)
            path = arg
        if arg.startswith('-'):
            parameters.append(arg)

    if "-h" in parameters or "--help" in parameters:
        rprint(fr'[green]Usage: python3 {sys.argv[0]} [blue]\[path] [cyan]\[options]')
        rprint(f'[green]Options:')
        rprint(f'[yellow]  -h, --help: [reset]Show this help message and exit')
        rprint(f'[cyan]  -a, --approximate: 启用正方形近似分类')
        exit(0)
    if path is None:
        rprint(f'[red]无路径参数[reset]')
        exit(0)
    classify(path, parameters)


if __name__ == "__main__":
    main()
