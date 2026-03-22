> [!TIP]  
> ***This project is one of the THOUGHT OF THE DAY projects.***  
> ***该项目是“每日灵感记录”系列项目之一。***  
> *The development of these project may not be active.*  
> *这些项目的开发可能不会活跃。*  

### BOM Toolbox
usage: bom.py [-h] {remove,analyze} ...

移除或检测文件的 UTF-8 BOM 头。

positional arguments:
  {remove,analyze}  子命令 (remove / analyze)
    remove          移除特定文件或文件夹中文件的 BOM 头
    analyze         检测特定文件或文件夹中的文件是否存在 BOM 头

options:
  -h, --help        show this help message and exit


扫描大型文件夹请使用`bom_c.py`以获得更舒适体验（支持`--ext`白名单和`--exclude`黑名单）。
LICENSE: Apache Licese 2.0
欢迎使用。
