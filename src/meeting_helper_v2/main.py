#!/usr/bin/env python
import sys
import warnings
from datetime import datetime

from meeting_tool.crew import MeetingTool

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    user_transcript = input("Enter the meeting transcript: ")
    inputs = {
        'transcript': user_transcript,
    }

    try:
        result = MeetingTool().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    output = run()
    print(output)