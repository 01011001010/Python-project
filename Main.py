# Semestrálny projekt predmetu Programovanie1
# Hra Hex
# Autor kódu a všetkých grafických súborov: Katarína Osvaldová 1DAV1


import tkinter
from math import dist
from time import time
from PIL import Image, ImageTk
import json
from random import choice, randrange


class Animated:
    def next(self):
        if self.pics[self.num] is None:
            self.can.delete(self.id)
        else:
            self.can.itemconfig(self.id, image=self.pics[self.num])
        self.num += 1
        if self.num < self.atmost:
            self.can.after(self.aniSpeed, self.next)


class Blast(Animated):
    def __init__(self, pics, x, y):
        self.pics = pics + [None]
        self.id = self.can.create_image(randrange(100, x-100), randrange(100, y-100), image=None)
        self.atmost = 10
        self.num = 0
        self.aniSpeed = 150
        self.can.after(randrange(100, 4000), self.next)


class Bee(Animated):
    def __init__(self, x, y, pic):
        self.x, self.y = x, y
        self.pic = pic
        self.live = True
        self.can.after(randrange(200, 500), self.birth)

    def birth(self):
        self.can.after(randrange(1000, 2000), self.die)
        self.id = self.can.create_image(randrange(self.x), randrange(self.y), image=self.pic)
        self.can.after(150, self.wander)

    def wander(self):
        self.can.move(self.id, randrange(-20, 21), randrange(-20, 21))
        self.can.after(70, self.wander)

    def die(self):
        self.can.delete(self.id)
        if self.live:
            self.can.after(randrange(1500, 6000), self.birth)

    def flyAway(self):
        self.live = False
        self.can.delete(self.id)


class Piece(Animated):
    def __init__(self, x, y, pics):
        self.pics = pics
        self.id = self.can.create_image(x, y, image=pics[0])

    def shatter(self):
        self.atmost = 21
        self.num = 14
        self.aniSpeed = 50
        self.can.after(60, self.next)

    def pour(self):
        self.atmost = 14
        self.num = 1
        self.aniSpeed = 120
        self.can.after(60, self.next)

    def scoot(self, coor):
        self.can.coords(self.id, coor)


class Filling(Animated):
    def __init__(self, x, y, pics, grid):
        self.pics = pics
        self.id = self.can.create_image(x, y, image=None)
        self.can.tag_lower(self.id, grid)
        self.atmost = 4
        self.num = 0
        self.aniSpeed = 150
        self.can.after(960, self.next)

    def glow(self):
        self.can.itemconfig(self.id, image=self.pics[4])

    def getLost(self):
        self.can.delete(self.id)


class Program:
    def __init__(self):
        try:
            with open('leaderboard.txt'):
                pass
        except IOError:
            with open('leaderboard.txt', 'w') as file:
                json.dump({}, file, indent=2)
        self.texts = {'en': {'start': 'Start Game', 'rules': 'Rules', 'leader': 'Leaderboard', 'qstart': 'Quickstart', 'lname': 'Player Name', 'lwins': 'Wins', 'lratio': 'W/L', 'ready': 'Ready',
                             'name': 'Name', 'back': 'Back', 'win': 'Congratlations ', 'player': 'Player', 'back2menu': 'Main Menu', 'again': 'Play Again'},
                      'sk': {'start': 'Začať hru', 'rules': 'Pravidlá', 'leader': 'Rebríček', 'qstart': 'Rýchloštart', 'lname': 'Meno hráča', 'lwins': 'Výhry', 'lratio': 'V/P', 'ready': 'Pripravený',
                             'name': 'Meno', 'back': 'Naspäť', 'win': 'Gratulujeme, ', 'player': 'Hráč', 'back2menu': 'Hlavné menu', 'again': 'Hrať znovu'}
                      }
        with open('rulesEN.txt', 'r') as file:
            self.texts['en']['rulesfull'] = file.read().strip().replace('\n', ' ')
        with open('rulesSK.txt', 'r') as file:
            self.texts['sk']['rulesfull'] = file.read().strip().replace('\n', ' ')
        self.tk = tkinter.Tk()
        self.tk.title('Hex Bee Upon You')
        self.tk.state('zoomed')
        self.can = Animated.can = tkinter.Canvas(self.tk)
        self.can.pack(fill=tkinter.BOTH, expand=True)
        self.can.update()
        self.width = self.can.winfo_width()
        self.height = self.can.winfo_height()
        self.gridPic = tkinter.PhotoImage(file='Graphics/grid11.png')
        self.backgroundPic = tkinter.PhotoImage(file='Graphics/mainbg.png')
        self.varGraphics = {'sk': tkinter.PhotoImage(file='Graphics/skflag.png'),
                            'en': tkinter.PhotoImage(file='Graphics/enflag.png'),
                            'deact': tkinter.PhotoImage(file='Graphics/deactivate.png'),
                            'button': tkinter.PhotoImage(file='Graphics/buttonbg.png'),
                            'buttonlong': tkinter.PhotoImage(file='Graphics/buttonlong.png'),
                            'Richie': tkinter.PhotoImage(file='Graphics/Richie.png'),
                            'sbutton': ImageTk.PhotoImage(Image.open('Graphics/buttonbg.png').resize((300, 114))),
                            'fws': [tkinter.PhotoImage(file=f'Graphics/firews{n}.png') for n in '987654310'],
                            'fwl': [tkinter.PhotoImage(file=f'Graphics/firewl{n}.png') for n in '987654310'],
                            'colourrects': {col: [tkinter.PhotoImage(file=f'Graphics/{col}.png'), tkinter.PhotoImage(file=f'Graphics/un{col}.png'), tkinter.PhotoImage(file=f'Graphics/un{col}un.png')] for col in ('yellow', 'orange', 'red', 'mag', 'purple', 'blue', 'turq', 'green', 'grey')}}
        self.honey = {}
        self.namesOnCan = {}
        self.colourPicker = {}
        self.filled = {0: {}, 1: {}}
        self.colours = {0: 'yellow', 1: 'orange'}
        self.names = {0: 'Player1', 1: 'Player2'}
        self.forDeletion = []
        self.coloursRects = {}
        self.gridMidpoints = [(start+77*i, 175+67*j) for i in range(11) for j, start in enumerate([768-i for i in [0, 39, 77, 116, 154, 193, 231, 270, 308, 347, 385]])]
        self.clickAreas = {}
        self.can.create_image(self.width/2, self.height/2, image=self.backgroundPic, anchor='center')
        self.languageScreen()
        tkinter.mainloop()

    def applyColour(self):
        self.pics = {0: [tkinter.PhotoImage(file=f'Graphics/{n}jar{self.colours[0]}.png') for n in '05432111123450']
                     + [tkinter.PhotoImage(file=f'Graphics/{n}breakjar{self.colours[0]}.png') for n in '1234567'],
                     1: [ImageTk.PhotoImage(Image.open(f'Graphics/{n}jar{self.colours[1]}.png').transpose(Image.FLIP_LEFT_RIGHT)) for n in '05432111123450']
                     + [ImageTk.PhotoImage(Image.open(f'Graphics/{n}breakjar{self.colours[1]}.png').transpose(Image.FLIP_LEFT_RIGHT)) for n in '1234567'],
                     '0honey': [tkinter.PhotoImage(file=f'Graphics/{n}fill{self.colours[0]}.png') for n in '12345'],
                     '1honey': [tkinter.PhotoImage(file=f'Graphics/{n}fill{self.colours[1]}.png') for n in '12345'],
                     '0flair': [tkinter.PhotoImage(file=f'Graphics/{self.colours[0]}top.png'), tkinter.PhotoImage(file=f'Graphics/big{self.colours[0]}.png')],
                     '1flair': [tkinter.PhotoImage(file=f'Graphics/{self.colours[1]}side.png'), tkinter.PhotoImage(file=f'Graphics/big{self.colours[1]}.png')]}

    def languageScreen(self):
        self.forDeletion.append(self.can.create_image(self.width/2-400, self.height/2+100, image=self.varGraphics['sk'], anchor='center'))
        self.forDeletion.append(self.can.create_image(self.width/2+400, self.height/2+100, image=self.varGraphics['en'], anchor='center'))
        x, yy, xx, y = map(int, (self.width/2-700, self.height/2+400, self.width/2-100, self.height/2-200))
        self.forDeletion.append(self.can.create_rectangle(x, y, xx, yy, outline='#ffffff', width=15))
        self.clickAreas['langSK'] = (range(x, xx), range(y, yy))
        xx, yy, x, y = map(int, (self.width/2+700, self.height/2+400, self.width/2+100, self.height/2-200))
        self.forDeletion.append(self.can.create_rectangle(x, y, xx, yy, outline='#ffffff', width=15))
        self.clickAreas['langEN'] = (range(x, xx), range(y, yy))
        self.can.bind('<ButtonPress-1>', self.clickable)

    def mainMenu(self):
        self.names = {0: self.texts[self.language]['player']+'1', 1: self.texts[self.language]['player']+'2'}
        self.colours = {0: 'yellow', 1: 'orange'}
        for i in self.forDeletion:
            self.can.delete(i)
        self.Richie = Bee(self.width, self.height, self.varGraphics['Richie'])
        h = 115
        w = 310
        fontsize = 67
        x, y = map(int, (self.width/2-400, self.height/2-80))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['button'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['start'], font=('Courier', fontsize)))
        self.clickAreas['customization'] = (range(x-w, x+w), range(y-h, y+h))
        x, y = map(int, (self.width/2+400, self.height/2-80))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['button'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['qstart'], font=('Courier', fontsize)))
        self.clickAreas['quickstart'] = (range(x-w, x+w), range(y-h, y+h))
        x, y = map(int, (self.width/2-400, self.height/2+180))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['button'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['leader'], font=('Courier', fontsize)))
        self.clickAreas['leaderboard'] = (range(x-w, x+w), range(y-h, y+h))
        x, y = map(int, (self.width/2+400, self.height/2+180))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['button'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['rules'], font=('Courier', fontsize)))
        self.clickAreas['rules'] = (range(x-w, x+w), range(y-h, y+h))
        self.can.bind('<ButtonPress-1>', self.clickable)

    def rulesScreen(self):
        self.Richie.flyAway()
        for i in self.forDeletion:
            self.can.delete(i)
        self.forDeletion.append(self.can.create_text(self.width/2, self.height/2-200, text=self.texts[self.language]['rulesfull'], font=('Courier', 30), anchor='n', justify='center', width=self.width-400))
        x, y = map(int, (self.width/2+700, self.height/2-400))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['sbutton'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['back'], font=('Courier', 45), anchor='center'))
        self.clickAreas['menu'] = (range(x-150, x+150), range(y-57, y+57))
        self.can.bind('<ButtonPress-1>', self.clickable)

    def clickable(self, event):
        found = False
        for button, area in self.clickAreas.items():
            if event.x in area[0] and event.y in area[1]:
                found = True
                self.can.unbind('<ButtonPress-1>')
                break
        if not found:
            pass
        elif button == 'langEN':
            self.language = 'en'
            del self.clickAreas['langEN'], self.clickAreas['langSK']
            self.mainMenu()
        elif button == 'langSK':
            self.language = 'sk'
            del self.clickAreas['langEN'], self.clickAreas['langSK']
            self.mainMenu()
        elif button == 'customization':
            del self.clickAreas['customization'], self.clickAreas['quickstart'], self.clickAreas['leaderboard'], self.clickAreas['rules']
            self.customizationScreen()
        elif button == 'quickstart':
            if 'customization' in self.clickAreas:
                del self.clickAreas['customization'], self.clickAreas['quickstart'], self.clickAreas['leaderboard'], self.clickAreas['rules']
            else:
                del self.clickAreas['menu'], self.clickAreas['quickstart']
            self.startGame()
        elif button == 'leaderboard':
            del self.clickAreas['customization'], self.clickAreas['quickstart'], self.clickAreas['leaderboard'], self.clickAreas['rules']
            self.leaderboardScreen()
        elif button == 'rules':
            del self.clickAreas['customization'], self.clickAreas['quickstart'], self.clickAreas['leaderboard'], self.clickAreas['rules']
            self.rulesScreen()
        elif button == 'menu':
            del self.clickAreas['menu'],
            if 'quickstart' in self.clickAreas:
                del self.clickAreas['quickstart']
            self.mainMenu()
        elif button[0] == 'p':
            if button[2:] == 'name':
                self.nameChanger = int(button[1])
                self.can.bind_all('<Key>', self.typeName)
                self.can.bind('<ButtonPress-1>', self.clickable)
                self.can.itemconfig(self.namesOnCan[self.nameChanger], text=self.names[self.nameChanger]+'|')
                other = (self.nameChanger + 1) % 2
                self.can.itemconfig(self.namesOnCan[other], text=self.names[other] or self.texts[self.language]['name'])
            elif button[2:] == 'ready':
                self.can.bind('<ButtonPress-1>', self.clickable)
                for i in self.colourPicker:
                    if i in self.clickAreas and button[1] in i:
                        del self.clickAreas[i]
                del self.clickAreas[f'p{button[1]}ready'], self.clickAreas[f'p{button[1]}name']
                if self.ready:
                    del self.colourPicker
                    self.can.unbind_all('<Key>')
                    self.startGame()
                else:
                    self.forDeletion.append(self.can.create_image(self.width/2, self.height/2, image=self.varGraphics['deact'], anchor='w' if button[1] == '1' else 'e'))
                    self.ready = True
            else:
                self.can.itemconfig(self.coloursRects[button[1]+self.colours[int(button[1])]], image=self.varGraphics['colourrects'][self.colours[int(button[1])]][1])
                self.can.itemconfig(self.coloursRects[button[1].replace('1', '*').replace('0', '1').replace('*', '0')+self.colours[int(button[1])]], image=self.varGraphics['colourrects'][self.colours[int(button[1])]][1])
                if not self.ready:
                    self.clickAreas[button[:2].replace('1', '*').replace('0', '1').replace('*', '0')+self.colours[int(button[1])]] = self.colourPicker[button[:2].replace('1', '*').replace('0', '1').replace('*', '0')+self.colours[int(button[1])]]
                self.colours[int(button[1])] = button[2:]
                self.can.itemconfig(self.coloursRects[button[1:]], image=self.varGraphics['colourrects'][button[2:]][0])
                self.can.itemconfig(self.coloursRects[button[1:].replace('1', '*').replace('0', '1').replace('*', '0')], image=self.varGraphics['colourrects'][button[2:]][2])
                if not self.ready:
                    del self.clickAreas[button.replace('1', '*').replace('0', '1').replace('*', '0')]
                self.can.bind('<ButtonPress-1>', self.clickable)

    def typeName(self, event):
        if event.keysym == 'BackSpace':
            self.names[self.nameChanger] = self.names[self.nameChanger][:-1]
            self.can.itemconfig(self.namesOnCan[self.nameChanger], text=self.names[self.nameChanger] + '|')
        elif event.char in 'qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM' and len(self.names[self.nameChanger]) < 11:
            self.names[self.nameChanger] += event.char
            self.can.itemconfig(self.namesOnCan[self.nameChanger], text=self.names[self.nameChanger] + '|')

    def customizationScreen(self):
        self.Richie.flyAway()
        self.ready = False
        for i in self.forDeletion:
            self.can.delete(i)
        self.names = {0: '', 1: ''}
        nameSize = 45
        w = 272
        h = 50
        x, y = map(int, (self.width / 2 + 450, self.height / 2 - 400))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['buttonlong'], anchor='center'))
        self.namesOnCan[1] = self.can.create_text(x, y, text=self.texts[self.language]['name'], font=('Courier', nameSize), anchor='center')
        self.forDeletion.append(self.namesOnCan[1])
        self.clickAreas['p1name'] = (range(x - w, x + w), range(y - h, y + h))
        x, y = map(int, (self.width / 2 - 450, self.height / 2 - 400))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['buttonlong'], anchor='center'))
        self.namesOnCan[0] = self.can.create_text(x, y, text=self.texts[self.language]['name'], font=('Courier', nameSize), anchor='center')
        self.forDeletion.append(self.namesOnCan[0])
        self.clickAreas['p0name'] = (range(x - w, x + w), range(y - h, y + h))
        w = h = 94
        for i, col in enumerate(('yellow', 'orange', 'red', 'mag', 'purple', 'blue', 'turq', 'green', 'grey')):
            x, y = map(int, (self.width / 2 - 680 + ((i % 3) * 230), self.height / 2 - 220 + ((i // 3) * 230)))
            self.coloursRects['0' + col] = self.can.create_image(x, y, image=self.varGraphics['colourrects'][col][1], anchor='center')
            self.forDeletion.append(self.coloursRects['0' + col])
            self.clickAreas['p0' + col] = self.colourPicker['p0'+col] = (range(x - w, x + w), range(y - h, y + h))

            x, y = map(int, (self.width / 2 + 220 + ((i % 3) * 230), self.height / 2 - 220 + ((i // 3) * 230)))
            self.coloursRects['1' + col] = self.can.create_image(x, y, image=self.varGraphics['colourrects'][col][1], anchor='center')
            self.forDeletion.append(self.coloursRects['1' + col])
            self.clickAreas['p1' + col] = self.colourPicker['p1' + col] = (range(x - w, x + w), range(y - h, y + h))
        self.can.itemconfig(self.coloursRects['0yellow'], image=self.varGraphics['colourrects']['yellow'][0])
        self.can.itemconfig(self.coloursRects['1orange'], image=self.varGraphics['colourrects']['orange'][0])
        self.can.itemconfig(self.coloursRects['0orange'], image=self.varGraphics['colourrects']['orange'][2])
        self.can.itemconfig(self.coloursRects['1yellow'], image=self.varGraphics['colourrects']['yellow'][2])
        del self.clickAreas['p0orange'], self.clickAreas['p1yellow']
        w = 272
        h = 50
        x, y = map(int, (self.width / 2 - 450, self.height / 2 + 420))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['buttonlong'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['ready'], font=('Courier', nameSize), anchor='center'))
        self.clickAreas['p0ready'] = (range(x - w, x + w), range(y - h, y + h))
        x, y = map(int, (self.width / 2 + 450, self.height / 2 + 420))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['buttonlong'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['ready'], font=('Courier', nameSize), anchor='center'))
        self.clickAreas['p1ready'] = (range(x - w, x + w), range(y - h, y + h))
        self.can.bind('<ButtonPress-1>', self.clickable)

    def leaderboardScreen(self):
        self.Richie.flyAway()
        for i in self.forDeletion:
            self.can.delete(i)
        fontsize = 35
        x, y = map(int, (self.width / 2 + 700, self.height / 2 - 400))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['sbutton'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['back'], font=('Courier', 45), anchor='center'))
        self.clickAreas['menu'] = (range(x - 150, x + 150), range(y - 57, y + 57))
        self.can.bind('<ButtonPress-1>', self.clickable)
        data = list(map(lambda info: ((info[1]['won'], info[1]['lost']), info[0]), list(json.load(open('leaderboard.txt')).items())))
        data.sort(reverse=True)
        data = data[:20]
        self.forDeletion.append(self.can.create_text(self.width / 2 - 840, self.height / 2 - 200, anchor='w', text=self.texts[self.language]['lname'], font=('Courier', fontsize, 'bold')))
        self.forDeletion.append(self.can.create_text(self.width / 2 - 300, self.height / 2 - 200, anchor='e', text=self.texts[self.language]['lwins'], font=('Courier', fontsize, 'bold')))
        self.forDeletion.append(self.can.create_text(self.width / 2 - 100, self.height / 2 - 200, anchor='e', text=self.texts[self.language]['lratio'], font=('Courier', fontsize, 'bold')))
        self.forDeletion.append(self.can.create_text(self.width / 2 - 840 + 910, self.height / 2 - 200, anchor='w', text=self.texts[self.language]['lname'], font=('Courier', fontsize, 'bold')))
        self.forDeletion.append(self.can.create_text(self.width / 2 - 300 + 910, self.height / 2 - 200, anchor='e', text=self.texts[self.language]['lwins'], font=('Courier', fontsize, 'bold')))
        self.forDeletion.append(self.can.create_text(self.width / 2 - 100 + 910, self.height / 2 - 200, anchor='e', text=self.texts[self.language]['lratio'], font=('Courier', fontsize, 'bold')))
        for i, line in enumerate(data):
            self.forDeletion.append(self.can.create_text(self.width / 2 - 840 + 910 * (i // 10), self.height / 2 - 120 + 62 * (i % 10), anchor='w', text=line[1], font=('Courier', fontsize)))
            self.forDeletion.append(self.can.create_text(self.width / 2 - 300 + 910 * (i // 10), self.height / 2 - 120 + 62 * (i % 10), anchor='e', text=line[0][0], font=('Courier', fontsize)))
            self.forDeletion.append(self.can.create_text(self.width / 2 - 100 + 910 * (i // 10), self.height / 2 - 120 + 62 * (i % 10), anchor='e', text=round(line[0][0] / (line[0][0] + line[0][1]), 2), font=('Courier', fontsize)))

    def startGame(self):
        self.Richie.flyAway()
        self.applyColour()
        self.names = {0: self.names[0] or self.texts[self.language]['player']+'1', 1: self.names[1] or self.texts[self.language]['player']+'2'}
        for i in self.forDeletion:
            self.can.delete(i)
        self.filled = {0: {}, 1: {}}
        self.forDeletion.append(self.can.create_image(self.width / 2, self.height / 2, image=self.pics['0flair'][0], anchor='center'))
        self.forDeletion.append(self.can.create_image(self.width / 2, self.height / 2, image=self.pics['1flair'][0], anchor='center'))
        self.NameObjs = []
        w = 93
        h = 107
        x, y = map(int, (self.width / 2 - 800, self.height / 2 + 265))
        self.forDeletion.append(self.can.create_image(x, y, image=self.pics['0flair'][1], anchor='center'))
        self.NameObjs.append(self.can.create_text(x + 60, y - 200, text=self.names[0], anchor='center', font=('Courier', 45)))
        self.forDeletion.append(self.NameObjs[-1])
        self.jarplacement = {0: (range(x - w, x + w), range(y - h, y + h))}
        x, y = map(int, (self.width / 2 + 800, self.height / 2 - 265))
        self.forDeletion.append(self.can.create_image(x, y, image=self.pics['1flair'][1], anchor='center'))
        self.NameObjs.append(self.can.create_text(x - 60, y + 200, text=self.names[1], anchor='center', font=('Courier', 45)))
        self.forDeletion.append(self.NameObjs[-1])
        self.jarplacement[1] = (range(x - w, x + w), range(y - h, y + h))
        self.above = self.can.create_image(self.width / 2, self.height / 2, image=self.gridPic, anchor='center')
        self.forDeletion.append(self.above)
        self.turn(choice((0, 1)))
        self.can.bind('<ButtonPress-1>', self.grab)

    def turn(self, player):
        self.current = player
        self.can.itemconfig(self.NameObjs[player], font=('Courier', 45, 'bold'))
        self.can.itemconfig(self.NameObjs[int((player + 1) % 2)], font=('Courier', 45))
        self.grabFieldX, self.grabFieldY = self.jarplacement[player]

    def grab(self, event):
        if event.x in self.grabFieldX and event.y in self.grabFieldY:
            self.piece = Piece(event.x, event.y, self.pics[self.current])
            self.can.bind('<ButtonRelease-1>', self.place)
            self.can.bind('<B1-Motion>', self.drag)

    def drag(self, event):
        if self.piece is not None:
            self.piece.scoot((event.x, event.y))

    def place(self, event):
        where, center = self.gridField((event.x, event.y))
        self.can.unbind('<ButtonPress-1>')
        self.can.unbind('<ButtonRelease-1>')
        self.can.unbind('<B1-Motion>')
        if where and where not in self.filled[0] and where not in self.filled[1]:
            self.piece.pour()
            self.honey[where] = Filling(center[0], center[1], self.pics[str(self.current) + 'honey'], self.above)
            self.can.after(1500, self.cleanUpHoney)
            self.addToPath(where)
            self.turn((self.current + 1) % 2)
        else:
            self.piece.shatter()
            self.can.after(800, self.cleanUpHoney)

    def cleanUpHoney(self):
        self.can.delete(self.piece.id)
        self.piece = None
        self.can.bind('<ButtonPress-1>', self.grab)
        self.can.bind('<B1-Motion>', self.drag)

    def gridField(self, dropped):
        for mid in self.gridMidpoints:
            if dist(dropped, mid) <= 35:
                row = int((mid[1] - 175) / 67)
                col = (mid[0] - 383) // 38
                return (col, row), mid
        return None, None

    def addToPath(self, filled):
        first = True
        for neighbour in [(filled[0] + x, filled[1] + y) for x, y in [(-2, 0), (2, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]]:
            if neighbour in self.filled[self.current]:
                if first:
                    self.filled[self.current][filled] = self.filled[self.current][neighbour]
                    first = False
                else:
                    toChange = self.filled[self.current][neighbour]
                    for merge in self.filled[self.current].items():
                        if merge[1] == toChange:
                            self.filled[self.current][merge[0]] = self.filled[self.current][filled]
        if first:
            self.filled[self.current][filled] = time()
        else:
            self.checkWin(self.filled[self.current][filled])

    def checkWin(self, pathTime):
        if self.current == 0:
            sideOne = set([self.filled[self.current].get((x, 10)) for x in range(0, 21, 2)]) - {None}
            sideTwo = set([self.filled[self.current].get((x, 0)) for x in range(10, 31, 2)]) - {None}
        else:
            sideOne = set([self.filled[self.current].get((x, 10 - x)) for x in range(11)]) - {None}
            sideTwo = set([self.filled[self.current].get((20 + x, 10 - x)) for x in range(11)]) - {None}
        if len(sideOne & sideTwo) == 1:
            self.can.unbind('<ButtonPress-1>')
            self.can.unbind('<ButtonRelease-1>')
            self.can.unbind('<B1-Motion>')
            self.beeRun(pathTime)

    def beeRun(self, pathTime):
        tiles = list(map(lambda x: x[0], filter(lambda x: x[1] == pathTime, self.filled[self.current].items())))
        for chosenOnes in tiles:
            self.honey[chosenOnes].can.after(1650, self.honey[chosenOnes].glow)

        self.can.after(4000, self.winScreen)
        self.current += 1

    def winScreen(self):
        for i in self.forDeletion:
            self.can.delete(i)
        for hexie in self.honey.values():
            hexie.getLost()
        data = json.load(open('leaderboard.txt'))
        if self.names[self.current] in data:
            data[self.names[self.current]]['won'] = data[self.names[self.current]]['won'] + 1
        else:
            data[self.names[self.current]] = {'won': 1, 'lost': 0}
        if self.names[int((self.current + 1) % 2)] in data:
            data[self.names[int((self.current + 1) % 2)]]['lost'] = data[self.names[int((self.current+1) % 2)]]['lost'] + 1
        else:
            data[self.names[int((self.current + 1) % 2)]] = {'won': 0, 'lost': 1}
        with open('leaderboard.txt', 'w') as file:
            json.dump(data, file, indent=2)
        self.forDeletion.append(self.can.create_text(self.width / 2, self.height / 2 - 80, text=self.texts[self.language]['win']+self.names[self.current], font=('Courier', 90)))
        for i in range(15):
            Blast(self.varGraphics['fw' + choice(('s', 'l'))], self.width, self.height)
        h = 115
        w = 310
        fontsize = 67
        x, y = map(int, (self.width / 2 - 400, self.height / 2 + 180))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['button'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['again'], font=('Courier', fontsize)))
        self.clickAreas['quickstart'] = (range(x - w, x + w), range(y - h, y + h))
        x, y = map(int, (self.width / 2 + 400, self.height / 2 + 180))
        self.forDeletion.append(self.can.create_image(x, y, image=self.varGraphics['button'], anchor='center'))
        self.forDeletion.append(self.can.create_text(x, y, text=self.texts[self.language]['back2menu'], font=('Courier', fontsize)))
        self.clickAreas['menu'] = (range(x - w, x + w), range(y - h, y + h))
        self.can.bind('<ButtonPress-1>', self.clickable)


game = Program()
