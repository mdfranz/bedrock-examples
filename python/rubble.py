#!/usr/bin/env python3

#
# See https://sbstjn.com/blog/ai-generative-ai-aws-bedrock-cli-text-generation/
#

import boto3,json,logging,sys

## Globals for Logging BAD

logging.basicConfig(filename="rubble.log",level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def normalize_response(r):
  """Handle the output of different LLMs very stupidly"""
  logger.debug("RUBBLE: Entering normalize_response")
  
  # Pull out the stats from the response header
  metadata = r['ResponseMetadata']['HTTPHeaders']
  latency = metadata['x-amzn-bedrock-invocation-latency']
  tokens_out = metadata['x-amzn-bedrock-output-token-count']
  tokens_in = metadata['x-amzn-bedrock-input-token-count']
  logger.info(f"RUBBLE: Response stats latency={latency} input token count={tokens_in}  output token count={tokens_out}")

  # Process body 
  jr = json.loads(r.get('body').read())
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
  if model_result is None:
    return "Unknown results or Error!"
   
class Rubble(object):
  """Simple wrapper for invoking Bedrock"""

  def __init__(self,modelId="amazon.titan-text-lite-v1",temperature=0.5):
    self.client = boto3.client('bedrock-runtime') 
    self.temperature = temperature
    self.modelId = modelId
    logger.info("RUBBLE: Creating Rubble for model: %s",modelId)

  def set_prompt(self,p):
    self.prompt = p

  def create_body(self):
    """Form request to LLM for supported models"""
    logger.debug("RUBBLE: Creating body for %s ",self.modelId)
    if self.modelId.find("titan") > -1:
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
    """Call the model and normalize response"""
    print("\n\nInvoking model %s" % self.modelId)
    result = self.client.invoke_model( contentType="application/json", accept="*/*", modelId=self.modelId, body=json.dumps(self.create_body()))
    return normalize_response(result)

if __name__ == "__main__":
  logger.debug("RUBBLE: Starting __main__")

  if len(sys.argv) > 1:
    models = [sys.argv[1]]
  else:
    models = ["mistral.mixtral-8x7b-instruct-v0:1","mistral.mistral-7b-instruct-v0:2","amazon.titan-text-lite-v1","amazon.titan-tg1-large","amazon.titan-text-express-v1"]

  prompt = sys.stdin.read()

  for m in models:
    b = Rubble(modelId=m)
    b.set_prompt(prompt)
    print(b.invoke())
