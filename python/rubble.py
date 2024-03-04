#!/usr/bin/env python3

import boto3,sys,json

class Rubble(object):
  """Simple wrapper for invoking Bedrock"""

  def __init__(self,modelId="amazon.titan-text-lite-v1",temperature=0.5):
    self.client = boto3.client('bedrock-runtime') 
    self.temperature = temperature
    self.modelId = modelId

  def set_prompt(self,p):
    self.prompt = p

  def create_body(self):
    body  = {
      "inputText": f"{self.prompt}",
      "textGenerationConfig": {
        "temperature": self.temperature,
        "topP": 0.9, 
        "maxTokenCount": 512, 
        "stopSequences": []
      }
    }
    return body

  def invoke(self):
    result = self.client.invoke_model( contentType="application/json", accept="*/*", modelId=self.modelId, body=json.dumps(self.create_body()))
    print(result)
  
if __name__ == "__main__":
  print("Main")
  b = Rubble()
  b.set_prompt("Are you thered,Fred?")
  b.invoke()
