import os
from dotenv import load_dotenv
import streamlit as st
import openai

# Load environment variables
load_dotenv()


def initialize_llm():
    """
    Initialize the language model for processing user inputs.
    """
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return False

    # Set the API key for OpenAI
    openai.api_key = api_key
    return True


def process_user_feedback(current_content, user_feedback, stage):
    """
    Process user feedback using LLM to modify catalog content.

    Args:
        current_content: The current content being reviewed
        user_feedback: The user's feedback or correction
        stage: The current workflow stage

    Returns:
        str: The updated content based on user feedback
    """
    # If user feedback is minimal or affirmative, just return the current content
    affirmative_responses = ["oui", "valide", "d'accord", "ok", "rien", "parfait", "bien", "correct"]
    if any(response in user_feedback.lower() for response in affirmative_responses) and len(user_feedback) < 20:
        return current_content

    try:
        # Prepare the prompt for the LLM
        prompt = f"""
        Je suis en train de créer un catalogue de données et j'ai besoin d'intégrer les retours d'un utilisateur.

        Voici le contenu actuel pour l'étape "{stage}":

        {current_content}

        Voici le retour de l'utilisateur:
        "{user_feedback}"

        Veuillez modifier le contenu en fonction du retour de l'utilisateur. Si le retour concerne l'ajout d'informations, 
        intégrez-les de manière cohérente. Si le retour concerne des corrections, appliquez-les précisément.

        Retournez le contenu modifié complet, au même format que le contenu original.
        """

        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Vous êtes un assistant spécialisé dans la création de catalogues de données précis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2500
        )

        # Extract and return the modified content
        updated_content = response.choices[0].message.content.strip()
        return updated_content

    except Exception as e:
        st.error(f"Error processing feedback with LLM: {str(e)}")
        # Return original content if there's an error
        return current_content


def generate_response_to_user_feedback(user_feedback, stage):
    """
    Generate a response to the user's feedback using LLM.

    Args:
        user_feedback: The user's feedback
        stage: The current workflow stage

    Returns:
        str: A natural language response to the user
    """
    try:
        # Prepare the prompt for the LLM
        prompt = f"""
        Je suis un assistant de catalogage de données. Un utilisateur m'a donné ce retour concernant l'étape "{stage}":

        "{user_feedback}"

        Générez une réponse naturelle et sympathique à ce retour. Si le retour est positif ou affirmatif, 
        confirmez que nous passons à l'étape suivante. Si le retour contient des demandes de modification,
        confirmez que vous avez bien compris et allez intégrer ces modifications.

        Gardez la réponse courte et directe (maximum 2 phrases).
        """

        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Vous êtes un assistant sympathique et professionnel spécialisé dans le catalogage de données."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )

        # Extract and return the response
        return response.choices[0].message.content.strip()

    except Exception as e:
        # Fallback response if there's an error
        return "Merci pour votre retour. Je vais procéder aux ajustements nécessaires."