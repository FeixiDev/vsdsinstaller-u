#! /usr/bin/env python3
import os
import re
import sys
import shutil
from base import Base

class Package:
    def __init__(self, logger):
        self.base = Base(logger)
        self.logger = logger
        self.software_versions = self.base.get_version_from_yaml("packages", self.install_from_yaml())
        self.nmcli_versions = self.base.get_version_from_yaml("nmcli", self.install_from_yaml())
        self.targetcli_versions = self.base.get_version_from_yaml("targetcli", self.install_from_yaml())
        
    def install(self, software, version=None):
        if software == "nmcli":
            software ="network-manager"
        if software == "targetcli":
            software ="targetcli-fb"
        command = f"apt install {software}"
        if version is not None:
            command += f"={version}"
            self.logger.log(f"安装 {software} 版本: {version}")
            print(f"安装 {software} 版本: {version}")
        else:
            print(f"安装 {software} 默认版本")
            self.logger.log(f"安装 {software} 的默认版本")
        command += " -y"

        # print(f"command: {command} ")
        result = self.base.com(command)
        self.logger.log(f"执行 {command} 的结果: {result.stdout}")
        # print(f"结果: {result.stdout} ")
        if "not found" in result.stdout:
            self.logger.log(f"安装 {software} 失败，版本: {version} 不存在")
            print(f"安装 {software} 失败，版本: {version} 不存在")
            sys.exit()
        print(f"安装 {software} 成功")
        return result

    def install_from_yaml(self):
        yaml_filename = "vsdsinstaller-u_config.yaml"
        yaml_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), yaml_filename)
        try:
            if not os.path.isfile(yaml_path):
                raise FileNotFoundError(f"未找到 {yaml_filename} 文件\n请检查配置文件是否在当前路径或者配置文件名称是否为config.yaml")
            return yaml_path
        except FileNotFoundError as e:
            print(e)  
            sys.exit()

    def install_package(self, software_name):
        if software_name in self.software_versions:
            version = self.software_versions[software_name]
            self.install(software_name, version)
        elif software_name in self.nmcli_versions:
            version = self.nmcli_versions[software_name]
            self.install(software_name, version)
        elif software_name in self.targetcli_versions:
            version = self.targetcli_versions[software_name]
            self.install(software_name, version)
        
    def version_remain(self, software_name, version=None):
        result = self.base.com("")
        match_ = None
        pacemaker_agents_match = None
        resource_agents_match = None
        nmcli_match = None
        targetcli_match = None
        if software_name in ["pacemaker-resource-agents", "resource-agents"]:
            result = self.base.com(f"apt-cache policy {software_name} | grep Installed")
            self.logger.log(f"apt-cache policy {software_name} | grep Installed 的执行结果: {result.stdout}")
            pacemaker_agents_match = re.search(r'Installed:\s(.+)', str(result.stdout))
            resource_agents_match = re.search(r'Installed:\s(.+)', str(result.stdout))
        elif software_name == "pacemaker":
            software_name_new = "pacemakerd"
            result = self.base.com(f"{software_name_new} --version")
            self.logger.log(f"{software_name} --version的执行结果: {result.stdout}")
            match_ = re.search(r'Pacemaker\s(.+)', str(result.stdout))
        elif software_name == "crmsh":
            software_name_new = "crm"
            result = self.base.com(f"{software_name_new} --version")
            self.logger.log(f"{software_name} --version的执行结果: {result.stdout}")
            match_ = re.search(r'crm\s(.+)', str(result.stdout))
        elif software_name == "corosync":
            result = self.base.com(f"{software_name} -v")
            self.logger.log(f"{software_name} -v的执行结果: {result.stdout}")
            match_ = re.search(r'version \'(.+?)\'', str(result.stdout)) # corosync 
        else:
            result = self.base.com(f"{software_name} --version")
            self.logger.log(f"{software_name} --version的执行结果: {result.stdout}")
            if software_name == "nmcli":
                software_name = "network-manager"
                nmcli_match = re.search(r'version (.+)', str(result.stdout))
            elif software_name == "targetcli":
                software_name = "targetcli-fb"
                targetcli_match = re.search(r'version (.+)', str(result.stdout))
    
        if "No such file" in result.stdout or "not found" in result.stdout or "Warning" in result.stdout:
            self.logger.log(f"{software_name} 未安装")
            print(f"{software_name} 未安装")
        elif version != None:
            print(f"安装 {software_name} 完成，版本: {version}\n")
        else:
            if match_:
                print(f"安装 {software_name} 完成，版本: {match_.group(1)}\n")
            elif pacemaker_agents_match:
                print(f"安装 {software_name} 完成，版本: {pacemaker_agents_match.group(1)}\n")
            elif resource_agents_match:
                print(f"安装 {software_name} 完成，版本: {resource_agents_match.group(1)}\n")
            elif nmcli_match:
                print(f"安装 {software_name} 完成，版本: {nmcli_match.group(1)}\n")
            elif targetcli_match:
                print(f"安装 {software_name} 完成，版本: {targetcli_match.group(1)}\n")
            else:
                self.logger.log(f"{software_name} 版本信息无法解析")
                print(f"{software_name} 版本信息无法解析\n")
            
    def check_versions(self, software_name):
        if software_name in self.software_versions:
            version = self.software_versions[software_name]
            # print(f"{software_name} version: {version}")
            self.version_remain(software_name, version)
        elif software_name in self.nmcli_versions:
            version = self.nmcli_versions[software_name]
            # print(f"{software_name} version: {version}")
            self.version_remain(software_name, version)
        elif software_name in self.targetcli_versions:
            version = self.targetcli_versions[software_name]
            # print(f"{software_name} version: {version}")
            self.version_remain(software_name, version)
        else:
            self.logger.log(f"未找到 {software_name} 的软件版本信息")
            print(f"未找到 {software_name} 的软件版本信息")

    def replace_files(self):
        # 获取当前脚本所在路径
        script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        
        # 定义目标路径
        target_path = "/usr/lib/ocf/resource.d/heartbeat"

        # 定义文件列表
        files_to_replace = ["iSCSILogicalUnit", "iSCSITarget"]

        # 检查目标路径是否存在
        if not os.path.exists(target_path):
            self.logger.log(f"目标路径 {target_path} 不存在")
            print(f"目标路径 {target_path} 不存在")
            raise FileNotFoundError(f"目标路径 {target_path} 不存在")

        # 检查每个文件是否存在并替换
        for file_name in files_to_replace:
            source_file_path = os.path.join(script_path, file_name)
            target_file_path = os.path.join(target_path, file_name)
            # print(f"source_file_path: {source_file_path}")
            # 检查文件是否存在
            if not os.path.isfile(source_file_path):
                self.logger.log(f"源文件 {file_name} 不存在于{source_file_path}")
                print(f"替换文件失败，源文件 {file_name} 不存在于{source_file_path}")
                raise FileNotFoundError(f"源文件 {file_name} 不存在")

            # 替换文件
            try:    
                shutil.copy(source_file_path, target_file_path)
                print(f"{file_name} 已成功替换到 {target_path}")
                self.logger.log(f"{file_name} 已成功替换到 {target_path}")

                # 修改文件权限为755（rwxr-xr-x）
                os.chmod(target_file_path, 0o755)
                # print(f"权限已更改为 755: {target_file_path}")
                self.logger.log(f"权限已更改为 755: {target_file_path}")
            except (shutil.Error, shutil.SameFileError, PermissionError) as e:
                print(f"替换文件时出现错误: {e}")
                self.logger.log(f"替换文件时出现错误: {e}")

    def check_replace_success(self):
        # 检查iSCSITarget
        command_1 = "grep -i 'iSCSITarget.mod_cache_gena_acl_0' iSCSITarget"
        # 检查iSCSILogicalUnit
        command_2 = "grep -i 'iSCSILogicalUnit.450_patch1476_mod' iSCSILogicalUnit"
        # 执行 grep 命令检查目标文件
        result_1 = self.base.com(command_1) 
        self.logger.log(f"执行 {command_1} 的结果: {result_1.stdout}")
        result_2 = self.base.com(command_2) 
        self.logger.log(f"执行 {command_2} 的结果: {result_2.stdout}")
        if "iSCSITarget.mod_cache_gena_acl_0" not in result_1.stdout:
            print("iSCSITarget 替换失败")
        if "iSCSILogicalUnit.450_patch1476_mod" not in result_2.stdout:
            print("iSCSILogicalUnit 替换失败")
        print("\n", end='')
