from PIL import Image, ImageDraw
from copy import*
import random
import time
import sys
from math import sqrt
from PIL import ImageFilter


class Particle:
    def __init__(self, array):
        #array of coordinates
        self.coordinates = array
        #AABB
        self.minX = sys.maxsize
        self.minY = sys.maxsize
        self.maxX = 0
        self.maxY = 0
        self.width = 0
        self.height = 0
        self.maxLength = 0
        self.thickness = 0
        self.max_length_vector = None
        self.max_length_a = None
        self.max_length_b = None

    def min_max(self):
        for coord in self.coordinates:
            if coord.x < self.minX:
                self.minX = coord.x
            if coord.x > self.maxX:
                self.maxX = coord.x
            if coord.y < self.minY:
                self.minY = coord.y
            if coord.y > self.maxY:
                self.maxY = coord.y

    def set_width(self):
        self.width = self.maxX - self.minX

    def set_height(self):
        self.height = self.maxY - self.minY

    def max_length(self):
        result = 0
        a = None
        b = None
        len_array = len(self.coordinates)
        for i in range(len_array):
            for j in range(i+1, len_array):
                max_length_calc = calculate_vector_length(self.coordinates[i], self.coordinates[j])
                if max_length_calc > result:
                    a = self.coordinates[i]
                    b = self.coordinates[j]
                    result = max_length_calc
        self.max_length_vector = Coordinates((b.x - a.x), (b.y - a.y),0)
        if a.y < b.y:
            self.max_length_a = a
            self.max_length_b = b
        else:
            self.max_length_a = b
            self.max_length_b = a

        line = ImageDraw.Draw(out)
        line.line((a.x, a.y, b.x,b.y), fill=255)
        self.maxLength = result

class Coordinates:
    def __init__(self, x, y,i):
        self.x = x
        self.y = y
        self.i = i #used for skiping this pixel in find path


def calculate_vector_length(a, b):
    return round(sqrt((b.x - a.x)**2 + (b.y - a.y)**2),2)

start = time.time()
change = 1


#need to input the size of image
xSize = 2048
ySize = 2048

boolArray = [[1] * xSize for i in [1] * xSize] #for checking already searched pixels
inputImg = Image.new("RGB", (xSize,xSize))

out = Image.new("RGB", (xSize,ySize))
TheCol = []
img2 = Image.new("RGB", (xSize,ySize))
img3 = Image.new("RGB", (xSize, ySize))

def filter(xSize,ySize):
    global inputImg
    global TheCol
    trash = 90
    for y in range(1,ySize-1):
        for x in range(1,xSize-1):
            col = TheCol[y*xSize +x]
            if (col > trash and col < trash + 20):
                inputImg.putpixel((x, y), TheCol[y * xSize + x] + 20)
            elif col < trash:
                inputImg.putpixel((x, y), TheCol[y * xSize + x] - 20)
            elif  col > 130 and col < trash:
                inputImg.putpixel((x, y), TheCol[y * xSize + x] - 20)
    inputImg = inputImg.filter(ImageFilter.BLUR)
    TheCol = inputImg.getdata()

def findEdge(arr, tmp,xSize,ySize):
    newArr = []
    global change
    global boolArray
    for p in arr:
        th = 0
        if p.i == 1:
            continue

        # x - 1
        if p.x-1 > 0 and TheCol[p.y*xSize + p.x-1] > tmp:
            if boolArray[p.y][p.x - 1] == 1:
                newArr.append(Coordinates(p.x - 1, p.y,0))
                change = 1
                boolArray[p.y][p.x - 1] = 0
            th += 1

        # y -1
        if p.y - 1 > 0 and TheCol[(p.y - 1) * xSize + p.x] > tmp:
            if boolArray[p.y - 1][p.x] == 1:
                newArr.append(Coordinates(p.x, p.y - 1,0))
                change = 1
                boolArray[p.y - 1][p.x] = 0
            th += 1

            # y + 1
        if p.y + 1 < ySize and TheCol[(p.y + 1) * xSize + p.x] > tmp:
            if boolArray[p.y + 1][p.x] == 1:
                newArr.append(Coordinates(p.x, p.y + 1,0))
                change = 1
                boolArray[p.y + 1][p.x] = 0
            th += 1

            # x + 1
        if p.x + 1 < xSize and TheCol[p.y * xSize + p.x + 1] > tmp:
            if boolArray[p.y][p.x + 1] == 1:
                newArr.append(Coordinates(p.x + 1, p.y,0))
                change = 1
                boolArray[p.y][p.x + 1] = 0
            th += 1
        if th == 0:
            p.i += 1
        if(th < 4):
            newArr.append(copy(p))
    return newArr;

def find(x,y, xSize,ySize):
    global change
    tmp = [Coordinates(x,y,0)]
    a = 0
    lenx = 0
    while change or a < 1:
        change = 0
        tmp2 = findEdge(tmp, 90, xSize,ySize)
        if lenx == len(tmp2):
            break
        else:
            lenx = len(tmp2)
        tmp = tmp2
        if change == 0:
            a += 1
    a = 0
    while change or a < 1:
        change = 0
        tmp2 = findEdge(tmp, 60, xSize,ySize)
        if lenx == len(tmp2):
            break
        else:
            lenx = len(tmp2)
        tmp = tmp2
        if change == 0:
            a += 1
    return tmp


def search(xSize,ySize):
    global boolArray
    global change
    arr = []
    for y in range(1, ySize -1):
        for x in range(1, xSize -1):
            if (TheCol[y*xSize + x] > 130) and boolArray[y][x] == 1:
                change = 1
                tmp = find(x,y, xSize, ySize)
                if len(tmp) > 36:
                    arr.append(Particle(tmp))
                for a in tmp:
                    out.putpixel((a.x, a.y),255)
    print(len(arr))
    return arr

def main(argv):

    global inputImg
    global TheCol
    global xSize
    global ySize
    global img2
    global out

    args = sys.argv[1:]
    if len(args) < 1:
        return
    inputImg = Image.open(args[0]).convert("L")
    xSize, ySize = inputImg.size
    if xSize < 10 or ySize < 10:
        return 1
    img2 = Image.new("RGB", (xSize,ySize))
    out = Image.open(args[0])
    TheCol = inputImg.getdata()
    filter(xSize,ySize)

    output = file("particles.csv", "w")
    output.writelines("number;width;height;maxLength;thickness")
    output.writelines("\n")
    particles = search(xSize,ySize)
    i = 1
    for particle in particles:
        particle.min_max()
        particle.set_width()
        particle.set_height()
        particle.max_length()
        if not (particle.minX == 1 or particle.minY == 1 or particle.maxX == xSize - 1 or particle.maxY == ySize - 1):
            output.writelines(str(i) + ";" + str(particle.width) + ";" + str(particle.height) + ";" + str(
                particle.maxLength) + ";" + str(particle.thickness))
            output.writelines("\n")
            for a in particle.coordinates:
                # print(a.x, " ", a.y)
                out.putpixel((a.x, a.y), 255)
            x = particle.minX
            y = particle.minY
            while x <= particle.maxX:
                out.putpixel((x, particle.minY), 255)
                out.putpixel((x, particle.maxY), 255)
                x += 1
            while y <= particle.maxY:
                out.putpixel((particle.minX, y), 255)
                out.putpixel((particle.maxX, y), 255)
                y += 1

            i += 1
    output.close()

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)


out.save("outputWithLines.jpg")