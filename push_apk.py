#!user/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import zipfile

import re

import shutil


class apk_push_utils:
    # unintall list
    apk_list = ["com.tuyou.tsd.audio",
                "com.tuyou.tsd.cardvr",
                "com.tuyou.tsd",
                "com.tuyou.tsd.navigation",
                "com.tuyou.tsd.news",
                "com.tuyou.tsd.podcast",
                "com.tuyou.tsd.settings",
                "com.tuyou.tsd.updatesoft",
                "com.tuyou.tsd.voice",
                "com.tuyou.tsd.collector",
                "com.tuyou.tsd.bluetooth",
                "com.mct.carlinkui.bluetooth",
                "com.tuyou.tsd.dday.mediaserver",
                "com.tuyou.tsd.system"]
    # 获取系统版本
    def get_os_version(self):
        command_get_os = "adb shell getprop ro.build.version.sdk"
        p = subprocess.Popen(command_get_os, stdout=subprocess.PIPE, stderr=None, shell=True)
        version_code = p.communicate()[0]
        return version_code

    # 获取包名
    def get_packagename(self, apk):
        command_getpackagename = "aapt d badging " + apk
        p = subprocess.Popen(command_getpackagename, stdout=subprocess.PIPE, stderr=None, shell=True)
        p_communicate = p.communicate()
        pattern = re.compile(r'package: name=\'(\S+)\'')
        search = pattern.search(p_communicate[0])
        package_name = search.group(1)
        return package_name

    # 设置so
    def set_so_file(self, zip_apk_path, dir):
        # zip_apk_path = "./dday-collect-debug-old.apk"
        z = zipfile.ZipFile(zip_apk_path, 'r')  # read zip files
        for filename in z.namelist():
            if filename.endswith(".so"):
                soPath = dir + os.sep + "lib" + os.sep + "arm"
                if not os.path.exists(soPath):
                    os.makedirs(soPath)
                soFile = os.path.join(soPath, os.path.basename(filename))
                f = open(soFile, 'wb')
                f.write(z.read(filename))
                f.close()
        z.close()


if __name__ == '__main__':
    # 循环遍历当前目录
    os.system("adb wait-for-device")
    os.system("adb root")
    os.system("adb remount")

    utils = apk_push_utils()
    version = int(utils.get_os_version())
    print version
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if  version < 22:
        print "version < 22 --> use old mode"
        # for list in utils.apk_list:
        #     os.system("adb uninstall "+list)
        #push so
        os.system("adb push ./so /system/lib")

        #push apk
        for file in os.listdir(current_dir):
            if file.endswith('.apk'):
                print file
                apk_realpath = os.path.realpath(file)
                adb_push_apk = "adb push " + apk_realpath + " /system/priv-app/"
                print adb_push_apk
                os.system(adb_push_apk)

        os.system("adb reboot")
        os.system('pause')



    else:
        print "version > 22 --> use new mode"
        os.system("adb shell rm -r /system/priv-app/com.tuyou*")
        for list in utils.apk_list:
            os.system("adb uninstall "+list)

        for file in os.listdir(current_dir):
            if file.endswith('.apk'):
                print file
                packagename = utils.get_packagename(file)
                print packagename
                # 创建包名目录
                package_dir = os.path.join(current_dir, packagename)
                if not os.path.exists(package_dir):
                    os.mkdir(package_dir)
                # 创建lib/arm
                utils.set_so_file(file, package_dir)
                # 移动apk
                shutil.copy(file, os.path.join(package_dir, packagename+".apk"))
                # push
                adb_push = "adb push " + package_dir + " /system/priv-app/"
                print adb_push
                os.system(adb_push)

        os.system("adb reboot")
        os.system('pause')
