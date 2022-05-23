*** Settings ***
Documentation       Show Interfaces with TTP parsing example
Library             NetmikoLibrary
Variables           template_cisco.py
Default Tags        examples
Suite Setup         Connect to device


*** Test Cases ***
Show Interfaces
    [Documentation]     Show interfaces
    # If connecting to multiple devices you can specify the device.
    # By default, the last connected device will be used.
    # Change connection   test-device
    ${cli}=             cli ttp      show interfaces    ${interface_template}
    #[
    #  {'interface': 'FastEthernet0/0', 'admin_state': 'down', 'protocol_state': 'down'}, 
    #  {'interface': 'GigabitEthernet0/1', 'admin_state': 'down', 'protocol_state': 'down'},
    #  ...
    #]
    Should be equal     ${cli[0]['interface']}    FastEthernet0/0
    Should be equal     ${cli[1]['interface']}    GigabitEthernet0/1



*** Keywords ***
Connect to Device
    [Documentation]    This is an example connecting to a local GNS3 device using telnet. The example device is a Cisco 7200 router.
    # Open Connection    ${alias}       ${ip}       ${os}               ${username}   ${password}     ${port}
    Open Connection      test-device    127.0.0.1   cisco_ios_telnet    test          password        port=5000