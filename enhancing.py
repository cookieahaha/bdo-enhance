#target
#enhance
#items / inventory
#armor
#weapon
#rate
#failstack
#price
#loss
#durability
#repair
#profit (silver calculation for items in inventory)
#downgrade service 15 > 14

#webapp using Flask

#accesory
#blackstar
#bossarmor


import random
import csv
import pandas as pd

from flask import Flask
from flask import render_template, request


failstack = 0 # get when you fail. high failstack increases the chance for successful enhancement
blackstone_armor = 0 # spend 1 to enhance armor 14
blackstone_weapon = 0 # spend 1 to enhance weapon 14
conc_armor = 0 # spend 1 to enhance armor 15+
conc_weapon = 0 # spend 1 to enhance weapon 15+
reblath = 0 # use to repair item reblath
memory_fragment = 0 # use to repair item
downgrade_service = 0 # from 15 to 14


'''
re = pd.read_csv('armor.csv')
print(re.head())
'''

def stone(target):
  global blackstone_armor
  global blackstone_weapon
  global conc_armor
  global conc_weapon

  #print('hi')
  #print(target.type())
  type = target.getType()
  level = target.getLevel()

  if type == 'reblath':
    if level < 15:
      blackstone_armor += 1
    else:
      conc_armor += 1
  elif type == 'dande':
    if level < 15:
      blackstone_weapon += 1
    else:
      conc_weapon += 1
  else:
      print('cannot find stone type')


def hit(target):
  global failstack
  global downgrade_service

  stone(target)

  rand = random.randint(0,10000)
  target_rate = target.rate()
  print('roll: ' + str(rand) + ' vs rate: ' + str(target_rate * 100))
  if target_rate * 100 >= rand:
    failstack = 0
    target.win()
    print('SUCCEEDED \n')
    if target.name() == 'reblath 15':
      downgrade_service += 1
      target.downgrade()
      print('used downgrade service. now its back to 14')
    else:
      return
  else:
    failstack += target.fs()
    target.lose()
    print('FAILED \n')

def printItems(items):
  num = 0
  for i in items:
    print(str(num) + ': ' + i.name() + ' ' + str(i.getDurability()))
    num += 1

def printStones():
  print('black stone armor spent: ' + str(blackstone_armor))
  print('black stone weapon spent: ' + str(blackstone_weapon))
  print('concentrated magical black stone armor spent: ' + str(conc_armor))
  print('concentrated magical black stone weapon spent: ' + str(conc_weapon))
  print('reblath spent: ' + str(reblath))
  print('memory fragment spent: ' + str(memory_fragment))
  print('downgrade service: ' + str(downgrade_service))

def printRateStack(item):
  print(item.name() + ', success rate = ' + str(item.rate()) + '%')
  print('failstack: ' + str(failstack))

def getPrice(df, item):
    #print(df)
    return df.loc[item, 'price']

def getLoss():

  df = pd.read_csv('price.csv', index_col = 'name')
  #print(df[0][1])
  #print(df[0,1])
  #print(df.iloc[0,1])
  #print(df)
  #getPrice(df, 'blackstone_armor') 
  price_stone_armor = blackstone_armor * getPrice(df, 'blackstone_armor')
  price_stone_weapon = blackstone_weapon * getPrice(df, 'blackstone_weapon')
  price_conc_armor = conc_armor * getPrice(df, 'conc_armor')
  price_conc_weapon = conc_weapon * getPrice(df, 'conc_weapon')
  price_reblath = reblath * getPrice(df, 'reblath')
  price_memory = memory_fragment * getPrice(df, 'memory_fragment')
  price_downgrade = downgrade_service * getPrice(df, 'downgrade_service')

  loss = price_stone_armor + price_stone_weapon + price_conc_armor + price_conc_weapon + price_reblath + price_memory + price_downgrade
  return loss

def getProfit(items):

  df = pd.read_csv('price.csv', index_col = 'name')
  profit = 0
  for item in items:
    profit += getPrice(df, item.name())
    #print(profit)
  return profit


def printSilver(items):

  profit = getProfit(items)
  loss = getLoss()
  net = profit - loss
  print('profit = ' + str(profit))
  print('loss = ' + str(loss))
  print('net = ' + str(net) + '\n')

def repairAll(items):
  for item in items:
    item.repair()
  print('\n')

class Target():
  
  global failstack
  global reblath
  global memory_fragment

  def __init__(self, ind, ty, le, dr):
    self.index = int(ind)
    self.type = ty
    self.level = int(le)
    self.durability = int(dr)

  def getIndex(self):
    return self.index

  def name(self):
    name = self.type + ' ' + str(self.level)
    return name

  def type(self):
    return self.type
  def getType(self):
    type = self.type
    return type

  def level(self):
    return self.level
  def getLevel(self):
    level = self.level
    return level
  def downgrade(self):
    self.level = 14

  def getDurability(self):
      dura = self.durability
      return dura

  def rate(self):
    rate = 0  
    if self.type == 'reblath':
      '''
      with open('armor.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            print(row[0])
            if row[0] == failstack:
                rate = row[0][self.level - 6]
                break
            else:
                continue
      '''
      df = pd.read_csv('armor.csv')
      rate = df.iloc[failstack, self.level - 4]

      return rate
    elif self.type == 'dande':
      df = pd.read_csv('weapon.csv')
      rate = df.iloc[failstack, self.level - 6]
      return rate
    else:
      return

  def fs(self):
    if self.level < 15:
      return 1
    elif self.level == 15:
      return 2
    elif self.level == 16:
      return 3
    elif self.level == 17:
      return 4
    elif self.level == 18:
      return 5
    elif self.level == 19:
      return 6
    else:
      print('failstack error')

  def win(self):
    self.level += 1

  def lose(self):
      if self.level < 15:
          self.durability -= 5
      else:
          self.durability -= 10
      if self.level > 16:
        self.level -= 1
      else:
        return

  def repair(self):
      global reblath
      global memory_fragment

      gap = 100 - self.durability
      self.durability = 100
      #reb = reblath
      if self.type == 'reblath':
        #reb += (gap / 2)
        reblath += (gap / 10)
        #reblath += reb
      elif self.type == 'dande':
        memory_fragment += gap
      else:
        print('type not implemented')
      print('repaired ' + self.type)


'''
a = 'hello'
b = 20
print(a + str(b))
'''

'''
a = 'abc'
b = 'der'
c = 'erfaes'
d = 'gdh'

items= []
items.append(a)
items.append(b)
items.append(c)
items.append(d)
for i in items:
  print(i)
'''
# create list of items (inventory)
items = []
with open('items.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        items.append(Target(row[0], row[1], row[2], row[3]))
        #print(isinstance(row[0], str))


app = Flask(__name__)

@app.route('/')
def webapp():
    loss = getLoss()
    profit = getProfit(items)
    net = profit - loss
    values = {"failstack": failstack, "blackstone_armor": blackstone_armor, "blackstone_weapon": blackstone_weapon, "conc_armor": conc_armor, "conc_weapon": conc_weapon, "reblath": reblath, "memory_fragment": memory_fragment, "downgrade_service": downgrade_service, "profit": '{:,}'.format(profit), "loss": '{:,}'.format(loss), "net": '{:,}'.format(net)}
    item_names = []
    for item in items:
      item_names.append(str(item.getIndex()) + ' ' + item.name() + ' ' + str(item.getDurability()) + ' ' + str(item.rate()) + '%')
    return render_template('index.html', values = values, item_names = item_names)

@app.route('/hit',methods=['post'])
def post():
  index = int(request.form["number"])
  hit(items[index])
  return webapp()

@app.route('/repair',methods=['post'])
def repairWeb():
  repairAll(items)
  return webapp()

if __name__ == '__main__':
    app.run()



while 1 == 1:
  printItems(items)
  printStones()


  choice = input('what do you wanna hit? num(number) / r(repair) / s(silver):')
  if choice == 's':
    printSilver(items)
  elif choice == 'r':
    #items[3].repair()  
    repairAll(items)
  else:
    item_int = int(choice)
    item = items[item_int]

    printRateStack(item)

    #print('fs = ' failstack ", item = " item)
    answer = input('enhance?(y/n):')
    if answer == 'y':
      hit(item)
    else:
      print('good bye')

    while 1 == 1:
      printRateStack(item)
      hit_again = input('wanna hit again?(y/n)')
      if hit_again == 'y':
        hit(item)
      else:
        print('\n')
        break

