
import json
from maya import cmds

import os
if 'FABRIC_RIGGINGTOOLBOX_PATH' not in os.environ:
  raise Exception("Please set the rigging ")
toolboxPath = os.environ['FABRIC_RIGGINGTOOLBOX_PATH']

cmds.file(new=True,f=True)
cmds.file(toolboxPath+"/Tests/GeometryStack/Resources/SkinnedTube_hierarchy.ma", r=True);


##############################################
## Set up the loader node.

initnode = cmds.createNode("spliceMayaNode", name = "tubeCharacter_Init")

cmds.fabricSplice('addInputPort', initnode, json.dumps({'portName':'filePath', 'dataType':'String', 'addMayaAttr': True}))
cmds.fabricSplice('addOutputPort', initnode, json.dumps({'portName':'stack', 'dataType':'GeometryStack', 'extension':'RiggingToolbox', 'addSpliceMayaAttr':True, 'autoInitObjects': True}))

cmds.setAttr(initnode + '.filePath', toolboxPath+"/Tests/GeometryStack/Resources/tubeCharacter_SkinningAndDeltaMush.json", type="string");


cmds.fabricSplice('addKLOperator', initnode, '{"opName":"tubeCharacter_Init"}', """

require RiggingToolbox;

operator tubeCharacter_Init(
  String filePath,
  io GeometryStack stack
) {
  report("Loading Character Definition:" + filePath);
  stack.loadJSONFile(filePath);
}
""")
  

##############################################
## Set up the skinning pose node.

poseNode = cmds.createNode("spliceMayaNode", name = "tubeCharacter_Skinning")

cmds.fabricSplice('addIOPort', poseNode, json.dumps({'portName':'stack', 'dataType':'GeometryStack', 'extension':'RiggingToolbox', 'addSpliceMayaAttr':True, 'autoInitObjects': False }))
cmds.fabricSplice('addInputPort', poseNode, json.dumps({'portName':'displayDebugging', 'dataType':'Boolean', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', poseNode, json.dumps({'portName':'deformers', 'dataType':'Mat44[]', 'addMayaAttr': True, 'arrayType':"Array (Multi)"}))

cmds.connectAttr('SkinnedTube_hierarchy_joint1.worldMatrix[0]', poseNode + '.deformers[0]')
cmds.connectAttr('SkinnedTube_hierarchy_joint2.worldMatrix[0]', poseNode + '.deformers[1]')
cmds.connectAttr('SkinnedTube_hierarchy_joint3.worldMatrix[0]', poseNode + '.deformers[2]')
cmds.connectAttr('SkinnedTube_hierarchy_joint4.worldMatrix[0]', poseNode + '.deformers[3]')


cmds.fabricSplice('addKLOperator', poseNode, '{"opName":"tubeCharacter_Skinning"}', """

require RiggingToolbox;

operator tubeCharacter_Skinning(
  io GeometryStack stack,
  Mat44 deformers[],
  Boolean displayDebugging
) {
  if(stack.numGeometryOperators() > 1){
    SkinningModifier skinningModifier = stack.getGeometryOperator(1);
    skinningModifier.setPose(deformers);
    skinningModifier.setDisplayDebugging(displayDebugging);
  }
}
""")

cmds.connectAttr(initnode + '.stack', poseNode + '.stack')


##############################################
## Set up the delta mush node.

mushNode = cmds.createNode("spliceMayaNode", name = "tubeCharacter_DeltaMush")

cmds.fabricSplice('addIOPort', mushNode, json.dumps({'portName':'stack', 'dataType':'GeometryStack', 'extension':'RiggingToolbox', 'addSpliceMayaAttr':True, 'autoInitObjects': False }))
cmds.fabricSplice('addInputPort', mushNode, json.dumps({'portName':'iterations', 'dataType':'Integer', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', mushNode, json.dumps({'portName':'displayDebugging', 'dataType':'Boolean', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', mushNode, json.dumps({'portName':'displayMask', 'dataType':'Boolean', 'addMayaAttr': True}))

cmds.setAttr(mushNode + '.iterations', 30);

cmds.fabricSplice('addKLOperator', mushNode, '{"opName":"tubeCharacter_DeltaMush"}', """

require RiggingToolbox;

operator tubeCharacter_DeltaMush(
  io GeometryStack stack,
  Integer iterations,
  Boolean displayMask,
  Boolean displayDebugging
) {
  if(stack.numGeometryOperators() > 3){
    WeightmapModifier weightmapModifier = stack.getGeometryOperator(2);
    weightmapModifier.setDisplay(displayMask);

    DeltaMushModifier deltaMushModifier = stack.getGeometryOperator(3);
    deltaMushModifier.setNumIterations(iterations);
    deltaMushModifier.setDisplayDebugging(displayDebugging);
  }
}
""")

cmds.connectAttr(poseNode + '.stack', mushNode + '.stack')


##############################################
## Set up the eval/render node.

evalStackNode = cmds.createNode("spliceMayaNode", name = "tubeCharacter_Eval")

cmds.fabricSplice('addInputPort', evalStackNode, json.dumps({'portName':'stack', 'dataType':'GeometryStack', 'extension':'RiggingToolbox', 'addSpliceMayaAttr':True, 'autoInitObjects': False}))
cmds.fabricSplice('addOutputPort', evalStackNode, json.dumps({'portName':'eval', 'dataType':'Scalar', 'addMayaAttr': True}))


cmds.fabricSplice('addInputPort', evalStackNode, json.dumps({'portName':'displayGeometries', 'dataType':'Boolean', 'addMayaAttr': True}))
cmds.setAttr(evalStackNode + '.displayGeometries', 1);

cmds.connectAttr(mushNode + '.stack', evalStackNode + '.stack')

cmds.fabricSplice('addKLOperator', evalStackNode, '{"opName":"tubeCharacter_Eval"}', """

require RiggingToolbox;

operator tubeCharacter_Eval(
  io GeometryStack stack,
  Boolean displayGeometries,
  EvalContext context,
  Scalar eval
) {
  stack.setDisplayGeometries(displayGeometries);

  //StartFabricProfiling();

  stack.evaluate(context);

  // Uncomment these lines to get a profiling report. 
  //StopFabricProfiling();
  //report( GetEvalPathReport() );
  //report(stack.getDesc());
}
""")


##############################################
## Set up the eval locator.

forceEvalLocator = cmds.createNode("locator", name = "forceEval")
cmds.connectAttr(evalStackNode + '.eval', forceEvalLocator + '.localPosition.localPositionY')
