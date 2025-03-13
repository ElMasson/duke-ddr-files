from crewai import Crew, Process
import streamlit as st
import asyncio
import time
from data_catalog.agents import (
    create_data_analyzer_agent,
    create_schema_extractor_agent,
    create_metadata_curator_agent,
    create_data_quality_agent,
    create_business_glossary_agent,
    create_documentation_agent,
)
from data_catalog.tasks import (
    create_file_analysis_task,
    create_schema_extraction_task,
    create_metadata_curation_task,
    create_data_quality_assessment_task,
    create_business_glossary_task,
    create_documentation_task,
    get_user_validation,
)
from chat_interface.utils import update_chat_with_catalog_progress

# Global variable to track current workflow state
current_workflow_state = {
    "current_file": None,
    "current_stage": 0,
    "results": {},
    "corrections": {}
}


def start_catalog_workflow(files):
    """
    Start the data catalog workflow with the given files.

    Args:
        files: List of uploaded files
    """
    # Update the chat with progress messages
    update_chat_with_catalog_progress(
        "Début de l'analyse",
        f"Je commence l'analyse de {len(files)} fichiers pour créer un catalogue de données."
    )

    # Process the first file
    if files:
        start_file_workflow(files[0])


def start_file_workflow(file):
    """
    Start the workflow for a single file.

    Args:
        file: The file to process
    """
    global current_workflow_state

    # Reset workflow state for new file
    current_workflow_state = {
        "current_file": file,
        "current_stage": 1,  # Start with stage 1
        "results": {},
        "corrections": {}
    }

    # Start with file analysis
    perform_file_analysis(file)


def continue_catalog_workflow(user_feedback=None):
    """
    Continue the catalog workflow after user validation or corrections.

    Args:
        user_feedback: Optional feedback provided by the user
    """
    global current_workflow_state

    # Import here to avoid circular imports
    from data_catalog.llm_processor import process_user_feedback

    # Process user feedback if provided
    if user_feedback and len(user_feedback) > 5 and not any(
            word in user_feedback.lower() for word in ["oui", "valide", "d'accord", "ok"]):
        # Get the current stage content to update
        current_stage = current_workflow_state["current_stage"]
        stage_key = None

        if current_stage == 1:
            stage_key = "analysis"
        elif current_stage == 2:
            stage_key = "schema"
        elif current_stage == 3:
            stage_key = "metadata"
        elif current_stage == 4:
            stage_key = "quality"
        elif current_stage == 5:
            stage_key = "glossary"
        elif current_stage == 6:
            stage_key = "documentation"

        if stage_key and stage_key in current_workflow_state["results"]:
            # Get the current content
            current_content = current_workflow_state["results"][stage_key]

            # Process feedback and get updated content
            stage_names = ["Analyse du fichier", "Extraction du schéma", "Création des métadonnées",
                           "Évaluation de la qualité", "Création du glossaire", "Documentation complète"]
            stage_name = stage_names[current_stage - 1] if 1 <= current_stage <= len(stage_names) else "cette étape"

            updated_content = process_user_feedback(current_content, user_feedback, stage_name)

            # Update the content in workflow state
            current_workflow_state["results"][stage_key] = updated_content

            # Store the feedback
            current_workflow_state["corrections"][f"stage_{current_stage}"] = user_feedback

    # Move to the next stage
    current_workflow_state["current_stage"] += 1
    current_stage = current_workflow_state["current_stage"]
    file = current_workflow_state["current_file"]

    # Save current state in session state for persistence across reruns
    if "current_workflow_state" not in st.session_state:
        st.session_state.current_workflow_state = {}
    st.session_state.current_workflow_state = current_workflow_state.copy()

    # Schedule the next step for after the current execution completes
    if "next_workflow_action" not in st.session_state:
        st.session_state.next_workflow_action = {
            "stage": current_stage,
            "file": file
        }

    # Force a rerun to start the next stage
    st.rerun()


def perform_file_analysis(file):
    """
    Perform file analysis as the first step of the workflow.

    Args:
        file: The file to analyze
    """
    update_chat_with_catalog_progress("Étape 1/6", "Analyse de la structure et du contenu du fichier...")

    # In a real implementation, this would use the data_analyzer agent
    # For the prototype, we'll simulate processing time
    time.sleep(2)

    # Generate a simulated analysis result
    analysis_result = f"""
    # Analyse du fichier: {file.name}

    Ce fichier semble être un ensemble de données tabulaires contenant des informations de vente d'une entreprise.

    ## Structure détectée:
    - Format: {file.type}
    - Taille: {file.size} bytes
    - Type de données: Données de vente/transactions

    ## Contenu détecté:
    - Informations sur les produits
    - Données de commandes et ventes
    - Informations géographiques (régions, pays)
    - Dates de commandes
    - Métriques financières (ventes, profit)

    Ce fichier paraît être un exemple classique de données de supermarché/magasin utilisé pour l'analyse des ventes et de la performance commerciale.
    """

    # Store the result
    current_workflow_state["results"]["analysis"] = analysis_result

    # Get user validation
    get_user_validation("Analyse du fichier", analysis_result)


def perform_schema_extraction(file):
    """
    Perform schema extraction as the second step of the workflow.

    Args:
        file: The file to process
    """
    update_chat_with_catalog_progress("Étape 2/6", "Extraction du schéma de données...")

    # Simulate processing time
    time.sleep(2)

    # Generate a simulated schema result
    schema_result = f"""
    # Schéma proposé pour: {file.name}

    ## Structure des colonnes:

    1. **OrderID** (entier)
       - Identifiant unique de commande
       - Clé primaire

    2. **OrderDate** (date)
       - Date à laquelle la commande a été passée

    3. **CustomerName** (texte)
       - Nom du client ayant passé la commande

    4. **Segment** (texte)
       - Segment de clientèle (Consumer, Corporate, Home Office)

    5. **Country/Region** (texte)
       - Localisation géographique 

    6. **City** (texte)
       - Ville de livraison

    7. **ProductID** (entier)
       - Identifiant unique du produit

    8. **Category** (texte)
       - Catégorie du produit

    9. **SubCategory** (texte)
       - Sous-catégorie du produit

    10. **ProductName** (texte)
        - Nom du produit

    11. **Sales** (décimal)
        - Montant des ventes

    12. **Quantity** (entier)
        - Quantité commandée

    13. **Discount** (décimal)
        - Pourcentage de remise

    14. **Profit** (décimal)
        - Profit réalisé sur la vente
    """

    # Store the result
    current_workflow_state["results"]["schema"] = schema_result

    # Get user validation
    get_user_validation("Extraction du schéma", schema_result)


def perform_metadata_curation(file):
    """
    Perform metadata curation as the third step of the workflow.

    Args:
        file: The file to process
    """
    update_chat_with_catalog_progress("Étape 3/6", "Création des métadonnées...")

    # Simulate processing time
    time.sleep(2)

    # Generate a simulated metadata result
    metadata_result = f"""
    # Métadonnées pour: {file.name}

    ## Informations générales:
    - **Titre**: Données de ventes Superstore
    - **Description**: Ensemble de données contenant les informations de ventes, profits, et caractéristiques des commandes pour une entreprise de commerce de détail.
    - **Propriétaire des données**: Département des ventes
    - **Date de création**: Non spécifiée dans le fichier
    - **Dernière mise à jour**: Non spécifiée dans le fichier
    - **Fréquence de mise à jour estimée**: Mensuelle

    ## Classification:
    - **Domaine**: Ventes et Marketing
    - **Confidentialité**: Interne (données commerciales sans informations personnelles sensibles)
    - **Importance**: Élevée (données critiques pour le suivi commercial)

    ## Tags:
    - ventes
    - profit
    - produits
    - clients
    - régions
    - superstore
    - commercial
    - commandes
    """

    # Store the result
    current_workflow_state["results"]["metadata"] = metadata_result

    # Get user validation
    get_user_validation("Création des métadonnées", metadata_result)


def perform_quality_assessment(file):
    """
    Perform data quality assessment as the fourth step of the workflow.

    Args:
        file: The file to process
    """
    update_chat_with_catalog_progress("Étape 4/6", "Évaluation de la qualité des données...")

    # Simulate processing time
    time.sleep(2)

    # Generate a simulated quality assessment result
    quality_result = f"""
    # Évaluation de la qualité des données pour: {file.name}

    ## Métriques de qualité:

    ### Complétude:
    - **Score**: 96%
    - **Détails**: La plupart des colonnes sont bien remplies. Quelques valeurs manquantes détectées dans 'Postal Code' et 'Region'.

    ### Exactitude:
    - **Score**: 94% 
    - **Détails**: Les valeurs semblent généralement précises et cohérentes avec les domaines attendus.

    ### Cohérence:
    - **Score**: 97%
    - **Détails**: Les relations entre catégories et sous-catégories sont cohérentes. Les dates de commande et d'expédition sont logiquement organisées.

    ### Unicité:
    - **Score**: 100%
    - **Détails**: Pas de doublons de commandes détectés.

    ## Problèmes identifiés:
    1. Quelques codes postaux manquants
    2. Quelques incohérences mineures dans les noms de villes (variations orthographiques)
    3. Valeurs aberrantes potentielles dans les montants de profit (certaines valeurs très négatives)

    ## Améliorations suggérées:
    1. Standardiser les formats des noms de villes
    2. Completer les codes postaux manquants
    3. Vérifier les commandes avec des profits très négatifs
    4. Ajouter des validations pour les valeurs numériques (quantités, remises)
    """

    # Store the result
    current_workflow_state["results"]["quality"] = quality_result

    # Get user validation
    get_user_validation("Évaluation de la qualité", quality_result)


def perform_business_glossary(file):
    """
    Create a business glossary as the fifth step of the workflow.

    Args:
        file: The file to process
    """
    update_chat_with_catalog_progress("Étape 5/6", "Création du glossaire métier...")

    # Simulate processing time
    time.sleep(2)

    # Generate a simulated business glossary
    glossary_result = f"""
    # Glossaire métier pour: {file.name}

    ## Termes commerciaux clés:

    ### Ventes (Sales)
    Montant total facturé au client pour les produits achetés, avant application des remises.

    ### Profit
    Bénéfice net réalisé après déduction de tous les coûts associés à la vente.

    ### Segment
    Classification des clients en différentes catégories selon leur type d'activité ou d'organisation.
    - Consumer: Clients particuliers achetant pour leur usage personnel
    - Corporate: Clients entreprises achetant pour usage professionnel
    - Home Office: Clients travailleurs indépendants ou petites entreprises à domicile

    ### Catégorie (Category)
    Classification principale des produits vendus par l'entreprise.

    ### Sous-catégorie (Sub-Category)
    Division plus détaillée au sein d'une catégorie de produits.

    ### Remise (Discount)
    Réduction de prix accordée sur le prix de vente standard, exprimée en pourcentage.

    ### Région (Region)
    Zone géographique principale regroupant plusieurs états ou provinces.

    ### Quantité (Quantity)
    Nombre d'unités d'un produit particulier commandées par le client.
    """

    # Store the result
    current_workflow_state["results"]["glossary"] = glossary_result

    # Get user validation
    get_user_validation("Création du glossaire", glossary_result)


def perform_documentation(file):
    """
    Generate comprehensive documentation as the final step of the workflow.

    Args:
        file: The file to process
    """
    update_chat_with_catalog_progress("Étape 6/6", "Génération de la documentation complète...")

    # Simulate processing time
    time.sleep(2)

    # Combine all previous results
    analysis = current_workflow_state["results"]["analysis"]
    schema = current_workflow_state["results"]["schema"]
    metadata = current_workflow_state["results"]["metadata"]
    quality = current_workflow_state["results"]["quality"]
    glossary = current_workflow_state["results"]["glossary"]

    # Generate a comprehensive documentation
    documentation_result = f"""
    # Documentation complète: {file.name}

    ## Résumé
    Ce document présente le catalogue de données complet pour le fichier "{file.name}", qui contient des données de ventes d'une entreprise de type superstore. Ce catalogue comprend l'analyse du fichier, le schéma des données, les métadonnées, une évaluation de la qualité des données et un glossaire métier.

    ## Table des matières
    1. [Analyse du fichier](#analyse-du-fichier)
    2. [Schéma des données](#schéma-des-données)
    3. [Métadonnées](#métadonnées)
    4. [Évaluation de la qualité](#évaluation-de-la-qualité)
    5. [Glossaire métier](#glossaire-métier)
    6. [Exemples d'utilisation](#exemples-dutilisation)

    ## Analyse du fichier
    {analysis}

    ## Schéma des données
    {schema}

    ## Métadonnées
    {metadata}

    ## Évaluation de la qualité
    {quality}

    ## Glossaire métier
    {glossary}

    ## Exemples d'utilisation

    ### Analyse des ventes par région
    ```sql
    SELECT Region, SUM(Sales) as TotalSales, SUM(Profit) as TotalProfit
    FROM SuperstoreData
    GROUP BY Region
    ORDER BY TotalSales DESC
    ```

    ### Analyse des produits les plus rentables
    ```sql
    SELECT Category, SubCategory, ProductName, SUM(Sales) as TotalSales, SUM(Profit) as TotalProfit
    FROM SuperstoreData
    GROUP BY Category, SubCategory, ProductName
    ORDER BY TotalProfit DESC
    LIMIT 10
    ```

    ### Analyse des tendances mensuelles des ventes
    ```sql
    SELECT EXTRACT(YEAR FROM OrderDate) as Year, EXTRACT(MONTH FROM OrderDate) as Month, 
           SUM(Sales) as MonthlySales, SUM(Profit) as MonthlyProfit
    FROM SuperstoreData
    GROUP BY Year, Month
    ORDER BY Year, Month
    ```
    """

    # Store the result
    current_workflow_state["results"]["documentation"] = documentation_result

    # Get user validation
    get_user_validation("Documentation complète", documentation_result)


def complete_workflow(file):
    """
    Complete the workflow for a file.

    Args:
        file: The processed file
    """
    update_chat_with_catalog_progress(
        "Catalogue terminé",
        f"Le catalogue de données pour {file.name} est maintenant complet. "
        f"Vous pouvez continuer à poser des questions sur ces données ou télécharger d'autres fichiers."
    )

    # Reset workflow stage to allow new file processing
    st.session_state.workflow_stage = "files_uploaded"


def create_catalog_crew(file):
    """
    Create a CrewAI crew for data cataloging.

    Args:
        file: The file to catalog

    Returns:
        Crew: The catalog crew
    """
    # Create agents
    data_analyzer = create_data_analyzer_agent()
    schema_extractor = create_schema_extractor_agent()
    metadata_curator = create_metadata_curator_agent()
    data_quality_agent = create_data_quality_agent()
    business_glossary_agent = create_business_glossary_agent()
    documentation_agent = create_documentation_agent()

    # Create tasks (placeholder implementation)
    # In a real implementation, these would be created dynamically and executed sequentially
    # with user validation between each step

    # Create the crew
    crew = Crew(
        llm_manager='o3-mini',
        agents=[
            data_analyzer,
            schema_extractor,
            metadata_curator,
            data_quality_agent,
            business_glossary_agent,
            documentation_agent
        ],
        tasks=[],  # Will be added dynamically
        process=Process.hierarchical,
        verbose=True
    )

    return crew