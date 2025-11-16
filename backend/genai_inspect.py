import google.generativeai as genai
import traceback
print("HAS list_models:", hasattr(genai, "list_models"))
try:
    print("CALLING list_models() ...")
    models = genai.list_models()
    print("list_models() returned:", models)
except Exception as e:
    print("list_models() raised an exception:")
    traceback.print_exc()
print("SAMPLE dir(genai) (filtered):")
print([n for n in dir(genai) if "model" in n.lower() or "list" in n.lower() or "generat" in n.lower()][:200])
