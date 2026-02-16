import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ReflectionAgent:
    def __init__(self, max_iterations=3, score_threshold=7):
        self.max_iterations = max_iterations
        self.score_threshold = score_threshold

    def generate_response(self, user_prompt):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

    def evaluate_response(self, user_prompt, ai_response):
        evaluation_prompt = f"""
        Evaluate the following AI response based on:
        1. Logical consistency
        2. Completeness
        3. Clarity
        4. Relevance to the question

        Provide:
        - A score from 1 to 10
        - Short reasoning
        - Suggested improvements

        Question:
        {user_prompt}

        AI Response:
        {ai_response}

        Respond in JSON format:
        {{
            "score": <number>,
            "reasoning": "...",
            "improvements": "..."
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0
        )

        return json.loads(response.choices[0].message.content)

    def refine_response(self, user_prompt, ai_response, improvements):
        refinement_prompt = f"""
        Improve the AI response below using the suggested improvements.

        Question:
        {user_prompt}

        Original Response:
        {ai_response}

        Improvements to Apply:
        {improvements}

        Provide a refined, improved answer.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": refinement_prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content

    def run(self, user_prompt):
        print("\n Generating initial response...\n")
        response = self.generate_response(user_prompt)

        for iteration in range(self.max_iterations):
            print(f"\n Evaluation Round {iteration + 1}")
            evaluation = self.evaluate_response(user_prompt, response)

            print("Score:", evaluation["score"])
            print("Reason:", evaluation["reasoning"])

            if evaluation["score"] >= self.score_threshold:
                print("\n Response meets quality threshold.")
                return response

            print("\n Refining response...\n")
            response = self.refine_response(
                user_prompt,
                response,
                evaluation["improvements"]
            )

        print("\n Max iterations reached. Returning best attempt.")
        return response


if __name__ == "__main__":
    agent = ReflectionAgent(max_iterations=3, score_threshold=8)

    user_input = input("Enter your question: ")
    final_answer = agent.run(user_input)

    print("\n===== FINAL ANSWER =====\n")
    print(final_answer)
