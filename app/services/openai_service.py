import os
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def summarize_transcript(transcript: str, max_takeaways: int = 5) -> List[Dict[str, str]]:
    """
    Summarize transcript using OpenAI GPT-4.

    Args:
        transcript: Transcript text to summarize
        max_takeaways: Maximum number of key takeaways to generate

    Returns:
        List of key takeaways, each with a title and description

    Raises:
        Exception: If summarization fails
    """
    try:
        # Prepare prompt for GPT-4
        prompt = f"""
        Please summarize the following transcript from a YouTube video. 
        Extract the {max_takeaways} most important key takeaways or main points.

        For each key takeaway:
        1. Provide a short, descriptive title (10 words or less)
        2. Write a brief description explaining the point (50 words or less)

        Format the output as JSON with a structure like this:
        [
            {{
                "title": "First key point title",
                "description": "Explanation of first key point"
            }},
            ...
        ]

        Only include the JSON in your response, no additional text.

        Transcript:
        {transcript}
        """

        # Call GPT-4 API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that summarizes YouTube video transcripts into key takeaways."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Extract JSON response
        content = response.choices[0].message.content

        # Parse response - ensure it's valid JSON
        import json
        try:
            # Try to parse the entire response as JSON
            takeaways = json.loads(content)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the text
            import re
            json_match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
            if json_match:
                takeaways = json.loads(json_match.group(0))
            else:
                raise Exception("Could not parse GPT-4 response as JSON")

        # Validate structure
        valid_takeaways = []
        for takeaway in takeaways:
            if isinstance(takeaway, dict) and "title" in takeaway and "description" in takeaway:
                valid_takeaways.append({
                    "title": takeaway["title"],
                    "description": takeaway["description"]
                })

        # Limit to max_takeaways
        return valid_takeaways[:max_takeaways]

    except Exception as e:
        raise Exception(f"GPT-4 summarization failed: {str(e)}")