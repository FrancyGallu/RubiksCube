#!/usr/bin/python
import prman
import copy

ri = prman.Ri()
ri.Option("rib", {"string asciistyle": "indented"})

####################################### FUNCTIONS #######################################
def chunks(l, n):
  """Yield successive n-sized chunks from l."""
  for i in range(0, len(l), n) :
    yield l[i:i + n]

def changeCoord(faceVerts,orientation) :
  """Change the coordinates of each face vertex to create a smaller patch on top of it"""
  # apply change according to sign of coords:
  # HOVER = ammount of distance of patch from cube
  HOVER = 0.005
  for i in range(0,4) :
    if faceVerts[i][orientation] > 0 :
      faceVerts[i][orientation] += HOVER
    else :
      faceVerts[i][orientation] -= HOVER
  # MARGIN = ammount of distance of patch from all the sides of cube 
  MARGIN = 0.09
  for i in range(0,4) :
    for j in range(0,3) :
      if j == orientation :
        continue
      if faceVerts[i][j] > 0 :
        faceVerts[i][j] -= MARGIN
      else :
        faceVerts[i][j] += MARGIN
  # save result in simple array
  newFaceVerts = []
  for j in range(0,3) :
    newFaceVerts += [ faceVerts[0][j] ]
  for j in range(0,3) :
    newFaceVerts += [ faceVerts[3][j] ]
  for j in range(0,3) :
    newFaceVerts += [ faceVerts[1][j] ]
  for j in range(0,3) :
    newFaceVerts += [ faceVerts[2][j] ]
  # return result
  return newFaceVerts

def drawPatches(points, nvertices, drawAllPatches) :
  """Given a pice of the Cube, it create a patch on top of each face"""
  # Transform the array of points into a dictionary
  vertices = []
  vertices = list(chunks(points, 3))
  verticesDics = [{}]
  index = 0
  for vertex in vertices :
    verticesDics[-1][index] = vertex
    index += 1
  # Transform the array of nvertices into a list of faces, each having the index of their vertices 
  faces = []
  faces = list(chunks(nvertices, 4))
  # For each face, draw the relative patch
  for face in faces :
    faceVerts = []
    for vert in face :
      vertCopy = copy.deepcopy(verticesDics[0][vert])
      faceVerts += [ vertCopy ]
    # establish face orientation: 0=x 1=y 2=z(visible) -2=z(invisible)
    orientation = -1
    for i in range(0,3) :
      if faceVerts[0][i] == faceVerts[1][i] == faceVerts[2][i] == faceVerts[3][i] :
        orientation = i
        if i==2 and faceVerts[0][i]>0 :
          orientation = -i
        break
    newFaceVerts = changeCoord(faceVerts, orientation)
    # Set up the patches bump map (Scratches)
    ri.Pattern("PxrBump","patchBump",{
                                      "string filename" : "textures/bump.tx",
                                      "float scale": 0.003,
                                      "int invertT" : 0
                                     })
    # Set colour of patches according to orientation
    if orientation == 0 :
      ri.Bxdf( "PxrDisney","bxdf", {
                                    "color baseColor" : [1,1,0],
                                    "float specular" : [1],
                                    "reference normal bumpNormal" : ["patchBump:resultN"]
                                   })
    elif orientation == 1 :
      ri.Bxdf( "PxrDisney","bxdf", {
                                    "color baseColor" : [0,0,1],
                                    "float specular" : [1],
                                    "float roughness" : [0.3],
                                    "reference normal bumpNormal" : ["patchBump:resultN"]
                                   })
    else :  
      ri.Bxdf( "PxrDisney","bxdf", {
                                    "color baseColor" : [1,0,0],
                                    "float specular" : [1],
                                    "reference normal bumpNormal" : ["patchBump:resultN"]
                                   })
    # Don't draw patches in internal areas of the Cube or on the back, to avoid red reflection on the ground
    if not((orientation == 0 and drawAllPatches == 0) or orientation == -2) :
      ri.Patch("bilinear",{'P':newFaceVerts})


def drawPiece(drawAllPatches) :
  """Draw a single piece of the Cube"""
  npolys=[4,4,4,4,4,4]
  points=[-0.5, -0.5, -0.5, #0
          0.5, -0.5, -0.5, #1
          -0.5, 0.5, -0.5, #2
          0.5, 0.5, -0.5, #3
          -0.5, -0.5, 0.5, #4
          0.5, -0.5, 0.5, #5
          -0.5, 0.5, 0.5, #6
          0.5, 0.5, 0.5] #7
  nvertices=[0, 1, 3, 2, #0
             0, 4, 5, 1, #1
             0, 2, 6, 4, #2
             1, 5, 7, 3, #3
             2, 3, 7, 6, #4
             4, 6, 7, 5] #5
  ri.Pattern("PxrBump","pieceBump",{
                                    "string filename" : "textures/bump.tx",
                                    "float scale": 0.005,
                                    "int invertT" : 0
                                   })
  ri.Bxdf( "PxrDisney","bxdf", {
                                "color baseColor" : [0.1,0.1,0.1],
                                "float specular" : [0.1],
                                "float roughness" : [0.3],
                                "reference normal bumpNormal" : ["pieceBump:resultN"]
                               })
  ri.SubdivisionMesh("catmull-clark", 
                      npolys, 
                      nvertices, 
                      [ri.CREASE, ri.CREASE, ri.CREASE, ri.CREASE], [5, 1, 5, 1, 5, 1, 5, 1], [4, 5, 7, 6, 4, 0, 1, 3, 2, 0, 0, 4, 6, 2, 0, 1, 5, 7, 3, 1], [3, 3, 3, 3], 
                      {ri.P:points})
  drawPatches(points, nvertices, drawAllPatches)

####################################### SCENE SETUP #######################################
filename = "__render"
ri.Begin(filename)
ri.Display("RubikCube.exr", "it", "rgba")
ri.Format(1280,720,1)

# setup the raytrace / integrators
ri.Hider("raytrace" ,{"int incremental" :[1], "int maxsamples": 128, "int minsamples": 128})
ri.PixelVariance (0.01)
ri.ShadingRate(10)
ri.ShadingInterpolation("smooth")
ri.Integrator ("PxrPathTracer" ,"integrator", {
                                                "float numLightSamples" : [4],
                                                "float numBxdfSamples" : [4]
                                              })
ri.DepthOfField(1.5,0.1,4)
ri.Projection(ri.PERSPECTIVE,{ri.FOV:50})

# Position the camera in the scene
ri.Translate(0,-1.5,6)
ri.Rotate(50,0,1,0)
ri.Rotate(-30,1,0,0) 
ri.Rotate(-30,0,0,1)

ri.WorldBegin()

####################################### LIGHTING #######################################
# Light 1 - Main shadow source, top right corner
ri.AttributeBegin()
ri.Declare("areaLight1" ,"string")
ri.AreaLightSource( "PxrStdAreaLight", {ri.HANDLEID:"areaLight1",
                                        "float exposure" : [13],
                                        "float intensity" : [10],
                                        "float enableTemperature" : [1],
                                        "float temperature" : [7500]
                                       })
ri.TransformBegin()
ri.Translate(-12,20,160)
ri.Rotate(180,1,0,0)
ri.Rotate(10,0,1,0)
ri.Scale(60,60,60)
ri.Geometry("rectlight")
ri.TransformEnd()
ri.AttributeEnd()

# Light 2 - Main light source, top right corner
ri.AttributeBegin()
ri.Declare("areaLight2" ,"string")
ri.AreaLightSource( "PxrStdAreaLight", {ri.HANDLEID:"areaLight2",
                                        "float exposure" : [8],
                                        "float intensity" : [10],
                                        "float enableTemperature" : [1],
                                        "float temperature" : [7500],
                                        "float enableShadows" : [0]
                                       })
ri.TransformBegin()
ri.Translate(-8,10,30)
ri.Rotate(180,1,0,0)
ri.Rotate(-10,0,1,0)
ri.Scale(0.02,0.02,0.02)
ri.Geometry("spherelight")
ri.TransformEnd()
ri.AttributeEnd()

# Light 3 - Environment Light
ri.AttributeBegin()
ri.Declare("envLight", "string")
ri.AreaLightSource("PxrStdEnvMapLight", {ri.HANDLEID:"envLight",
                                        "string rman__EnvMap" : ["textures/envtex.tx"],
                                        "float enableShadows" : [1],
                                        "float exposure" : [0.5],
                                        "color envTint" : [0.9, 0.97, 1]
                                        })
ri.TransformBegin()
ri.Rotate(180,0,1,0)
ri.Geometry("envsphere")
ri.TransformEnd()
ri.AttributeEnd()

####################################### MODELLING #######################################
# rotated pieces in front right side
ri.TransformBegin()
ri.Rotate(15, 1, 0, 0)
ri.Translate(0, 0.2, -0.3)
for z in range(0, 3) :
  for y in range (0, 3) :
    ri.TransformBegin()
    ri.Translate(0,y,z)
    drawAllPatches = 1
    drawPiece(drawAllPatches)
    ri.TransformEnd()
ri.TransformEnd()
# rest of the pieces of the Cube
for x in range (-2, 0) :
  for z in range(0, 3) :
    for y in range (0, 3) :
      ri.TransformBegin()
      ri.Translate(x,y,z)
      drawAllPatches = 0
      drawPiece(drawAllPatches)
      ri.TransformEnd()

# Ground plane
ri.Attribute("trace", {
                        "displacements" : [1]
                      })
ri.Attribute("displacementbound", {
                                    "sphere" : [1],
                                    "coordinatesystem" : ["shader"]
                                  })
ri.Displacement( "shaders/groundDisp", {
                                        "float Km" : [0.4],
                                        "float Layers" : [30]
                                       })
ri.Pattern("PxrOSL","groundShader",{
                                    "string shader" : "shaders/groundShader",
                                    "float Frequency" : [32]
                                   })
ri.Bxdf( "PxrDisney","bxdf", {
                              "reference color baseColor" : ["groundShader:Cout"],
                              "float specular" : [0],
                              "roughness" : [1]
                             })
ppoints = [-30, -0.7, -30, -30, -0.7, 30, 30, -0.7, -30, 30, -0.7, 30]
ri.TransformBegin()
ri.Rotate(-5,0,0,1)
ri.Patch("bilinear",{'P':ppoints})
ri.TransformEnd()

ri.WorldEnd()
ri.End()