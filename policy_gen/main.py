from llm.llm import LLM

if __name__ == "__main__":
    deepseek = LLM("Deepseek-V3.2")
    deepseek.input({
        'prompt': 'Please help me the following question!',
        'user': '1+1='
        })
    result = deepseek.output()
    print(result)
