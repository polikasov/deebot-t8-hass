from mappainter import MapPainter
import random

testPaint = MapPainter()
x,y = random.randint(0,100), random.randint(0,100)
for i in range(1):
    if random.randint(0,1):
        p = random.randint(0,1)
        if p:
            for k in range(10):
                x += 10
                testPaint.add(x,y)
        else:
            for k in range(10):
                x -= 10
                testPaint.add(x,y)
    else:
        p = random.randint(0,1)
        if p:
            for k in range(10):
                y += 10
                testPaint.add(x,y)
        else:
           for k in range(10):
                y -= 10
                testPaint.add(x,y)

    