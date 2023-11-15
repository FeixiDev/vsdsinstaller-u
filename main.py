#! /usr/bin/env python3

import argparse
from log_record import Logger
from package import Package

# 安装Pacemaker & Corosync & Crmsh
def install_package(package):

    software_names = ["pacemaker", "corosync", "crmsh", "pacemaker-resource-agents", "resource-agents"]
    for software_name in software_names:
        package.install_package(software_name)
        package.check_versions(software_name)

# 替换RA
def replace_RA(package):
    package.replace_files()
    package.check_replace_success()

# nmcli安装
def nmcli_(package):
    package.install_package("nmcli")
    package.check_versions("nmcli")

# targetcli安装
def targetcli_(package):
    package.install_package("targetcli")
    package.check_versions("targetcli")

def display_version():
    print("version: v1.0.0")

def main():
    parser = argparse.ArgumentParser(description='None')
    parser.add_argument('-p', '--package', action='store_true',
                        help='Pacemaker & Corosync & Crmsh')
    parser.add_argument('-r', '--RA', action='store_true',
                        help='replace RA')
    parser.add_argument('-n', '--nmcli', action='store_true',
                        help='install nmcli')
    parser.add_argument('-t', '--targetcli', action='store_true',
                        help='install targetcli_')
    parser.add_argument('-v', '--version', action='store_true',
                        help='Show version information')
    args = parser.parse_args()

    logger = Logger("log")
    package = Package(logger)
    
    if args.package:
        install_package(package)
    elif args.RA:
        replace_RA(package)
    elif args.nmcli:
        nmcli_(package)
    elif args.targetcli:
        targetcli_(package)
    elif args.version:
        display_version()
    else:
        install_package(package)
        replace_RA(package)
        nmcli_(package)
        targetcli_(package)

if __name__ == '__main__':
    main()
