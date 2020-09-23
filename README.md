# iland sdk Example

Based on the original work of Jerry Perry at iland.

I updated this python script to support version 1 of the iland Cloud API.
The script is an extremely basic CLI interface to the iland Cloud API. It
is intended to serve as an example of how you could use the iland Cloud API
in your own scripts. You could use this to handle basic power operations
for your VMs.

## Usage

```bash
python iland_api.py --uuid UUID [action] [object]
```

Available Actions:

- list - Queries the inventory and returns a list of objects
  - Objects: company, location, org, vdc, vapp, vm
- power_on - Power on the object
  - Objects: vm
- power_off - Power off the object
  - Objects: vm
- reboot - Power off and then power on the object
  - Objects: vm
- shutdown - Gracefully shutdown the object
  - Objects: vm
- suspend - Suspend a VM, saving state and powering off.
  - Objects: vm

## Requirements

You must install the iland-sdk (https://github.com/ilanddev/python-sdk):

```bash
pip install iland-sdk
```

You must supply credentials in creds.json. An example .json file is provided
in example.creds.json.

## Examples

List all the VMs and their UUIDs:

```bash
python iland_api.py list vm
```

Shutdown a VM:

```bash
python iland_api.py --uuid dal42.ilandcloud.com:urn:vcloud:vm:46fe90cf-6199-400a-a23e-ff44e0126a8c shutdown vm
```

Power down a VM:

```bash
python iland_api.py --uuid dal42.ilandcloud.com:urn:vcloud:vm:46fe90cf-6199-400a-a23e-ff44e0126a8c power_off vm
```

Power on a VM:

```bash
python iland_api.py --uuid dal42.ilandcloud.com:urn:vcloud:vm:46fe90cf-6199-400a-a23e-ff44e0126a8c power_on vm
```
