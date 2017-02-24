class base_class():

    def __init__(self):
        self.base_list = []

    def base_fun_1(self):
        self.base_fun_2()

    def base_fun_2(self):
        raise NotImplementedError()
