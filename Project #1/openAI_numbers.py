from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)
response = client.images.generate(
    prompt="A cute baby sea otter eating a pizza",
    n=2,
    size="1024x1024"
)

print(response.data[0].url)

print(completion.choices[0].message)