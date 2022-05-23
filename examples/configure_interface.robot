*** Settings ***
Documentation       Show Interfaces with TTP parsing example
Library             NetmikoLibrary
Variables           template_cisco.py
Default Tags        examples
Suite Setup         Connect to device


*** Variables ***
# This is a simple example of a list you can configure directly in RobotFramework.
# You can also set your configuration via yaml/jina2 or a variable file or any way you want.
@{config}           interface FastEthernet0/0
...                 ip address 1.1.1.1 255.255.255.252


*** Test Cases ***
Configure Interface
    [Documentation]     Configure the FastEthernet0/0 interface with an ip address.
    Change connection   test-device
    push config         ${config}  

    # Validate the configuration
    ${cli}=             cli       show run interface fa0/0
    Should contain      ${cli}    ip address 1.1.1.1


*** Keywords ***
Connect to Device
    [Documentation]    This is an example connecting to a local GNS3 device using telnet. The example device is a Cisco 7200 router.
    # Open Connection    ${alias}       ${ip}       ${os}               ${username}   ${password}     ${port}
    Open Connection      test-device    127.0.0.1   cisco_ios_telnet    test          password        port=5000