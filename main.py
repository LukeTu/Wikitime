# Function definitions remain the same...

# Prompt the user to search for an article
search_name = input('Please type the key words for the article name in English: ')
name_list = wikipedia.search(search_name)

# Display the list of found articles
for i, name in enumerate(name_list, start=1):
    print(f"{i}. {name}")

# Ask the user to select an article from the list
selected_number = int(input('Please type a number to select from the listed articles: '))
title_name = name_list[selected_number - 1]

# Ask the user to specify languages for translation
languages = []
while True:
    user_input = input("Please type the langcode, or leave it empty to break: ")
    
    if user_input == "":
        break
    elif user_input == "unlangs":
        languages = ['en', 'fr', 'ru', 'zh', 'ar', 'es']
        break
    else:
        languages.append(user_input)

print("Languages: ", languages)


# Initialize lists to hold data for each language
translated_article_names = []
creation_dates = []
modification_dates = []
revision_frequencies = []

# Process each language
# Make a copy of the languages list to iterate over
languages_copy = languages[:]
for lang in languages_copy:
    try:
        # Fetch the translated article name in the specified language
        translated_name = get_translated_article_name(title_name, lang)
        translated_article_names.append(translated_name)

        # Fetch the creation date of the article in the specified language
        creation_date = get_creation_date(translated_name, lang)
        creation_dates.append(creation_date)

        # Fetch the last modification date of the article in the specified language
        modification_date = get_modification_date(translated_name, lang)
        modification_dates.append(modification_date)

        # Calculate the revision frequency of the article in the specified language
        revision_frequency = calculate_revision_frequency(translated_name, lang)
        revision_frequencies.append(revision_frequency)
    except Exception as e:
        print(f"Skipping language {lang} due to error: {e}")
        languages.remove(lang)

# Normalize the revision frequencies to calculate completeness percentages
normalization_factor = 100 / max(revision_frequencies)
completeness_percentages = [freq * normalization_factor for freq in revision_frequencies]

# Prepare data for the Gantt chart
gantt_data = [
    {
        "Task": f"{name} {lang.upper()}",
        "Start": start_date,
        "Finish": end_date,
        "Complete": round(completion)
    }
    for name, lang, start_date, end_date, completion
    in zip(translated_article_names, languages, creation_dates, modification_dates, completeness_percentages)
]

# Notify the user that processing is finished
input("Processing finished. Press enter to generate the Gantt chart.")

# Generate the Gantt chart
fig = ff.create_gantt(gantt_data, colors= ['rgb(255,255,255)', 'rgb(0,0,0)'], index_col='Complete', title= f'WikiTime for {title_name.title()}', show_colorbar=False)
fig.update(layout_xaxis_rangeselector_visible=False)


