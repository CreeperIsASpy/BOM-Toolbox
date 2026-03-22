#!/usr/bin/env python3
import os
import sys
import argparse
import codecs

def has_bom(filepath):
    """检测文件是否存在 UTF-8 BOM 头"""
    try:
        with open(filepath, 'rb') as f:
            return f.read(3) == codecs.BOM_UTF8
    except IOError:
        return False

def remove_bom(filepath):
    """移除文件的 UTF-8 BOM 头"""
    if not has_bom(filepath):
        return False
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        with open(filepath, 'wb') as f:
            f.write(content[3:])
        return True
    except IOError as e:
        print(f"处理文件 {filepath} 时出错: {e}")
        return False

def is_utf8(filepath):
    """检测文件是否为有效的 UTF-8 文件"""
    try:
        # 使用 codecs 按行读取，有效避免大文件撑爆内存
        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            for _ in f:
                pass
        return True
    except UnicodeDecodeError:
        return False
    except Exception:
        return False

def handle_remove(path):
    if not os.path.exists(path):
        print(f"错误：路径 '{path}' 不存在。")
        sys.exit(1)

    if os.path.isfile(path):
        if has_bom(path):
            remove_bom(path)
            print(f"已移除文件 {path} 的 BOM 头。")
        else:
            print(f"文件 {path} 不存在 BOM 头。")
            
    elif os.path.isdir(path):
        count = 0
        for root, dirs, files in os.walk(path):
            # 过滤掉隐藏文件夹（如 .git）以提升速度
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                filepath = os.path.join(root, file)
                if has_bom(filepath):
                    if remove_bom(filepath):
                        count += 1
                        
        if count > 0:
            print(f"已移除文件夹 {path} 中 {count} 个文件的 BOM 头。")
        else:
            print("该文件夹中无任何存在 BOM 头的文件。")

def handle_analyze(path, show_list):
    if not os.path.exists(path):
        print(f"错误：路径 '{path}' 不存在。")
        sys.exit(1)

    if os.path.isfile(path):
        if has_bom(path):
            print(f"文件 {path} 存在 BOM 头。")
        else:
            print(f"文件 {path} 不存在 BOM 头。")
            
    elif os.path.isdir(path):
        utf8_count = 0
        bom_files = []
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                filepath = os.path.join(root, file)
                if is_utf8(filepath):
                    utf8_count += 1
                    if has_bom(filepath):
                        bom_files.append(filepath)
                        
        bom_count = len(bom_files)
        percentage = (bom_count / utf8_count * 100) if utf8_count > 0 else 0
        # 格式化百分比，去掉末尾多余的 0
        formatted_percentage = f"{percentage:.2f}".rstrip('0').rstrip('.')

        print(f"文件夹 {path} 中有 {bom_count} 个文件存在 BOM 头，占文件夹中所有 UTF-8 文件的 {formatted_percentage} %。")
        
        if show_list and bom_count > 0:
            print("\n存在 BOM 头的文件列表：")
            for bf in bom_files:
                print(f"  - {bf}")

def main():
    parser = argparse.ArgumentParser(description="移除或检测文件的 UTF-8 BOM 头。")
    subparsers = parser.add_subparsers(dest="command", help="子命令 (remove / analyze)")
    subparsers.required = True

    # Subcommand: remove
    parser_remove = subparsers.add_parser("remove", help="移除特定文件或文件夹中文件的 BOM 头")
    parser_remove.add_argument("path", help="文件或文件夹的路径")

    # Subcommand: analyze
    parser_analyze = subparsers.add_parser("analyze", help="检测特定文件或文件夹中的文件是否存在 BOM 头")
    parser_analyze.add_argument("path", help="文件或文件夹的路径")
    parser_analyze.add_argument("--list", action="store_true", help="列出存在 BOM 头的文件（仅针对文件夹有效）")

    args = parser.parse_args()

    if args.command == "remove":
        handle_remove(args.path)
    elif args.command == "analyze":
        handle_analyze(args.path, args.list)

if __name__ == "__main__":
    main()
