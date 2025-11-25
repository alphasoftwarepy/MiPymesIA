import sys
print(f"Python executable: {sys.executable}")
try:
    import langchain
    print(f"LangChain version: {langchain.__version__}")
    print(f"LangChain file: {langchain.__file__}")
    
    from langchain.chains import ConversationChain
    print("Import ConversationChain successful")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
