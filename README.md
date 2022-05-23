# RobotFramework Netmiko Library

A Netmiko library wrapper for use with RobotFramework.

# Installation

Install using your normal pip/pipenv installation method.

```bash
pip install robotframework-netmiko
```

# Examples


## RobotFramework + Netmiko

```robotframework

# show_version.robot

*** Settings ***
Documentation       Show Version Example
Library             NetmikoLibrary
Default Tags        examples
Suite Setup         Connect to device


*** Test Cases ***
Show Version
    [Documentation]     Show version example
    # If connecting to multiple devices you can specify the device.
    # Change connection   test-device
    ${cli}=             cli       show version
    Should contain      ${cli}    Cisco IOS Software


*** Keywords ***
Connect to Device
    [Documentation]    This is an example connecting to a local GNS3 device using telnet. The example device is a Cisco 7200 router.
    # Open Connection    ${alias}       ${ip}       ${os}               ${username}   ${password}     ${port}
    Open Connection      test-device    127.0.0.1   cisco_ios_telnet    test          password        port=5000
```

## Example Cli Output

```bash
#> robot --maxassignlength 5000 -s show_version .
==============================================================================
Robot-Netmiko-Library
==============================================================================
Robot-Netmiko-Library.Examples
==============================================================================
Robot-Netmiko-Library.Examples.Show Version :: Show Version Example
==============================================================================
Show Version :: Show version example                                  | PASS |
------------------------------------------------------------------------------
Robot-Netmiko-Library.Examples.Show Version :: Show Version Example   | PASS |
1 test, 1 passed, 0 failed
==============================================================================
Robot-Netmiko-Library.Examples                                        | PASS |
1 test, 1 passed, 0 failed
==============================================================================
Robot-Netmiko-Library                                                 | PASS |
1 test, 1 passed, 0 failed
==============================================================================
Output:  D:\Projects\robot-netmiko-library\output.xml
Log:     D:\Projects\robot-netmiko-library\log.html
Report:  D:\Projects\robot-netmiko-library\report.html
```

## Other examples

https://github.com/mitchmahan/robotframework-netmiko/tree/main/examples