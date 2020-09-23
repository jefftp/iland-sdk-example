import iland, json, argparse, time, sys

def init_api_client():
    with open('./creds.json', 'r') as f:
        creds = json.load(f)
        return Client(creds['client_id'], creds['client_secret'], creds['username'], creds['password'])

class Client:
    def __init__(self, client_id, client_secret, username, password):
        self.username = username
        self.api = iland.Api(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password)

    def get_entity(self, entity):
        items = []
        inventory = self.api.get('/users/{}/inventory'.format(self.username))
        
        for company in inventory['inventory']:
            for entity in company['entities'][entity]:
                items.append(entity)
        return items

    def get_vm(self, uuid):
        vm_data = self.api.get('/vms/{}'.format(uuid))
        return VirtualMachine(self, vm_data)

class VirtualMachine:
    def __init__(self, client, vm_data):
        self.client = client
        self.uuid = vm_data['uuid']
        self.status = vm_data['status']

    def power_on(self):
        task_data = self.client.api.post('/vms/{}/actions/poweron'.format(self.uuid))
        return Task(self.client, task_data)

    def shutdown(self):
        task_data = self.client.api.post('/vms/{}/actions/shutdown'.format(self.uuid))
        return Task(self.client, task_data)

    def power_off(self):
        task_data = self.client.api.post('/vms/{}/actions/poweroff'.format(self.uuid))
        return Task(self.client, task_data)

    def reboot(self):
        task_data = self.client.api.post('/vms/{}/actions/reboot'.format(self.uuid))
        return Task(self.client, task_data)

    def suspend(self):
        task_data = self.client.api.post('/vms/{}/actions/suspend'.format(self.uuid))
        return Task(self.client, task_data)

class Task:
    def __init__(self, client, task_data):
        self.client = client
        self.uuid = task_data['uuid']
        self.status = task_data['status']
        self.active = task_data['active']
        self.message = task_data['message']
        self.operation = task_data['operation']

    def refresh(self):
        task = self.client.api.get('/tasks/{}'.format(self.uuid))
        self.status = task['status']
        self.active = task['active']
        self.message = task['message']
        self.operation = task['operation']
        return

    def watch(self):
        while True:
            self.refresh()
            if self.active == False:
                if self.status == 'success':
                    print('{} - {}'.format(self.operation, self.status))
                else:
                    print('{} - {} ({})'.format(self.operation, self.status, self.message))                  
                return
            else:
                print('{} - {}'.format(self.operation, self.status))
            time.sleep(5)

def handle_input(client,args):
    if args.action == 'list':
        if args.object == 'company':
            for company in client.get_entity('COMPANY'):
                print("{}, {}".format(company["name"], company["uuid"]))
        if args.object == 'location':
            for location in client.get_entity('IAAS_LOCATION'):
                print("{}".format(location["name"]))
        if args.object == 'org':
            for org in client.get_entity('IAAS_ORGANIZATION'):
                print("{}, {}".format(org["name"], org["uuid"]))
        if args.object == 'vdc':
            for vdc in client.get_entity('IAAS_VDC'):
                print("{}, {}".format(vdc["name"], vdc["uuid"]))
        if args.object == 'vapp':
            for vapp in client.get_entity('IAAS_VAPP'):
                print("{}, {}".format(vapp["name"], vapp["uuid"]))
        if args.object == 'vm':
            for vm in client.get_entity('IAAS_VM'):
                print("{}, {}".format(vm["name"], vm["uuid"]))

    # The following blocks of elifs should be refactored into something more
    # elegant and compact.

    elif args.action == 'power_on':
        if args.object == 'vm':
            if args.uuid:
                vm = client.get_vm(args.uuid)
                task = vm.power_on()
                task.watch()
            else:
                sys.exit('Error: UUID required to power on a VM.')
        else:
            sys.exit('Error: Powering on {} is not supported.'.format(args.object))

    elif args.action == 'shutdown':
        if args.object == 'vm':
            if args.uuid:
                vm = client.get_vm(args.uuid)
                task = vm.shutdown()
                task.watch()
            else:
                sys.exit('Error: UUID required to shutdown a VM.')
        else:
            sys.exit('Error: Shutting down {} is not supported.'.format(args.object))

    elif args.action == 'power_off':
        if args.object == 'vm':
            if args.uuid:
                vm = client.get_vm(args.uuid)
                task = vm.power_off()
                task.watch()
            else:
                sys.exit('Error: UUID required to power off a VM.')
        else:
            sys.exit('Error: Powering off {} is not supported.'.format(args.object))

    elif args.action == 'reboot':
        if args.object == 'vm':
            if args.uuid:
                vm = client.get_vm(args.uuid)
                task = vm.reboot()
                task.watch()
            else:
                sys.exit('Error: UUID required to reboot a VM.')
        else:
            sys.exit('Error: Rebooting {} is not supported.'.format(args.object))

    elif args.action == 'suspend':
        if args.object == 'vm':
            if args.uuid:
                vm = client.get_vm(args.uuid)
                task = vm.suspend()
                task.watch()
            else:
                sys.exit('Error: UUID required to suspend a VM.')
        else:
            sys.exit('Error: Suspending {} is not supported.'.format(args.object))

if __name__ == '__main__':
    client = init_api_client()

    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='available actions', choices=['list','power_on','shutdown','power_off','reboot', 'suspend'], default=None)
    parser.add_argument('object', help='target object type', choices=['company', 'location','org','vdc','vapp','vm'], default=None)
    parser.add_argument('--uuid', help='target object uuid', default=None, required=False)
    args = parser.parse_args()

    handle_input(client,args)
