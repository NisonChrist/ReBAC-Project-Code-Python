"""
Main entry point for policy generation system
"""

from policy_gen.llm import LLM, Prompt


def main():
    """Main function to run policy generation"""
    prompt_list = [
        Prompt(
            system="You are a helpful assistant. Help me solve the following problem. The answer should be in JSON format.",
            user="1+1=?",
            template="sample",
        )
    ]
    deepseek = LLM(prompt_list=prompt_list)
    output = deepseek.generate()
    print(output)


if __name__ == "__main__":
    main()
