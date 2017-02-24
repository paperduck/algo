
from derived import *

class main():

    def __init__(self):
        self.list_of_instances = []
        self.list_of_instances.append(derived_class())
        self.list_of_instances.append(derived_class())
        self.list_of_instances.append(derived_class())

    def run(self):

        for i in self.list_of_instances:
            i.base_fun_1()

m = main()
m.run()

