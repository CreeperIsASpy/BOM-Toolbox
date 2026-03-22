#!/usr/bin/env python3
import os
import sys
import argparse
import codecs

try:
    from tqdm import tqdm
except ImportError:
    print("错误：缺少 tqdm 库。")
    print("请先运行：pip install tqdm (或 uv pip install tqdm)")
    sys.exit(1)

def has_bom(filepath):
    try:
        with open(filepath, 'rb') as f:
            return f.read(3) == codecs.BOM_UTF8
    except IOError:
        return False

def remove_bom(filepath):
    if not has_bom(filepath):
        return False
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        with open(filepath, 'wb') as f:
            f.write(content[3:])
        return True
    except IOError as e:
        tqdm.write(f"处理文件 {filepath} 时出错: {e}")
        return False

def is_utf8(filepath):
    try:
        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            for _ in f:
                pass
        return True
    except (UnicodeDecodeError, IOError):
        return False
    except Exception:
        return False

def is_allowed_file(file, ext_whitelist, ext_blacklist):
    if ext_blacklist and any(file.lower().endswith(ext.lower()) for ext in ext_blacklist):
        return False
    if ext_whitelist and not any(file.lower().endswith(ext.lower()) for ext in ext_whitelist):
        return False
    return True

def handle_remove(path, exts, excludes):
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
        with tqdm(unit="文件", dynamic_ncols=True) as pbar:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('$') and d != "System Volume Information"]
                
                # 动态更新当前正在扫描的文件夹路径 (超过 40 字符则截断保留末尾)
                display_path = root if len(root) <= 40 else "..." + root[-37:]
                pbar.set_description(f"正在扫描: {display_path:<40}")
                
                for file in files:
                    pbar.update(1)  # 【修复】：不管通没通过过滤，都算作扫过了一个文件
                    
                    if not is_allowed_file(file, exts, excludes):
                        continue
                        
                    filepath = os.path.join(root, file)
                    if has_bom(filepath):
                        if remove_bom(filepath):
                            count += 1
                        
        if count > 0:
            print(f"\n已移除文件夹 {path} 中 {count} 个文件的 BOM 头。")
        else:
            print("\n该文件夹中无任何存在 BOM 头的文件。")

def handle_analyze(path, show_list, exts, excludes):
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
        
        with tqdm(unit="文件", dynamic_ncols=True) as pbar:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('$') and d != "System Volume Information"]
                
                # 动态更新当前正在扫描的文件夹路径
                display_path = root if len(root) <= 40 else "..." + root[-37:]
                # 使用 :<40 强制左对齐填充空格，防止路径长度变化导致进度条一直抖动
                pbar.set_description(f"正在分析: {display_path:<40}")
                
                for file in files:
                    pbar.update(1) # 【修复】：计步器提前，真实反映底层扫描速度
                    
                    if not is_allowed_file(file, exts, excludes):
                        continue
                        
                    filepath = os.path.join(root, file)
                    if is_utf8(filepath):
                        utf8_count += 1
                        if has_bom(filepath):
                            bom_files.append(filepath)
                        
        bom_count = len(bom_files)
        
        print(f"\n\n分析完成！")
        if utf8_count == 0:
             print(f"在过滤后的文件中，未发现任何有效的 UTF-8 文本文件。")
        else:
            percentage = (bom_count / utf8_count * 100)
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

    parser_remove = subparsers.add_parser("remove", help="移除特定文件或文件夹中文件的 BOM 头")
    parser_remove.add_argument("path", help="文件或文件夹的路径")
    parser_remove.add_argument("--ext", nargs='+', help="【白名单】仅处理指定的扩展名")
    parser_remove.add_argument("--exclude", nargs='+', help="【黑名单】跳过指定的扩展名")

    parser_analyze = subparsers.add_parser("analyze", help="检测特定文件或文件夹中的文件是否存在 BOM 头")
    parser_analyze.add_argument("path", help="文件或文件夹的路径")
    parser_analyze.add_argument("--list", action="store_true", help="列出存在 BOM 头的文件")
    parser_analyze.add_argument("--ext", nargs='+', help="【白名单】仅分析指定的扩展名")
    parser_analyze.add_argument("--exclude", nargs='+', help="【黑名单】跳过指定的扩展名")

    args = parser.parse_args()

    if args.command == "remove":
        handle_remove(args.path, args.ext, args.exclude)
    elif args.command == "analyze":
        handle_analyze(args.path, args.list, args.ext, args.exclude)

if __name__ == "__main__":
    main()
