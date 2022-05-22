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
    Should contain      ${cli}    <some string>


*** Keywords ***
Connect to Device
    # Open Connection    ${alias}       ${ip}       ${os}       ${username}   ${password}
    Open Connection      test-device    127.0.0.1   cisco-xr    username      password