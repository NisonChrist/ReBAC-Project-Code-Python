from prompt import Prompt

prompt = Prompt(
    system="You are a helpful assistant. Answer the following question.",
    user="1+1=?",
    template="${question}",
)

print(prompt)
