
import json
from maya import cmds

import os
if 'FABRIC_RIGGINGTOOLBOX_PATH' not in os.environ:
  raise Exception("Please set the rigging ")
toolboxPath = os.environ['FABRIC_RIGGINGTOOLBOX_PATH']


cmds.file(new=True,f=True)



##############################################
## Set up the BlendShapesParams node.

initnode = cmds.createNode("spliceMayaNode", name = "BlendShapesSphereCharacter_Init")

cmds.fabricSplice('addInputPort', initnode, json.dumps({'portName':'filePath', 'dataType':'String', 'addMayaAttr': True}))
cmds.fabricSplice('addOutputPort', initnode, json.dumps({'portName':'stack', 'dataType':'GeometryStack', 'extension':'RiggingToolbox', 'addSpliceMayaAttr':True, 'autoInitObjects': True}))

cmds.setAttr(initnode + '.filePath', toolboxPath+"/Tests/GeometryStack/Resources/blendShapesSphereCharacter.json", type="string");


cmds.fabricSplice('addKLOperator', initnode, '{"opName":"blendShapesSphereCharacter"}', """

require RiggingToolbox;

operator blendShapesSphereCharacter(
  String filePath,
  io GeometryStack stack
) {
  report("Loading Character Definition:" + filePath);
  stack.loadJSONFile(filePath);
}
""")
  

##############################################
## Set up the BlendShapesParams node.

blendShapesNode = cmds.createNode("spliceMayaNode", name = "BlendShapesSphereCharacter_BlendShapes")

cmds.fabricSplice('addIOPort', blendShapesNode, json.dumps({'portName':'stack', 'dataType':'GeometryStack', 'extension':'RiggingToolbox', 'addSpliceMayaAttr':True, 'autoInitObjects': False }))
cmds.fabricSplice('addInputPort', blendShapesNode, json.dumps({'portName':'shape0', 'dataType':'Scalar', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', blendShapesNode, json.dumps({'portName':'shape1', 'dataType':'Scalar', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', blendShapesNode, json.dumps({'portName':'displayDebugging', 'dataType':'Boolean', 'addMayaAttr': True}))

cmds.fabricSplice('addKLOperator', blendShapesNode, '{"opName":"blendShapesSphereCharacter_BlendShapes"}', """

require RiggingToolbox;

operator blendShapesSphereCharacter_BlendShapes(
  io GeometryStack stack,
  Scalar shape0,
  Scalar shape1,
  Boolean displayDebugging
) {
  if(stack.numGeometryOperators() > 1){
    BlendShapesModifier blendShapesModifier = stack.getGeometryOperator(1);

    // Modify the blend params and then reevaluate. 
    Scalar weights[];
    weights.resize(2);
    weights[0] = shape0;
    weights[1] = shape1;
    blendShapesModifier.setBlendWeights(weights);
    blendShapesModifier.setDisplayDebugging(displayDebugging);
  }
}
""")

cmds.connectAttr(initnode + '.stack', blendShapesNode + '.stack')


##############################################
## Set up the BlendShapesParams node.

evalStackNode = cmds.createNode("spliceMayaNode", name = "BlendShapesSphereCharacter_Eval")

cmds.fabricSplice('addInputPort', evalStackNode, json.dumps({'portName':'stack', 'dataType':'GeometryStack', 'extension':'RiggingToolbox', 'addSpliceMayaAttr':True, 'autoInitObjects': False}))
cmds.fabricSplice('addOutputPort', evalStackNode, json.dumps({'portName':'eval', 'dataType':'Scalar', 'addMayaAttr': True}))

cmds.connectAttr(blendShapesNode + '.stack', evalStackNode + '.stack')

cmds.fabricSplice('addKLOperator', evalStackNode, '{"opName":"blendShapesSphereCharacter_Eval"}', """

require RiggingToolbox;

operator blendShapesSphereCharacter_Eval(
  io GeometryStack stack,
  Scalar eval
) {
  EvalContext context();
  stack.evaluate(context);
}
""")


##############################################
## Set up the eval locator.

forceEvalLocator = cmds.createNode("locator", name = "forceEval")
cmds.connectAttr(evalStackNode + '.eval', forceEvalLocator + '.localPosition.localPositionY')
