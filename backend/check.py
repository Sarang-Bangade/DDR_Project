import google.generativeai as genai

genai.configure(api_key="AIzaSyDAH51XgxOZ4FkN7tp5KhRz90LA-WFWfjc")
for m in genai.list_models():
    print(m.name)