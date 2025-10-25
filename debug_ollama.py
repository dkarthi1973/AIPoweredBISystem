import ollama
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_ollama():
    try:
        client = ollama.Client()
        
        # Test direct list call
        logger.info("🔍 Testing Ollama client.list()...")
        models_response = client.list()
        
        logger.info(f"📋 Response type: {type(models_response)}")
        logger.info(f"📋 Full response: {models_response}")
        
        # Try different ways to access models
        if hasattr(models_response, '__dict__'):
            logger.info(f"📋 Response attributes: {models_response.__dict__}")
        
        # Check if it's a dict
        if isinstance(models_response, dict):
            logger.info("📋 Response is a dictionary")
            for key, value in models_response.items():
                logger.info(f"  Key: {key}, Type: {type(value)}")
                if key == 'models':
                    if isinstance(value, list):
                        logger.info(f"  Models list length: {len(value)}")
                        for i, model in enumerate(value):
                            logger.info(f"    Model {i}: {model}")
                            if isinstance(model, dict):
                                for model_key, model_value in model.items():
                                    logger.info(f"      {model_key}: {model_value}")
        
        # Check if it's a list
        elif isinstance(models_response, list):
            logger.info("📋 Response is a list")
            for i, item in enumerate(models_response):
                logger.info(f"  Item {i}: {item}")
                if isinstance(item, dict):
                    for key, value in item.items():
                        logger.info(f"    {key}: {value}")
        
        # Test generation with known model
        logger.info("🧪 Testing generation with llama3.1:latest...")
        try:
            test_response = client.generate(
                model="llama3.1:latest",
                prompt="Test",
                stream=False
            )
            logger.info(f"✅ Generation test successful: {test_response}")
        except Exception as e:
            logger.error(f"❌ Generation test failed: {e}")
            
    except Exception as e:
        logger.error(f"💥 Debug failed: {e}")

if __name__ == "__main__":
    debug_ollama()
