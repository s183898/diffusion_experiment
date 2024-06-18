import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns

def combine_samples():
    path = "experiment/sample"

    df = pd.DataFrame()
    for user_id in os.listdir(path):
        if not os.path.isdir(os.path.join(path, user_id)):
            continue
        progress_file = os.path.join(path, user_id, "image_labels.csv")
        new_df = pd.read_csv(progress_file)

        new_df["user_id"] = user_id

        df = pd.concat([df, new_df], ignore_index=True)

    df.to_csv("experiment/sample_total.csv", index=False)


def extract_prompt_name(image_name):
    if 'None_Normal' in image_name:
        return image_name.split('_None_Normal')[0].replace('a_photo_of_the_face_of_', '')
    elif 'afro-american_caucasian_female_male_both' in image_name:
        return image_name.split('afro-american_caucasian_female_male_both')[0].replace('a_photo_of_the_face_of_', '')
    return None

def fix_csv():
    
    df = pd.read_csv("experiment/sample_total.csv")

    quality_categories = ["bad", "poor", "fair", "good", "excellent"]
    df['quality_int'] = df['quality'].apply(lambda x: quality_categories.index(x))
    
    # Apply the function to create a new column for the prompt name
    df['prompt_name'] = df['image'].apply(extract_prompt_name)

    df['group'] = df['image'].apply(lambda x: 'normal' if 'None_Normal' in x else
                                'debias' if 'afro-american_caucasian_female_male_both' in x else None)

    df.to_csv("experiment/sample_total.csv", index=False)
    

def analyze_diff():
    df = pd.read_csv("experiment/sample_total.csv")
        
    df_norm = df[df['image'].str.contains("None_Normal")]
    df_debias = df[df['image'].str.contains("caucasian")]

    mean_norm = df_norm['quality_int'].mean()
    mean_debias = df_debias['quality_int'].mean()

    # gender:
    mean_norm_gender = df_norm['gender'].mean()
    mean_debias_gender = df_debias['gender'].mean()

    print("Normal quality: ", mean_norm)
    print("Debias quality: ", mean_debias)

    print("Normal gender: ", mean_norm_gender)
    print("Debias gender: ", mean_debias_gender)
    print("Independence: ", (1+2+3+4+5)/5)


def test():

    df = pd.read_csv("experiment/sample_total.csv")

    grouped = df.groupby(['prompt_name', 'group']).agg({
        'quality_int': 'mean',
        'gender': 'mean',
        'ethnicity': lambda x: x.value_counts().index[0]  # Most frequent ethnicity
    }).reset_index()


    if not os.path.exists("quality.png"):

        # Pivot data for comparison
        pivot_quality = grouped.pivot(index='prompt_name', columns='group', values='quality_int')

        # Plotting
        pivot_quality.plot(kind='bar', figsize=(10, 5))
        plt.title('Comparison of Mean Quality by Group')
        plt.xlabel('Prompt Name')
        plt.ylabel('Mean Quality')
        plt.xticks(rotation=20)
        plt.legend(title='Group')
        plt.tight_layout()
        plt.savefig("quality.png")

    if not os.path.exists("gender.png"):
        pivot_gender = grouped.pivot(index='prompt_name', columns='group', values='gender')
        # Plotting
        pivot_gender.plot(kind='bar', color=['blue', 'green'], figsize=(10, 5))
        plt.title('Comparison of Mean Gender by Group')
        plt.xlabel('Prompt Name')
        plt.ylabel('Mean Gender')
        plt.xticks(rotation=20)
        plt.legend(title='Group')
        plt.savefig("gender.png")


    pivot_ethnicity = grouped.pivot(index='prompt_name', columns='group', values='ethnicity')

    plt.figure(figsize=(10, 5))
    ax = sns.barplot(x='prompt_name', y='ethnicity', hue='group', data=grouped, dodge=True)
    plt.title('Most Frequent Ethnicity by Group')
    plt.xlabel('Prompt Name')
    plt.ylabel('Ethnicity')
    plt.xticks(rotation=20)
    ax.legend(title='Group')
    plt.savefig("ethnicity.png")

if __name__ == "__main__": 

    df = pd.read_csv("experiment/sample_total.csv")

    df['gender'] = pd.to_numeric(df['gender'], errors='coerce')

    prompts = df['prompt_name'].unique()

    # Plotting
    for prompt in prompts:
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))  # 2 rows, 2 columns
        fig.suptitle(f'Distributions for Prompt: {prompt}')

        for i, group in enumerate(['Normal', 'Debias']):
            # Filter data for the current prompt and group
            subset = df[(df['prompt_name'] == prompt) & (df['group'] == group)].dropna()
            
            # Gender distribution
            axs[0, i].hist(subset['gender'].dropna(), bins=range(int(subset['gender'].min()), int(subset['gender'].max()) + 2))
            axs[0, i].set_title(f'Gender Distribution ({group})')
            axs[0, i].set_xlabel('Gender')
            axs[0, i].set_ylabel('Frequency')
            
            # Quality distribution
            axs[1, i].hist(subset['quality_int'].dropna(), bins=range(int(subset['quality_int'].min()), int(subset['quality_int'].max()) + 2))
            axs[1, i].set_title(f'Quality Distribution ({group})')
            axs[1, i].set_xlabel('Quality')
            axs[1, i].set_ylabel('Frequency')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout
        plt.savefig(f"{prompt}_plot.png")