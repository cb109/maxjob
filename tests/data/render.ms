-- Render some teapots.
delete objects

print "create some teapots"
for i = 1 to 10 do (
    local pos = [i * 20, 0, 0]
    local even = (mod i 2) == 0
    Teapot pos:pos wirecolor:(if even then red else green)
)

print "lets zoom out"
actionMan.executeAction 0 "310"  -- Tools: Zoom Extents Selected

print "now we will setup the render output"
rendSaveFile = true
rendOutputFileName = pathConfig.appendPath (pathConfig.removePathLeaf (getThisScriptFileName())) "render.png"
print ("rendering to:" + rendOutputFileName)
deleteFile rendOutputFileName
print "now render the image"
max quick render

print "nice, we are done here"
