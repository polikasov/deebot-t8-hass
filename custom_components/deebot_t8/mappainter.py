
from ctypes.wintypes import SIZE
import os
import json
from PIL import Image, ImageDraw

class MapPainter(object):
    
    CURRENT_MAP_ID = 0
    LAST_POSITION_X = -10000
    LAST_POSITION_Y = -10000
    SIZE_X = 100
    SIZE_Y = 100
    CENTER_MOVE = 0
    POINT_ARRAY = []

    def __init__(self):
        self.load()
        pass

    def toJsonable(self, x):
        try:
            return x.__dict__
        except:
            return {}

    def initDirs(self):
        if not os.path.exists("www/painter/"):
            os.mkdir("www/painter")
            os.mkdir("www/painter/maps")
        if not os.path.exists("www/painter/mapdb.json"):
            self.save()
            self.initNewMap()

    def load(self):
        if not os.path.exists("www/painter/mapdb.json"):
            self.initDirs()
            return self.load()
        f = open("www/painter/mapdb.json", "r")
        res = json.loads(f.readline())
        f.close()
        try:
            self.CURRENT_MAP_ID = res["CURRENT_MAP_ID"]
            self.LAST_POSITION_Y = res.get("LAST_POSITION_Y")
            self.LAST_POSITION_X = res.get("LAST_POSITION_X")
            self.CENTER_MOVE = res.get("CENTER_MOVE")
            self.SIZE_Y = res.get("SIZE_Y")
            self.SIZE_X = res.get("SIZE_X")
            self.POINT_ARRAY = res['POINT_ARRAY']
        except Exception as e:
            self.CURRENT_MAP_ID = 0
            self.LAST_POSITION_X = -10000
            self.LAST_POSITION_Y = -10000
            self.SIZE_X = 100
            self.SIZE_Y = 100
            self.CENTER_MOVE = 0
            self.POINT_ARRAY = []
            self.save()
            raise "error with opening config"
            pass

        pass

    def save(self):
        # print("saving", json.dumps(vars(self)))
        f = open("www/painter/mapdb.json", "w")
        f.write(json.dumps(self, default = lambda x: self.toJsonable(x)))
        f.close()
    def getCurFileName(self):
        return "www/painter/maps/map_" + str(self.CURRENT_MAP_ID) + ".png"

    def initNewMap(self):
        fname = self.getCurFileName()
        img = Image.new('RGB', (100, 100), color = (73, 109, 137))
        img.save(fname)
        self.save()
        

    def add(self, x,y,z = 0):
        x += 5
        y += 5
        if len(self.POINT_ARRAY) > 0:
            if self.POINT_ARRAY[-1] == (x,y):
                return x, y
        self.POINT_ARRAY += [(x,y)]
        self.save()
        return x, y
    
    def paint(self):
        fname = self.getCurFileName()
        mn_number = min(sorted(self.POINT_ARRAY,  key = lambda x: min(x))[0])
        mx_number = max(sorted(self.POINT_ARRAY,  key = lambda x: max(x))[-1])
        if mn_number < 0:
            self.CENTER_MOVE = mn_number * -1 + 10
        else:
            self.CENTER_MOVE = 0
        
        self.SIZE_X = mx_number + self.CENTER_MOVE + 5
        self.SIZE_Y = mx_number + self.CENTER_MOVE + 5
        with Image.new('RGB', [self.SIZE_X, self.SIZE_Y], color = (73, 109, 137)) as _img:
            draw = ImageDraw.Draw(_img)
            prev_line = -1
            for point in self.POINT_ARRAY:
                x1 = point[0] - 5 + self.CENTER_MOVE
                y1 = point[1] - 5 + self.CENTER_MOVE
                x2 = point[0] + 5 + self.CENTER_MOVE
                y2 = point[1] + 5 + self.CENTER_MOVE
                # print(self.SIZE_X, x1, x2)
                # print(self.SIZE_Y, y1, y2)
                draw.ellipse((x1, y1, x2, y2), fill=(255, 0, 0), outline=(0, 0, 0))   
                if prev_line != -1:
                    _x1, _y1 = point[0] + self.CENTER_MOVE, point[1] + self.CENTER_MOVE
                    _x2, _y2 = self.POINT_ARRAY[prev_line][0]+ self.CENTER_MOVE, self.POINT_ARRAY[prev_line][1]+ self.CENTER_MOVE
                    _SIZE = 15
                    # draw.polygon((_x1-_SIZE, _y1 + _SIZE, _x1 + _SIZE, _y1 - _SIZE, _x2 - _SIZE, _y2 - _SIZE, _x2 + _SIZE, _y2 + _SIZE), fill = (255,0,0))
                    draw.line((_x1, _y1, _x2, _y2),  fill=(255, 0, 0), width = _SIZE)

                prev_line += 1
                # break
            _img.save(fname)
        self.save()

    def reset(self):
        if self.POINT_ARRAY == []:
            return 0
        self.CURRENT_MAP_ID += 1 % 100
        self.initNewMap()
        self.POINT_ARRAY = []
        self.save()

    def getFilePath(self):
        return self.getCurFileName().replace("www/", "/local/")