import os

import pandas as pd
import argparse


def main(args):
    input_dir = args.input
    output_dir = args.output
    interactive = args.interactive
    if interactive:
        input_dir = input("input dir(xlsx文件目录):")
        output_dir = input("output dir(输出目录):")
    if not os.path.exists(input_dir):
        print("input dir not exists")
        return
    if not os.path.exists(output_dir):
        print("output dir not exists, create it")
        os.makedirs(output_dir)
    files = [x for x in os.listdir(input_dir) if x.endswith(".xlsx")]
    if len(files) == 0:
        print("no xlsx file found")
        return
    if len(files) == 1:
        print("only one xlsx file found")
        return

    # take head from first xlsx, and merge remain xlsx
    head = pd.read_excel(os.path.join(input_dir, files[0]))
    for file in files[1:]:
        df = pd.read_excel(os.path.join(input_dir, file))
        # concatenate by vertical and ingore index and header
        head = pd.concat([head, df], axis=0, ignore_index=True, sort=False)
    out_name = "merged.xlsx"
    files_in_outdir = [x for x in os.listdir(output_dir) if x.endswith(".xlsx")]
    i = 0
    while out_name in files_in_outdir:
        i += 1
        out_name = "merged_{}.xlsx".format(i)
    head.to_excel(os.path.join(output_dir, out_name), index=False)


def parse_args():
    parser = argparse.ArgumentParser(description="excel merge")
    parser.add_argument("-i", "--input", type=str, help="dir that have xlsx file", default=".")
    parser.add_argument("-o", "--output", type=str, help="output dir", default="./output")
    parser.add_argument("-I", "--interactive",  help="interactive mode", action='store_true', default=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
