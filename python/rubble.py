#!/usr/bin/env python3

#
# See https://sbstjn.com/blog/ai-generative-ai-aws-bedrock-cli-text-generation/
#

import boto3,sys,json,logging

## Globals for Logging BAD

logging.basicConfig(filename="rubble.log",level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def normalize_response(r):
  """Handle the output of different LLMs very stupidly"""
  jr = json.loads(r.get('body').read())

  logger.info("RUBBLE: Entering normalize_response")
  logger.debug(r.keys())
  model_result = None


  # assume we have unique fields so as soon as there
  for result_field in ['outputs','results']:
    logger.debug("RUBBLE result_field: %s",result_field)
    
    if result_field in jr:
      model_result = jr[result_field]

      if result_field == "outputs":
        return model_result[0]['text']
      elif result_field == "results":
        return model_result[0]['outputText']

  # Fallback 
  if model_result == None:
    return "Unknown results or Error!"
   
class Rubble(object):
  """Simple wrapper for invoking Bedrock"""

  def __init__(self,modelId="amazon.titan-text-lite-v1",temperature=0.5):
    self.client = boto3.client('bedrock-runtime') 
    self.temperature = temperature
    self.modelId = modelId
    logger.debug("RUBBLE: Creating Rubble for: %s",modelId)

  def set_prompt(self,p):
    self.prompt = p

  def create_body(self):
    if self.modelId.find("titan") > -1:
      logger.info("RUBBLE: Creating body for %s ",self.modelId)
      body  = {
        "inputText": f"{self.prompt}",
        "textGenerationConfig": {
          "temperature": self.temperature,
          "topP": 0.9, 
          "maxTokenCount": 512, 
          "stopSequences": []
        }
      }
    else:
      body  = {
        "prompt": f"{self.prompt}",
        "temperature": self.temperature
      }

    return body

  def invoke(self):
    print("\n\nInvoking model %s" % self.modelId)
    result = self.client.invoke_model( contentType="application/json", accept="*/*", modelId=self.modelId, body=json.dumps(self.create_body()))
    return normalize_response(result)

if __name__ == "__main__":
  logger.info("RUBBLE: Starting __main__")
  b = Rubble(modelId="mistral.mistral-7b-instruct-v0:2")
  b.set_prompt("Are you there, Fred? Is your name, Fred. I am Barney")
  print(b.invoke())

  b = Rubble(modelId="amazon.titan-text-lite-v1")
  b.set_prompt("Are you there, Fred? Is your name, Fred. I am Barney")
  print(b.invoke())
