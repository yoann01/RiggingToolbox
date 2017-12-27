
import json
from maya import cmds

cmds.file(new=True,f=True)


##############################################
## Set up the BezierXfo test node.

knot1Locator = cmds.createNode("locator", name = "knot1")
cmds.move(-2,0,2)
knot2Locator = cmds.createNode("locator", name = "knot2")
cmds.move(3,0,-4)

knot3Locator = cmds.createNode("locator", name = "knot2")
cmds.move(6,0,0)


node = cmds.createNode("spliceMayaNode", name = "BezierXfo")

cmds.fabricSplice('addOutputPort', node, json.dumps({'portName':'bezierXfo', 'dataType':'BezierXfo', 'extension':'RiggingToolbox', 'addSpliceMayaAttr':True }))
cmds.fabricSplice('addOutputPort', node, json.dumps({'portName':'handle', 'dataType':'DrawingHandle', 'extension':'InlineDrawing', 'addSpliceMayaAttr':True }))

cmds.fabricSplice('addInputPort', node, json.dumps({'portName':'mode', 'dataType':'Integer', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', node, json.dumps({'portName':'count', 'dataType':'Integer', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', node, json.dumps({'portName':'samples', 'dataType':'Integer', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', node, json.dumps({'portName':'start', 'dataType':'Scalar', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', node, json.dumps({'portName':'end', 'dataType':'Scalar', 'addMayaAttr': True}))
cmds.fabricSplice('addInputPort', node, json.dumps({'portName':'tangentLength', 'dataType':'Scalar', 'addMayaAttr': True}))

cmds.fabricSplice('addInputPort', node, json.dumps({'portName':'knots', 'dataType':'Mat44[]', 'addMayaAttr': True, 'arrayType':"Array (Multi)"}))

cmds.connectAttr(knot1Locator+'.worldMatrix', node + '.knots[0]')
cmds.connectAttr(knot2Locator+'.worldMatrix', node + '.knots[1]')
cmds.connectAttr(knot3Locator+'.worldMatrix', node + '.knots[2]')

cmds.fabricSplice('addKLOperator', node, '{"opName":"bezierXfoTest"}', """

require RiggingToolbox;

operator bezierXfoTest(
  io BezierXfo bezierXfo,
  Integer mode,
  Integer count,
  Integer samples,
  Scalar start,
  Scalar end,
  Scalar tangentLength,
  Mat44 knots[],
  DrawingHandle handle
) {
  bezierXfo.tangentLength = tangentLength;

  for(Integer i=0; i<knots.size; i++)
    bezierXfo.setKnot(i, Xfo(knots[i]));

  report("bezierXfo Length:" + bezierXfo.length(samples));

  Xfo xfos[];
  switch(mode){
    case 0:
      xfos = bezierXfo.projectArray(count, start, end);
      break;
    case 1:
      xfos = bezierXfo.projectRegularly(count, samples);
      break;
  }
  drawXfoArray(handle.getRootTransform(), "bezierXfoTest", xfos, Color(1.0,0.0,0.0));
}
""")

cmds.setAttr(node + '.count', 30);
cmds.setAttr(node + '.samples', 100);
cmds.setAttr(node + '.end', 1.0);
cmds.setAttr(node + '.tangentLength', 2.0);

cmds.fabricSplice('addOutputPort', node, json.dumps({'portName':'eval', 'dataType':'Scalar', 'addMayaAttr': True}))
forceEvalLocator = cmds.createNode("locator", name = "forceEval")
cmds.connectAttr(node + '.eval', forceEvalLocator + '.localPosition.localPositionY')
