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