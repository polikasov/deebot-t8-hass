
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
        if not os.path.exists("painter/"):
            os.mkdir("painter")
            os.mkdir("painter/maps")
        if not os.path.exists("painter/mapdb.json"):
            self.save()
            self.imitNewMap()

    def load(self):
        if not os.path.exists("painter/mapdb.json"):
            self.initDirs()
            return self.load()
        f = open("painter/mapdb.json", "r")
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
        print("saving", json.dumps(vars(self)))
        f = open("painter/mapdb.json", "w")
        f.write(json.dumps(self, default = lambda x: self.toJsonable(x)))
        f.close()
    def getCurFileName(self):
        return "painter/maps/map_" + str(self.CURRENT_MAP_ID) + ".png"

    def imitNewMap(self):
        fname = self.getCurFileName()
        img = Image.new('RGB', (100, 100), color = (73, 109, 137))
        img.save(fname)
        self.save()
        

    def add(self, x,y):
        fname = self.getCurFileName()
        x += 5
        y += 5
        self.POINT_ARRAY += [(x,y)]
        mn_number = min(sorted(self.POINT_ARRAY,  key = lambda x: min(x))[0])
        mx_number = min(sorted(self.POINT_ARRAY,  key = lambda x: max(x))[-1])
        if mn_number < 0:
            self.CENTER_MOVE = mn_number * -1 + 10
        else:
            self.CENTER_MOVE = 0
        
        self.SIZE_X = mx_number + self.CENTER_MOVE + 5
        self.SIZE_Y = mx_number + self.CENTER_MOVE + 5
        _img = Image.new('RGB', [self.SIZE_X, self.SIZE_Y], color = (73, 109, 137))
        draw = ImageDraw.Draw(_img)
        for point in self.POINT_ARRAY:
            x = point[0]
            y = point[1]
            draw.ellipse((x - 5 + self.CENTER_MOVE, y -5 + self.CENTER_MOVE, x + 5 + self.CENTER_MOVE, y + 5 + self.CENTER_MOVE), fill=(255, 0, 0), outline=(0, 0, 0))   
        _img.save(fname)
        self.save()
        pass

    def reset(self):
        pass

    def getFilePath(self):
        pass