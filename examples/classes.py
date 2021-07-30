name='Bobby'
id='123123123'
cmds=[1,2,3,4]
class Bot():
    def __init__(self, name,id,cmds):
        self.name = name
        self.id = id
        self.cmds = cmds

bot=Bot(name,id,cmds)

print(vars(bot))


