# iOSReSignApp

> 对'.app/.ipa'文件，进行重签名；  
> 注意：仅支持 Python3；

## 安装 Install

```

pip3 install iOSReSignApp

```

## CLI 使用说明

```bash

iosresignapp -h 

```

## Python Modules 使用说明

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

usage: 对'.app/.ipa'文件，进行重签名 [-h] -m MOBILEPROVISION_INFO [-s SIGN]
                            [-e ENTITLEMENTS_PATH]
                            [--re-suffix-name RE_SUFFIX_NAME]
                            [-o OUTPUT_IPA_PATH] [-q] [-S]
                            app_path

positional arguments:
  app_path              '.app/.ipa'文件路径

optional arguments:
  -h, --help            show this help message and exit
  -m MOBILEPROVISION_INFO, --mobileprovision MOBILEPROVISION_INFO
                        mobileprovision文件路径,或者Name属性,或者UUID属性
  -s SIGN, --sign SIGN  (可选)签名证书的 SHA1或者name
  -e ENTITLEMENTS_PATH, --entitlements-path ENTITLEMENTS_PATH
                        (可选)entitlements环境plist文件
  --re-suffix-name RE_SUFFIX_NAME
                        (可选)重签名后的文件名后缀，如果设置了'--output-ipa-
                        path'，此选项无效，默认为'resign'
  -o OUTPUT_IPA_PATH, --output-ipa-path OUTPUT_IPA_PATH
                        (可选)ipa文件输出路径，不传此值则输出到.app同级目录下
  -q, --quiet           是否隐藏print信息
  -S, --show-ipa        是否打开Finder显示最终的ipa文件


```

## 注意

重签名时，需要使用 Keychain（钥匙串）里的证书，这时候就有2个点要注意：  
1.证书所在的钥匙串（一般为`登录`钥匙串）必须要被解锁(也可以通过security来解锁)；  
2.证书首次被使用时，会有`授权弹框`提示，这是需要手动确认（可以通过security导入证书到钥匙串，解决授权弹框问题）；  


## 待完成的功能

* 检测.app文件里可执行文件是否已经 加壳/砸过壳;
* 优化codesign命令输出的log信息;
* ~~支持App的扩展，例如watch, today等~~;
* ~~支持修改更多Info.plist的参数~~;
* 支持换图标icon；
* 支持在图标上版本号等额外信息；
* 屏蔽：读取info.plist信息时的错误输出；
