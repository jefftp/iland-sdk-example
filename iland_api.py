import iland, json, argparse, time

def init_api_client():
    with open('./creds.json', 'r') as f:
        creds = json.load(f)
        return Client(creds['client_id'],creds['client_secret'],creds['username'],creds['password'])

class Client:
    def __init__(self,client_id,client_secret,username,password):
        self.username = username
        self.api = iland.Api(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password)

    def get_inventory(self):
        return self.api.get('/users/{}/inventory'.format(self.username))

    def get_locations(self):
        locations = []
        api_dict = self.get_inventory()
        for item in api_dict:
            locations.append(Location(self,item["location_id"]))
        return locations

    def get_virtual_machine(self,virtual_machine_uuid):
        api_dict = self.api.get('/vm/{}'.format(virtual_machine_uuid))
        return VirtualMachine(self,api_dict)

class Location:
    def __init__(self,client,location_id):
        self.client = client
        self.id = location_id

    def get_orgs(self):
        return self.client.api.get('/location/{}/orgs'.format(self.id))

    def get_vdcs(self):
        return self.client.api.get('/location/{}/vdcs'.format(self.id))

    def get_vapps(self):
        return self.client.api.get('/location/{}/vapps'.format(self.id))

    def get_virtual_machines(self):
        return self.client.api.get('/location/{}/vms'.format(self.id))

    def get_task(self,task_uuid):
        api_dict = self.client.api.get('/task/{}/{}'.format(self.id,task_uuid))
        return Task(self,api_dict)

class VirtualMachine:
    def __init__(self,client,api_dict):
        self.client = client
        self.name = api_dict['name']
        self.uuid = api_dict['uuid']

    def power_on(self):
        api_dict = self.client.api.post('/vm/{}/poweron'.format(self.uuid))
        return Task(self.client,api_dict)

    def shutdown(self):
        api_dict = self.client.api.post('/vm/{}/shutdown'.format(self.uuid))
        return Task(self.client,api_dict)

    def power_off(self):
        api_dict = self.client.api.post('/vm/{}/poweroff'.format(self.uuid))
        return Task(self.client,api_dict)

    def reboot(self):
        api_dict = self.client.api.post('/vm/{}/reboot'.format(self.uuid))
        return Task(self.client,api_dict)

class Task:
    def __init__(self,client,api_dict):
        self.client = client
        self.uuid = api_dict['uuid']
        self.entity_uuid = api_dict['entity_uuid']
        self.status = api_dict['status']
        self.progress = api_dict['progress']
        self.active = api_dict['active']
        self.synchronized = api_dict['synchronized']
        self.message = api_dict['message']
        self.task_type = api_dict['task_type']
        self.operation = api_dict['operation']
        self.operation_description = api_dict['operation_description']
        self.location_id = api_dict['location_id']
        self.org_uuid = api_dict['org_uuid']
        self.task_id = api_dict['task_id']
        self.username = api_dict['username']
        self.initiation_time = api_dict['initiation_time']
        self.start_time = api_dict['start_time']
        self.end_time = api_dict['end_time']

    def refresh(self):
        location = Location(self.client,self.location_id)
        return location.get_task(self.uuid)

    def watch(self):
        while True:
            task = self.refresh()
            if task.active == False:
                if task.status == 'success':
                    print('{} - {}'.format(task.operation,task.status))
                else:
                    print('{} - {} ({})'.format(task.operation,task.status,task.message))                  
                return
            else:
                print('{} - {}'.format(task.operation,task.status))
            time.sleep(5)

def handle_input(client,args):
    if args.action == 'list':
        if args.object == 'location':
            for location in client.get_locations():
                print(location.id)
        if args.object == 'org':
            for location in client.get_locations():
                for org in location.get_orgs():                
                    print('{},{}'.format(org['name'],org['uuid']))
        if args.object == 'vdc':
            for location in client.get_locations():
                for vdc in location.get_vdcs():
                    print('{},{}'.format(vdc['name'],vdc['uuid']))
        if args.object == 'vapp':
            for location in client.get_locations():
                for vapp in location.get_vapps():
                    print('{},{}'.format(vapp['name'],vapp['uuid']))
        if args.object == 'vm':
            for location in client.get_locations():
                for vm in location.get_virtual_machines():
                    print('{},{}'.format(vm['name'],vm['uuid']))
    if args.action == 'power_on':
        if args.object == 'vm':
            vm = client.get_virtual_machine(args.uuid)
            task = vm.power_on()
            task.watch()
    if args.action == 'shutdown':
        if args.object == 'vm':
            vm = client.get_virtual_machine(args.uuid)
            task = vm.shutdown()
            task.watch()
    if args.action == 'power_off':
        if args.object == 'vm':
            vm = client.get_virtual_machine(args.uuid)
            task = vm.power_off()
            task.watch()
    if args.action == 'reboot':
        if args.object == 'vm':
            vm = client.get_virtual_machine(args.uuid)
            task = vm.reboot()
            task.watch()


if __name__ == '__main__':
    client = init_api_client()

    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='available actions', choices=['list','power_on','shutdown','power_off','reboot'], default=None)
    parser.add_argument('object', help='target object type', choices=['location','org','vdc','vapp','vm'], default=None)
    parser.add_argument('--uuid', help='target object uuid', default=None, required=False)
    args = parser.parse_args()

    handle_input(client,args)










