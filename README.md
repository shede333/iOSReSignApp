# iOSReSignApp

> 对'.app/.ipa'文件，进行重签名

## 安装 Install

```

pip install iOSReSignApp

```

## Example Modules:

```python

from iosresignapp import resign

app_path = "~/Desktop/hello.app"
mobileprovision_path = "~/Desktop/hello.mobileprovision"

# 自动检测mobileprovision文件 sign信息+entitlements信息
resign(app_path, mobileprovision_path)

# is_show_ipa: 重签完成后，使用Finder打开ipa文件所在目录
resign(app_path, mobileprovision_path, is_show_ipa=True)

# 到系统路径（~/Library/MobileDevice/Provisioning Profiles），查找"Name"属性为"dev-hello"的最新的mobileprovision文件
resign(app_path, "Name:dev-hello")

# 到系统路径（~/Library/MobileDevice/Provisioning Profiles），查找"UUID"属性为"a4adb1bd-948f-1234-5678-79628e8ce280"的最新的mobileprovision文件
resign(app_path, "UUID:a4adb1bd-948f-1234-5678-79628e8ce280")

# 使用是在的sign和entitlements信息重签名
entitlements_path = "~/Desktop/entitlements.plist"
sign = "40位长签名证书的SHA1字符串，例如：ABC5F4F03263A3A29F0BC84910303364E0123456"
resign(app_path, mobileprovision_path, sign=sign, entitlements_path=entitlements_path)


```

## Example CLI:

```shell

iosresignapp -h 

usage: 对'.app/.ipa'文件，进行重签名 [-h] -m MOBILEPROVISION_PATH [-s SIGN] [-e ENTITLEMENTS_PATH]
                [-q] [-S]
                app_path

positional arguments:
  app_path              '.app/.ipa'文件路径

optional arguments:
  -h, --help            show this help message and exit
  -m MOBILEPROVISION_PATH, --mobileprovision MOBILEPROVISION_PATH
                        mobileprovision文件路径
  -s SIGN, --sign SIGN  (可选)签名证书的 SHA1或者name
  -e ENTITLEMENTS_PATH, --entitlements-path ENTITLEMENTS_PATH
                        (可选)entitlements环境plist文件
  -q, --quiet           是否隐藏print信息
  -S, --show-ipa            是否打开Finder显示最终的ipa文件


```


## 待完成的功能

* 检测.app文件里可执行文件是否已经 加壳/砸过壳;
* 优化codesign命令输出的log信息;
* ~~支持App的扩展，例如watch, today等~~;
