# SWReSignApp

重签名.app文件；

## 安装 Install

```

pip install SWReSignApp

```

## Example Modules:

```python

from swresignapp import resign

app_path = "~/Desktop/hello.app"
mobileprovision_path = "~/Desktop/hello.mobileprovision"

# 自动检测mobileprovision文件 sign信息+entitlements信息
resign(app_path, mobileprovision_path)

# is_show_ipa: 重签完成后，使用Finder打开ipa文件所在目录
resign(app_path, mobileprovision_path, is_show_ipa=True)

# 使用是在的sign和entitlements信息重签名
entitlements_path = "~/Desktop/entitlements.plist"
sign = "40位长签名证书的SHA1字符串，例如：ABC5F4F03263A3A29F0BC84910303364E0123456"
resign(app_path, mobileprovision_path, sign=sign, entitlements_path=entitlements_path)


```

## Example CLI:

```shell

swresignapp -h 

usage: App文件重签名 [-h] -m MOBILEPROVISION_PATH [-s SIGN] [-e ENTITLEMENTS_PATH]
                [-q] [--show-ipa]
                app_path

positional arguments:
  app_path              .app文件路径

optional arguments:
  -h, --help            show this help message and exit
  -m MOBILEPROVISION_PATH, --mobileprovision MOBILEPROVISION_PATH
                        mobileprovision文件路径
  -s SIGN, --sign SIGN  (可选)签名证书的 SHA1或者name
  -e ENTITLEMENTS_PATH, --entitlements-path ENTITLEMENTS_PATH
                        (可选)entitlements环境plist文件
  -q, --quiet           是否隐藏print信息
  --show-ipa            是否打开Finder显示最终的ipa文件


```


## 待完成的功能

* 检测.app文件里可执行文件是否已经 加壳/砸过壳;
* 支持App的扩展，例如watch, today等;
